#
# Copyright 2021 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""
Provides props.conf parsing mechanism
"""
from typing import Dict
from typing import Generator
from typing import Optional
import logging
import os
import re
from itertools import product

import addonfactory_splunk_conf_parser_lib as conf_parser

from .fields import convert_to_fields
from .transforms_parser import TransformsParser

LOGGER = logging.getLogger("pytest-splunk-addon")


class PropsParser(object):
    """
    Parses props.conf and extracts the fields.

    Args:
        splunk_app_path (str): Path of the Splunk app
    """

    def __init__(self, splunk_app_path: str):
        self._conf_parser = conf_parser.TABConfigParser()
        self.splunk_app_path = splunk_app_path
        self._props = None
        self.transforms_parser = TransformsParser(self.splunk_app_path)

    @property
    def props(self) -> Optional[Dict]:
        if self._props is not None:
            return self._props
        props_conf_path = os.path.join(self.splunk_app_path, "default", "props.conf")
        LOGGER.info("Parsing props.conf")
        self._conf_parser.read(props_conf_path)
        self._props = self._conf_parser.item_dict()
        return self._props if self._props else None

    def get_props_fields(self):
        """
        Parse the props.conf and yield all supported fields

        Yields:
            generator of all the supported fields
        """
        for stanza_type, stanza_name, stanza_values in self._get_props_stanzas():
            for key, value in stanza_values.items():
                LOGGER.info(f"Parsing parameter={key} of stanza={stanza_name}")
                if not re.match("REPORT", key, re.IGNORECASE):
                    LOGGER.info(f"Trying to parse classname={key}")
                    parsing_method = self._get_props_method(key)
                    if parsing_method:
                        field_list = list(parsing_method(key, value))
                        if field_list:
                            yield {
                                "stanza": stanza_name,
                                "stanza_type": stanza_type,
                                "classname": key,
                                "fields": field_list,
                            }
                else:
                    for transform_stanza, fields in self._get_report_fields(key, value):
                        field_list = list(fields)
                        if field_list:
                            yield {
                                "stanza": stanza_name,
                                "stanza_type": stanza_type,
                                "classname": f"{key}::{transform_stanza}",
                                "fields": field_list,
                            }

    def _get_props_method(self, class_name: str):
        """
        Get the parsing method depending on classname

        Args:
            class_name (str): class name of the props property

        Returns:
            instance method to parse the property
        """
        method_mapping = {
            "EXTRACT": self._get_extract_fields,
            "EVAL": self._get_eval_fields,
            "FIELDALIAS": self._get_fieldalias_fields,
            "LOOKUP": self._get_lookup_fields,
        }
        for each_type in method_mapping:
            if re.match(each_type, class_name, re.IGNORECASE):
                LOGGER.info(f"Matched method of type={each_type}")
                return method_mapping[each_type]
        else:
            LOGGER.warning(f"No parser available for {class_name}. Skipping...")

    def _get_props_stanzas(self) -> Optional[Generator]:
        """
        Parse the props.conf of the App & yield stanzas.
        For source with | (OR), it will return all combinations

        Yields:
            generator of stanzas from the props
        """
        if not self.props:
            return
        for stanza_name, stanza_values in self.props.items():
            if stanza_name.startswith("host::"):
                LOGGER.warning("Host stanza is not supported. Skipping..")
                continue
            if stanza_name.startswith("source::"):
                LOGGER.info(f"Parsing Source based stanza: {stanza_name}")
                for each_source in self.get_list_of_sources(stanza_name):
                    yield "source", each_source, stanza_values
            else:
                LOGGER.info(f"Parsing Sourcetype based stanza: {stanza_name}")
                yield "sourcetype", stanza_name, stanza_values

    @staticmethod
    def get_list_of_sources(source: str) -> Generator:
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

    @convert_to_fields
    def _get_extract_fields(self, name: str, value: str):
        """
        Returns the fields parsed from EXTRACT

        Example::

            EXTRACT-one = regex with (?<capturing_group>.*)

        Args:
            name: key in the configuration settings
            value: value of the respective name in the configuration

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
        for field in re.findall(regex, value):
            if not field.startswith(("_KEY_", "_VAL_")):
                fields_group.append(field)
                yield field

        # If SOURCE_KEY is used in EXTRACT, generate the test for the same.
        regex_for_source_key = r"(?:(?i)in\s+(\w+))\s*$"
        extract_source_key = re.search(regex_for_source_key, value, re.MULTILINE)
        if extract_source_key:
            LOGGER.info(f"Found a source key in {name}")
            yield extract_source_key.group(1)
            fields_group.insert(0, extract_source_key.group(1))

    @convert_to_fields
    def _get_eval_fields(self, name, value):
        """
        Return the fields parsed from EVAL

        Example::

            EVAL-action = if(isnull(action), "unknown", action)

        Args:
            name: key in the configuration settings
            value: value of the respective name in the configuration

        Yields:
            generator of fields
        """
        regex = r"EVAL-(?P<FIELD>.*)"
        if not value == "null()":
            yield from re.findall(regex, name, re.IGNORECASE)

    @convert_to_fields
    def _get_fieldalias_fields(self, name: str, value: str):
        """
        Return the fields parsed from FIELDALIAS

        Example::

            FIELDALIAS-class = source AS dest, sc2 AS dest2

        Args:
            name: key in the configuration settings
            value: value of the respective name in the configuration

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
        fields_tuples = re.findall(regex, value, re.IGNORECASE)
        return list(set([item for t in fields_tuples for item in t]))

    def _get_report_fields(self, name: str, value: str):
        """
        Returns the fields parsed from REPORT

        In order to parse the fields REPORT, the method parses the
        transforms.conf and returns the list

        Args:
            name: key in the configuration settings
            value: value of the respective name in the configuration

        Yields:
            generator of (transform_stanza ,fields) parsed from transforms.conf
        """

        transforms_itr = (each_stanza.strip() for each_stanza in value.split(","))
        for transforms_section in transforms_itr:
            yield (
                transforms_section,
                self.transforms_parser.get_transform_fields(transforms_section),
            )

    @convert_to_fields
    def _get_lookup_fields(self, name: str, value: str):
        """
        Extracts the lookup fields

        Args:
            name: key in the configuration settings
            value: value of the respective name in the configuration

        Returns:
            List of lookup fields
        """
        parsed_fields = self._parse_lookup(value)
        lookup_field_list = (
            parsed_fields["input_fields"] + parsed_fields["output_fields"]
        )

        # If the OUTPUT or OUTPUTNEW argument is never used, then get the fields from the csv file
        if not parsed_fields["output_fields"]:
            LOGGER.info(
                "OUTPUT fields not found classname=%s. Parsing the lookup csv file",
                name,
            )
            lookup_field_list += list(
                self.transforms_parser.get_lookup_csv_fields(
                    parsed_fields["lookup_stanza"]
                )
            )
        return list(set(lookup_field_list))

    def _parse_lookup(self, lookup: str):
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
        lookup_stanza = lookup.split(" ")[0]
        lookup_str = " ".join(lookup.split(" ")[1:])

        # 0: Take the left side of the OUTPUT as input fields
        # -1: Take the right side of the OUTPUT as output fields
        for input_output_index in [0, -1]:
            if "OUTPUT" not in lookup_str:
                lookup_str += " OUTPUT "

            # Take input fields or output fields depending on the input_output_index
            input_output_str = lookup_str.split("OUTPUTNEW")[input_output_index].split(
                "OUTPUT"
            )[input_output_index]

            field_parser = r"(\"(?:\\\"|[^\"])*\"|\'(?:\\\'|[^\'])*\'|[^\s,]+)\s*(?:[aA][sS]\s+(\"(?:\\\"|[^\"])*\"|\'(?:\\\'|[^\'])*\'|[^\s,]+))?"
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
