import os
import re
import logging
import csv
from urllib.parse import unquote

from itertools import product
from splunk_appinspect import App

from .fields import convert_to_fields, Field

LOGGER = logging.getLogger("pytest_splunk_addon")


class AddonParser(object):
    def __init__(self, splunk_app_path):
        self.splunk_app_path = splunk_app_path
        self.app = App(splunk_app_path, python_analyzer_enable=False)
        self.props = self.app.props_conf()
        self.transforms = self.app.transforms_conf()
        self.tags = self.app.get_config("tags.conf")
        self.eventtypes = self.app.eventtypes_conf()

    def get_props_stanzas(self):
        for stanza_name in self.props.sects:
            stanza = self.props.sects[stanza_name]
            if stanza.name.startswith("host::"):
                continue
            if stanza.name.startswith("source::"):
                for each_source in self.get_list_of_sources(stanza_name):
                    yield "source", each_source, stanza
            else:
                yield "sourcetype", stanza.name, stanza

    @staticmethod
    def get_list_of_sources(source):
        """
        Implement generator object of source list

        Args:
            source(str): Source name

        Yields:
            generator of source name
        """
        match_obj = re.search(r"source::(.*)", source)
        value = match_obj.group(1).replace("...", "*")
        sub_groups = re.findall(r"\([^\)]+\)", value)
        sub_group_list = []
        for each_group in sub_groups:
            sub_group_list.append(each_group.strip("()").split("|"))
        template = re.sub(r"\([^\)]+\)", "{}", value)
        for each_permutation in product(*sub_group_list):
            yield template.format(*each_permutation)


    def get_props_method(self, class_name):
        method_mapping = {
            "EXTRACT": self.get_extract_fields,
            "EVAL": self.get_eval_fields,
            "FIELDALIAS": self.get_fieldalias_fields,
            "sourcetype": self.get_sourcetype_assignments,
            "REPORT": self.get_report_fields,
            "LOOKUP": self.get_lookup_fields
        }
        for each_type in method_mapping:
            if re.match(each_type, class_name, re.IGNORECASE):
                return method_mapping[each_type]

    def get_tags(self):
        for stanza in self.tags.sects:
            tag_sections = self.tags.sects[stanza]
            stanza = stanza.replace("=", '="') + '"'
            stanza = unquote(stanza)

            for key in tag_sections.options:
                tags_property = tag_sections.options[key]
                tag_container = {
                    "stanza": stanza,
                    "tag": tags_property.name,
                    # "enabled": True
                }
                if tags_property.value == "enabled":
                    tag_container["enabled"] = True
                else:
                    tag_container["enabled"]= False
                yield tag_container

    def get_eventtypes(self):
        for eventtype_section in self.eventtypes.sects:
            yield {
                "stanza": eventtype_section
            }

    def get_props_fields(self):
        for stanza_type, stanza_name, stanza in self.get_props_stanzas():
            for classname in stanza.options:
                LOGGER.info(
                    "Parsing parameter=%s of stanza=%s",
                    classname,
                    stanza_name,
                )
                props_property = stanza.options[classname]
                parsing_method = self.get_props_method(classname)
                if parsing_method:
                    yield {
                        "stanza": stanza_name,
                        "stanza_type": stanza_type,
                        "classname": classname,
                        "fields": list(parsing_method(props_property))
                    }

    @convert_to_fields
    def get_extract_fields(self, props_property):
        """
        Returns the fields parsed from EXTRACT
        Args:
            props_property(
                splunk_appinspect.configuration_file.ConfigurationSetting
                ): The configuration setting object of EXTRACT.
                properties used:
                        name : key in the configuration settings
                        value : value of the respective name in the configuration
        Yields:
            generator of fields
        """
        regex = r"\(\?P?(?:[<'])([^\>'\s]+)[\>']"
        fields_group = []
        for field in re.findall(regex, props_property.value):
            fields_group.append(field)
            yield field

        # If SOURCE_KEY is used in EXTRACT, generate the test for the same.
        regex_for_source_key = r"(?:(?i)in\s+(\w+))\s*$"
        extract_source_key = re.search(
            regex_for_source_key, props_property.value, re.MULTILINE
        )
        if extract_source_key:
            yield extract_source_key.group(1)
            fields_group.insert(0, extract_source_key.group(1))

    def get_sourcetype_assignments(self, props_property):
        """
        Return the fields parsed from sourcetype

        Args:
            props_property(splunk_appinspect.configuration_file.ConfigurationSetting): 
                The configuration setting object of REPORT.
                properties used:
                        name : key in the configuration settings
                        value : value of the respective name in the configuration

        Returns: the sourcetype field with possible value
        """
        yield Field({
            "name": props_property.name,
            "expected_values": [props_property.value]
        })

    @convert_to_fields
    def get_eval_fields(self, props_property):
        regex = r"EVAL-(?P<FIELD>.*)"
        yield from re.findall(regex, props_property.name, re.IGNORECASE)


    @convert_to_fields
    def get_fieldalias_fields(self, props_property):
        regex = (
            r"(\"(?:\\\"|[^\"])*\"|\'(?:\\\'|[^\'])*\'|[^\s,]+)"
            r"\s+(?i)(?:as(?:new)?)\s+"
            r"(\"(?:\\\"|[^\"])*\"|\'(?:\\\'|[^\'])*\'|[^\s,]+)"
        )
        fields_tuples = re.findall(regex, props_property.value, re.IGNORECASE)
        # Convert list of tuples into list
        return list(set([item for t in fields_tuples for item in t]))

    @convert_to_fields
    def get_report_fields(self, props_property):
        """
        Returns the fields parsed from transforms.conf  as pytest parameters

        Args:
            props_property(splunk_appinspect.configuration_file.ConfigurationSetting): 
                The configuration setting object of REPORT.
                properties used:
                        name : key in the configuration settings
                        value : value of the respective name in the configuration
        Yields:
            generator of fields parsed from transforms.conf 
        """
        try:
            transforms_itr = (each_stanza.strip() for each_stanza in props_property.value.split(","))
            for transforms_section in transforms_itr:
                transforms_section = self.transforms.sects[transforms_section]
                if "SOURCE_KEY" in transforms_section.options:
                    yield transforms_section.options["SOURCE_KEY"].value

                if "REGEX" in transforms_section.options:
                    regex = r"\(\?P?(?:[<'])([^\>'\s]+)[\>']"
                    yield from re.findall(regex, transforms_section.options["REGEX"].value)

                if "FIELDS" in transforms_section.options:
                    for each_field in transforms_section.options["FIELDS"].value.split(","):
                        yield each_field.strip()

                if "FORMAT" in transforms_section.options:
                    regex = r"(\S*)::"
                    yield from re.findall(regex, transforms_section.options["FORMAT"].value)
        except KeyError:
            LOGGER.error(
                "The stanza {} does not exists in transforms.conf.".format(
                    transforms_section
                ),
            )

    @convert_to_fields
    def get_lookup_fields(self, props_property):
        """
        This extracts the lookup fields in which we will use for testing later on.

        Args:
            props_property(splunk_appinspect.configuration_file.ConfigurationSetting):
                The configuration setting object of eval
                properties used:
                    name : key in the configuration settings
                    value : value of the respective name in the configuration

        returns:
            List of lookup fields
        """
        parsed_fields = self.parse_lookup_str(props_property.value)
        lookup_field_list = parsed_fields["input_fields"] + parsed_fields["output_fields"]

        # If the OUTPUT or OUTPUTNEW argument is never used, then get the fields from the csv file
        if not parsed_fields["output_fields"]:
            lookup_field_list += list(self.get_lookup_csv_fields(parsed_fields["lookup_stanza"]))
        return list(set(lookup_field_list))

    def get_lookup_csv_fields(self, lookup_stanza):
        if lookup_stanza in self.transforms.sects:
            stanza = self.transforms.sects[lookup_stanza]
            if "filename" in stanza.options:
                lookup_file = stanza.options["filename"].value
                try:
                    location = os.path.join(
                        self.splunk_app_path, "lookups", lookup_file
                    )
                    with open(location, "r") as csv_file:
                        reader = csv.DictReader(csv_file)
                        fieldnames = reader.fieldnames
                        for items in fieldnames:
                            yield items.strip()
                # If there is an error. the test should fail with the current fields
                # This makes sure the test doesn't exit prematurely
                except (OSError, IOError, UnboundLocalError, TypeError) as e:
                    LOGGER.info(
                        "Could not read the lookup file, skipping test. error=%s",
                        str(e),
                    )


    def parse_lookup_str(self, lookup_str):
        """
        Get list of lookup fields by parsing the lookup string.
        If a field is aliased to another field, take the aliased field into consideration

        Args:
            lookup_str(str): Lookup string from props.conf
        returns(dict):
            lookup_stanza(str): The stanza name for the lookup in question in transforms.conf
            input_fields(list): The fields in the input of the lookup
            output_fields(list): The fields in the output of the lookup
        """

        input_output_field_list = []
        lookup_stanza = lookup_str.split(" ")[0]
        lookup_str = " ".join(lookup_str.split(" ")[1:])

        # 0: Take the left side of the OUTPUT as input fields
        # -1: Take the right side of the OUTPUT as output fields
        for input_output_index in [0, -1]:
            if "OUTPUT" not in lookup_str:
                lookup_str += " OUTPUT "

            # Take input fields or output fields depending on the input_output_index
            input_output_str = lookup_str.split("OUTPUTNEW")[input_output_index].split(
                "OUTPUT"
            )[input_output_index]

            field_parser = r"(\"(?:\\\"|[^\"])*\"|\'(?:\\\'|[^\'])*\'|[^\s,]+)\s*(?:[aA][sS]\s*(\"(?:\\\"|[^\"])*\"|\'(?:\\\'|[^\'])*\'|[^\s,]+))?"
            # field_groups: Group of max 2 fields - (source, destination) for "source as destination"
            field_groups = re.findall(field_parser, input_output_str)

            field_list = []
            # Take the last non-empty field from a field group.
            # Taking last non-empty field ensures that the aliased value will have
            # higher priority
            for each_group in field_groups:
                field_list.append(
                    [each_field for each_field in reversed(each_group) if each_field][0]
                )

            input_output_field_list.append(field_list)

        return {
            "input_fields": input_output_field_list[0],
            "output_fields": input_output_field_list[1],
            "lookup_stanza": lookup_stanza,
        }

