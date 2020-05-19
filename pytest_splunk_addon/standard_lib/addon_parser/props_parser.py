# -*- coding: utf-8 -*-
"""
Provides props.conf parsing mechanism
"""
import logging
import re 
from itertools import product
from . import convert_to_fields, Field
from . import TransformsParser

LOGGER = logging.getLogger("pytest-splunk-addon")

class PropsParser(object):
    """
    Parses props.conf and extracts the fields.
    
    Args:
        splunk_app_path (str): Path of the Splunk app
        app (splunk_appinspect.App): Object of Splunk app
    """

    def __init__(self, splunk_app_path, app):
        self.app = app 
        self.splunk_app_path = splunk_app_path
        self._props = None
        self.transforms_parser = TransformsParser(self.splunk_app_path, self.app)

    @property
    def props(self):
        try:
            if not self._props:
                LOGGER.info("Parsing props.conf")
                self._props = self.app.props_conf()
            return self._props
        except OSError:
            LOGGER.warning("props.conf not found.")
            return None

    def get_props_fields(self):
        """
        Parse the props.conf and yield all supported fields

        Yields:
            generator of all the supported fields 
        """
        for stanza_type, stanza_name, stanza in self.get_props_stanzas():
            for classname in stanza.options:
                LOGGER.info(
                    "Parsing parameter=%s of stanza=%s",
                    classname,
                    stanza_name,
                )
                props_property = stanza.options[classname]
                if not re.match("REPORT", classname, re.IGNORECASE):
                    LOGGER.info("Trying to parse classname=%s", classname)
                    parsing_method = self.get_props_method(classname)
                    if parsing_method:
                        field_list = list(parsing_method(props_property))
                        if field_list:
                            yield {
                                "stanza": stanza_name,
                                "stanza_type": stanza_type,
                                "classname": classname,
                                "fields": field_list
                            }
                else:
                    for transform_stanza, fields in self.get_report_fields(props_property):
                        field_list = list(fields)
                        if field_list:
                            yield {
                                "stanza": stanza_name,
                                "stanza_type": stanza_type,
                                "classname": f"{classname}::{transform_stanza}",
                                "fields": field_list
                            }

    def get_props_method(self, class_name):
        """
        Get the parsing method depending on classname
        
        Args:
            class_name (str): class name of the props property 

        Returns:
            instance method to parse the property
        """
        method_mapping = {
            "EXTRACT": self.get_extract_fields,
            "EVAL": self.get_eval_fields,
            "FIELDALIAS": self.get_fieldalias_fields,
            "LOOKUP": self.get_lookup_fields
        }
        for each_type in method_mapping:
            if re.match(each_type, class_name, re.IGNORECASE):
                LOGGER.info("Matched method of type=%s", each_type)
                return method_mapping[each_type]
        else:
            LOGGER.warning("No parser available for %s. Skipping...", class_name)

    def get_props_stanzas(self):
        """
        Parse the props.conf of the App & yield stanzas.
        For source with | (OR), it will return all combinations

        Yields:
            generator of stanzas from the props
        """
        if not self.props:
            return
        for stanza_name in self.props.sects:
            stanza = self.props.sects[stanza_name]
            if stanza.name.startswith("host::"):
                LOGGER.warning("Host stanza is not supported. Skipping..")
                continue
            if stanza.name.startswith("source::"):
                LOGGER.info("Parsing Source based stanza: %s", stanza.name)
                for each_source in self.get_list_of_sources(stanza_name):
                    yield "source", each_source, stanza
            else:
                LOGGER.info("Parsing Sourcetype based stanza: %s", stanza.name)
                yield "sourcetype", stanza.name, stanza

    @staticmethod
    def get_list_of_sources(source):
        """
        For source with | (OR), it will return all combinations.
        Uses itertools.product to list the combinations 

        Example::

            input "(preA|preB)str(postX|postY)"
            output [
                preAstrpostX
                preBstrpostX
                preAstrpostY
                preBstrpostY
            ]

        Args:
            source (str): Source name

        Yields:
            generator of source name
        """
        LOGGER.debug("Finding combinations of a source..")
        match_obj = re.search(r"source::(.*)", source)
        value = match_obj.group(1).replace("...", "*")
        sub_groups = re.findall(r"\([^\)]+\)", value)
        sub_group_list = []
        for each_group in sub_groups:
            sub_group_list.append(each_group.strip("()").split("|"))
        template = re.sub(r"\([^\)]+\)", "{}", value)
        count = 0
        for each_permutation in product(*sub_group_list):
            count += 1
            yield template.format(*each_permutation)
        LOGGER.debug("Found %d combinations", count)


    def get_sourcetype_assignments(self, props_property):
        """
        Get the sourcetype assigned for the source

        Example::

            [source::/splunk/var/log/splunkd.log]
            sourcetype = splunkd

        Args:
            props_property (splunk_appinspect.configuration_file.ConfigurationSetting): 
                The configuration setting object of REPORT.
                properties used:

                * name : key in the configuration settings
                * value : value of the respective name in the configuration

        Yields:
            the sourcetype field with possible value
        """
        yield Field({
            "name": props_property.name,
            "expected_values": [props_property.value]
        })

    @convert_to_fields
    def get_extract_fields(self, props_property):
        """
        Returns the fields parsed from EXTRACT

        Example::

            EXTRACT-one = regex with (?<capturing_group>.*)

        Args:
            props_property (splunk_appinspect.configuration_file.ConfigurationSetting): 
                The configuration setting object of EXTRACT.
                properties used:

                * name : key in the configuration settings
                * value : value of the respective name in the configuration

        Regex:
            Parse the fields from a regex. Examples,

            * (?<name>regex)
            * (?'name'regex)
            * (?P<name>regex)

        Yields:
            generator of fields
        """
        regex = r"\(\?P?(?:[<'])([^\>'\s]+)[\>']"
        fields_group = []
        for field in re.findall(regex, props_property.value):
            if not field.startswith(("_KEY_", "_VAL_")):
                fields_group.append(field)
                yield field

        # If SOURCE_KEY is used in EXTRACT, generate the test for the same.
        regex_for_source_key = r"(?:(?i)in\s+(\w+))\s*$"
        extract_source_key = re.search(
            regex_for_source_key, props_property.value, re.MULTILINE
        )
        if extract_source_key:
            LOGGER.info("Found a source key in %s", props_property.name)
            yield extract_source_key.group(1)
            fields_group.insert(0, extract_source_key.group(1))


    @convert_to_fields
    def get_eval_fields(self, props_property):
        """
        Return the fields parsed from EVAL

        Example::

            EVAL-action = if(isnull(action), "unknown", action)

        Args:
            props_property (splunk_appinspect.configuration_file.ConfigurationSetting): 
                The configuration setting object of eval
                properties used:

                * name : key in the configuration settings
                * value : value of the respective name in the configuration

        Yields:
            generator of fields
        """
        regex = r"EVAL-(?P<FIELD>.*)"
        yield from re.findall(regex, props_property.name, re.IGNORECASE)


    @convert_to_fields
    def get_fieldalias_fields(self, props_property):
        """
        Return the fields parsed from FIELDALIAS

        Example::

            FIELDALIAS-class = source AS dest, sc2 AS dest2

        Args:
            props_property (splunk_appinspect.configuration_file.ConfigurationSetting): 
                The configuration setting object of FIELDALIAS
                properties used:

                * name : key in the configuration settings
                * value : value of the respective name in the configuration

        Regex:
            Description:

            * Find all field alias group separated by space or comma

            Examples:

            * field_source AS field_destination
            * "Field Source" as "Field Destination"
            * field_source ASNEW 'Field Destination'
            * field_source asnew field_destination

        Yields:
            generator of fields
        """
        regex = (
            r"(\"(?:\\\"|[^\"])*\"|\'(?:\\\'|[^\'])*\'|[^\s,]+)"
            r"\s+(?i)(?:as(?:new)?)\s+"
            r"(\"(?:\\\"|[^\"])*\"|\'(?:\\\'|[^\'])*\'|[^\s,]+)"
        )
        fields_tuples = re.findall(regex, props_property.value, re.IGNORECASE)
        # Convert list of tuples into list
        return list(set([item for t in fields_tuples for item in t]))


    def get_report_fields(self, props_property):
        """
        Returns the fields parsed from REPORT

        In order to parse the fields REPORT, the method parses the 
        transforms.conf and returns the list

        Args:
            props_property (splunk_appinspect.configuration_file.ConfigurationSetting): 

                The configuration setting object of REPORT.
                properties used:

                * name : key in the configuration settings
                * value : value of the respective name in the configuration

        Yields:
            generator of (transform_stanza ,fields) parsed from transforms.conf 
        """

        transforms_itr = (each_stanza.strip() for each_stanza in props_property.value.split(","))
        for transforms_section in transforms_itr:
            yield (
                transforms_section, 
                self.transforms_parser.get_transform_fields(transforms_section)
            ) 


    @convert_to_fields
    def get_lookup_fields(self, props_property):
        """
        Extracts the lookup fields 

        Args:
            props_property (splunk_appinspect.configuration_file.ConfigurationSetting): 
                The configuration setting object of eval
                properties used:

                * name : key in the configuration settings
                * value : value of the respective name in the configuration

        Returns:
            List of lookup fields
        """
        parsed_fields = self.parse_lookup_str(props_property.value)
        lookup_field_list = parsed_fields["input_fields"] + parsed_fields["output_fields"]

        # If the OUTPUT or OUTPUTNEW argument is never used, then get the fields from the csv file
        if not parsed_fields["output_fields"]:
            LOGGER.info("OUTPUT fields not found classname=%s. Parsing the lookup csv file",
                props_property.name
            )
            lookup_field_list += list(
                    self.transforms_parser.get_lookup_csv_fields(parsed_fields["lookup_stanza"])
                )
        return list(set(lookup_field_list))


    def parse_lookup_str(self, lookup_str):
        """
        Get list of lookup fields by parsing the lookup string.
        If a field is aliased to another field, take the aliased field into consideration

        Example::

            LOOKUP-class = lookup_stanza input_field OUTPUT output_field

        Args:
            lookup_str (str): Lookup string from props.conf

        Regex:
            Parse the fields from the lookup string. Examples,

            * field1 AS field2, field3 field4 as field5 

        Returns:
            (dict):
                lookup_stanza (str): The stanza name for the lookup in question in transforms.conf
                input_fields (list): The fields in the input of the lookup
                output_fields (list): The fields in the output of the lookup
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


