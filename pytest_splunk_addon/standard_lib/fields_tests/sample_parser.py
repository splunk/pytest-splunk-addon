# Copyright 2022 Splunk Inc.
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

import logging
import re
import os

from defusedxml import cElementTree as ET
from defusedxml.cElementTree import ParseError

from .requirement_test_datamodel_tag_constants import dict_datamodel_tag

LOGGER = logging.getLogger("pytest-splunk-addon")


def parse_sample_files(folder_path):
    if os.path.isdir(folder_path):
        for file in os.listdir(folder_path):
            if file.endswith(".log") or file.endswith(".xml"):
                filename = os.path.join(folder_path, file)
                LOGGER.info(filename)
                for event_tag in parse_file(filename):
                    if event_tag is not None:
                        yield EventXML(event_tag)


def parse_file(filename):
    try:
        tree = ET.parse(filename)
    except ParseError:
        LOGGER.error("Invalid XML")
        tree = None
    if not tree:
        return None
    root = tree.getroot()
    for event_tag in root.iter("event"):
        yield event_tag


class XMLParser:
    def extract_transport_tag(self, event):
        for transport in event.iter("transport"):
            return str(transport.get("type"))

    def strip_syslog_header(self, raw_event):
        # remove leading space chars
        raw_event = raw_event.strip()
        CEF_format_match = re.search(
            r"\s(CEF:\d\|[^\|]+\|([^\|]+)\|[^\|]+\|[^\|]+\|[^\|]+\|([^\|]+)\|(.*))",
            raw_event,
        )
        CEF_checkpoint_match = re.search(
            r"(time=\d+\|[^\|]+\|([^\|]+)\|[^\|]+\|[^\|]+\|[^\|]+\|([^\|]+)\|(.*))",
            raw_event,
        )
        if CEF_format_match:
            stripped_header = CEF_format_match.group(1)
            return stripped_header
        if CEF_checkpoint_match:
            stripped_header = CEF_checkpoint_match.group(1)
            return stripped_header
        regex_rfc5424 = re.search(
            r"(?:(\d{4}[-]\d{2}[-]\d{2}[T]\d{2}[:]\d{2}[:]\d{2}(?:\.\d{1,6})?(?:[+-]\d{2}[:]\d{2}|Z)?)|-)\s(?:([\w][\w\d\.@-]*)|-)\s(.*)$",
            raw_event,
        )
        if regex_rfc5424:
            stripped_header = regex_rfc5424.group(3)
            return stripped_header
        #    regex = r"([A-Z][a-z][a-z]\s{1,2}\d{1,2}\s\d{2}[:]\d{2}[:]\d{2})\s+([\w][\w\d\.@-]*)\s\w*:?(.*)$",
        #   (?:\s\d{4})? Added to support cisco asa date format
        regex_rfc3164 = re.search(
            r"([A-Z][a-z][a-z]\s{1,2}\d{1,2}(?:\s\d{4})?\s\d{2}[:]\d{2}[:]\d{2})\s+([\w][\w\d\.@-]*)\s\w*:?(.*)$",
            raw_event,
        )
        if regex_rfc3164:
            stripped_header = regex_rfc3164.group(3)
            return stripped_header
        if not (CEF_format_match and regex_rfc3164 and regex_rfc5424):
            return None

    def get_event(self, root):
        """
        Input: Root of the xml file
        Function to return raw event string
        """
        event = None
        for raw in root.iter("raw"):
            event = raw.text
        return event

    def get_models(self, root):
        """
        Input: Root of the xml file
        Function to return list of models in each event of the log file
        """
        model_list = []
        for model in root.iter("model"):
            model_list.append(str(model.text))
        return model_list

    def split_model(self, model):
        """
        Input: Root of the xml file
        Function to return list of models in each event of the log file
        """
        model_name = model.split(":", 2)
        if len(model_name) == 3:
            model = model_name[0]
            dataset = model_name[1]
            subdataset = model_name[2]
            model = model.replace(" ", "_")
            model_dataset_subdaset = model + "_" + dataset + "_" + subdataset
        elif len(model_name) == 2:
            model = model_name[0]
            dataset = model_name[1]
            model = model.replace(" ", "_")
            model_dataset_subdaset = model + "_" + dataset
        else:
            model = model_name[0]
            model_dataset_subdaset = model

        return model_dataset_subdaset

    def get_event(self, root):
        """
        Input: Root of the xml file
        Function to return raw event string
        """
        event = None
        for raw in root.iter("raw"):
            event = raw.text
        return event

    def get_root(self, filename):
        """
        Input: Filename ending with .log extension
        Function to return raw event string
        """
        tree = ET.parse(filename)
        root = tree.getroot()
        return root

    def check_xml_format(self, file_name):
        if ET.parse(file_name):
            return True
        else:
            return False

        # extract_params_transport

    def extract_params(self, event):
        host, source, source_type = "", "", ""
        for transport in event.iter("transport"):
            if transport.get("host"):
                host = transport.get("host")
            if transport.get("source"):
                source = transport.get("source")
            if transport.get("sourcetype"):
                source_type = transport.get("sourcetype")
        return host, source, source_type

    def escape_host_src_srctype(self, host, source, sourcetype):
        escaped_host = host.replace('"', '\\"')
        escaped_source = source.replace('"', '\\"')
        escaped_sourcetype = sourcetype.replace('"', '\\"')
        return escaped_host, escaped_source, escaped_sourcetype

    def escape_char_event(self, event):
        """
        Input: Event getting parsed
        Function to escape special characters in Splunk
        https://docs.splunk.com/Documentation/StyleGuide/current/StyleGuide/Specialcharacters
        """
        escape_splunk_chars = [
            "`",
            "~",
            "!",
            "@",
            "#",
            "$",
            "%",
            "^",
            "&",
            "(",
            ")",
            "-",
            "=",
            "+",
            "[",
            "]",
            "}",
            "{",
            "|",
            ";",
            ":",
            "'",
            r"\,",
            "<",
            ">",
            r"\/",
            "?",
            "IN",
            "AS",
            "BY",
            "OVER",
            "WHERE",
            "LIKE",
            "NOT",
        ]
        event = event.replace("\\", "\\\\")
        # bounded_asterisk = re.search(
        #     r"\"[\s*\w*\.\-\,\\\?\_\]\[\']*\*+[\s*\w*\.\-\,\\\?\_\[\]\']*\"", event
        # )
        bounded_asterisk = re.search(r"\".*?\*+.*?\"", event)
        if bounded_asterisk:
            event = event.replace("*", "\\*")
        else:
            event = event.replace("*", " ")
        for character in escape_splunk_chars:
            event = event.replace(character, "\\" + character)
        return event


class EventXML:
    transport_types = [
        "modinput",
        "Modinput",
        "Mod input",
        "Modular Input",
        "Modular input",
        "modular input",
        "modular_input",
        "Mod Input",
        "dbx",
        "windows_input",
        "hec_event",
        "scripted_input",
        "scripted input",
        "hec_raw",
        "file_monitor",
        "forwarder",
    ]
    all_transport_types = transport_types + ["syslog"]

    def __init__(self, event_tag):
        self.event_tag = event_tag
        self.xml_parser = XMLParser()
        self.transport_type = self.xml_parser.extract_transport_tag(self.event_tag)
        self.event_string = self.get_event_string()
        self.name = self.event_tag.get("name")
        self.models = self.xml_parser.get_models(event_tag)
        self.tags_to_check = self.get_tags_to_check()
        self.list_model_dataset_subdataset = self.get_model_list()
        self.host, self.source, self.sourcetype = self.get_basic_fields()
        self.transport_type_params = self.get_transport_type_params()
        self.cim_fields = self.extract_key_value_xml("cim_fields")
        self.exceptions = self.extract_key_value_xml("exceptions")

    def get_transport_type(self):
        tt = self.xml_parser.extract_transport_tag(self.event_tag)
        if tt not in EventXML.all_transport_types:
            raise ValueError(f"Not supported transport type for {self.event_tag}")

    def get_model_list(self):
        list_model_dataset_subdataset = []
        for model in self.models:
            model = model.replace(" ", "_")
            # Function to extract data set
            model_name = self.xml_parser.split_model(model)
            list_model_dataset_subdataset.append(model_name)
            LOGGER.info(model_name)
        return list_model_dataset_subdataset

    def get_event_string(self):
        unescaped_event = self.xml_parser.get_event(self.event_tag)
        if self.transport_type.lower() == "syslog":
            stripped_event = self.xml_parser.strip_syslog_header(unescaped_event)
            unescaped_event = stripped_event
            if stripped_event is None:
                LOGGER.error("Syslog event do not match CEF, RFC_3164, RFC_5424 format")
                raise ValueError(
                    f"Empty event for syslog transport type from event_tag {self.event_tag}"
                )
        return self.xml_parser.escape_char_event(unescaped_event)

    def get_basic_fields(self):
        if self.transport_types in EventXML.transport_types:
            host, source, sourcetype = self.xml_parser.extract_params(self.event_tag)
            return self.xml_parser.escape_host_src_srctype(host, source, sourcetype)
        else:
            return None, None, None

    def get_transport_type_params(self):
        return {
            "host": self.host,
            "source": self.source,
            "sourcetype": self.sourcetype,
        }

    def get_tags_to_check(self):
        tags = []
        for model in self.models:
            tags += dict_datamodel_tag[model.replace(" ", "_").replace(":", "_")]
        return list(set(tags))

    def extract_key_value_xml(self, _type):
        key_value_dict = {}
        for type_fields in self.event_tag.iter(_type):
            for fields in type_fields.iter("field"):
                if fields.get("name"):
                    field_name = fields.get("name")
                    field_value = fields.get("value")
                    key_value_dict[field_name] = field_value
        # self.logger.info(key_value_dict)
        return key_value_dict
