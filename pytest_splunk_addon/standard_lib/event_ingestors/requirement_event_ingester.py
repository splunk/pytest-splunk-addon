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
# ******* Input - requirement_log file, Transforms.conf of the addon Function:  parse and extract events from
# requirement files from path TA/requirement_files/abc.log Example
# TA_broken/requirement_files/sample_requirement_file.log
# Function:  Sourcetype the event before ingesting  to Splunk by using
# transforms.conf regex in config [Metadata: Sourcetype]

import logging
import os

from defusedxml import cElementTree as ET

from pytest_splunk_addon.standard_lib.sample_generation.sample_event import SampleEvent

LOGGER = logging.getLogger("pytest-splunk-addon")


class RequirementEventIngestor:
    def __init__(self, requirement_file_path):
        """
        app_path to drill down to requirement file folder in package/tests/requirement_files/
        """
        self.requirement_file_path = requirement_file_path
        pass

    def check_xml_format(self, file_name):
        if ET.parse(file_name):
            return True
        else:
            return False

    def get_root(self, filename):
        """
        Input: Filename ending with .log extension
        Function to return raw event string
        """
        tree = ET.parse(filename)
        root = tree.getroot()
        return root

    def extract_raw_events(self, root):
        """
        This function returns raw events in <raw> section of the requirement files
        Iterate over all the requirement files and then send all the events to ingestor helper class
        Input: Root of the xml file
        Function to return raw event string
        """
        event = None
        for raw in root.iter("raw"):
            event = raw.text
        return event

    def escape_before_ingest(self, event):
        """
        Function to escape event's with backslash before ingest
        """
        # escape_splunk_chars = ["\""]
        # for character in escape_splunk_chars:
        #     event = event.replace(character, '\\' + character)
        event = event.strip()
        return event

    # extract transport tag
    def extract_transport_tag(self, event):
        for transport in event.iter("transport"):
            return transport.get("type")

    # to get models tag in an event
    def get_models(self, root):
        """
        Input: Root of the xml file
        Function to return list of models in each event of the log file
        """
        model_list = []
        for model in root.iter("model"):
            model_list.append(str(model.text))
        return model_list

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

    def get_events(self):
        req_file_path = self.requirement_file_path
        events = []
        host_type = None
        host, source, sourcetype = "", "", ""
        if os.path.isdir(req_file_path):
            for file1 in os.listdir(req_file_path):
                filename = os.path.join(req_file_path, file1)
                if filename.endswith(".log") or filename.endswith(".xml"):
                    if self.check_xml_format(filename):
                        root = self.get_root(filename)
                        for event_tag in root.iter("event"):
                            model_list = self.get_models(event_tag)
                            if len(model_list) != 0:
                                transport_type = self.extract_transport_tag(event_tag)
                                if transport_type == "syslog":
                                    transport_type = "syslog_tcp"
                                    LOGGER.info(f"sending data using sc4s {filename}")
                                elif transport_type in (
                                    "modinput",
                                    "Modinput",
                                    "Mod input",
                                    "Modular Input",
                                    "Modular input",
                                    "modular input",
                                    "modular_input",
                                    "Mod Input",
                                    "hec_event",
                                ):
                                    transport_type = "modinput"
                                    host, source, sourcetype = self.extract_params(
                                        event_tag
                                    )
                                    LOGGER.info(
                                        f"sending data transport_type:modinput filename:{filename} host:{host}, source:{source} sourcetype:{sourcetype}"
                                    )
                                elif transport_type == "dbx":
                                    transport_type = "modinput"
                                    host, source, sourcetype = self.extract_params(
                                        event_tag
                                    )
                                    LOGGER.info(
                                        f"sending data transport_type:dbx filename:{filename} host:{host}, source:{source} sourcetype:{sourcetype}"
                                    )
                                elif transport_type == "windows_input":
                                    host, source, sourcetype = self.extract_params(
                                        event_tag
                                    )
                                    LOGGER.info(
                                        f"sending data transport_type:windows_input filename:{filename} host:{host}, source:{source} sourcetype:{sourcetype}"
                                    )
                                elif transport_type == "forwarder":
                                    transport_type = "uf_file_monitor"
                                    host, source, sourcetype = self.extract_params(
                                        event_tag
                                    )
                                    host_type = "plugin"
                                    LOGGER.info(
                                        f"sending data transport_type:forwarder/uf_file_monitor filename:{filename} "
                                    )
                                elif transport_type in (
                                    "scripted_input",
                                    "scripted input",
                                    "hec_raw",
                                ):
                                    transport_type = "scripted_input"
                                    host, source, sourcetype = self.extract_params(
                                        event_tag
                                    )
                                    LOGGER.info(
                                        f"sending data transport_type:scripted_input or hec_raw filename:{filename} "
                                    )
                                elif transport_type == "file_monitor":
                                    host, source, sourcetype = self.extract_params(
                                        event_tag
                                    )
                                    LOGGER.info(
                                        f"sending data transport_type:file_monitor filename:{filename} "
                                    )
                                else:
                                    transport_type = "default"
                                unescaped_event = self.extract_raw_events(event_tag)
                                escaped_ingest = self.escape_before_ingest(
                                    unescaped_event
                                )
                                metadata = {
                                    "input_type": transport_type,
                                    "index": "main",
                                    "source": source,
                                    "host": host,
                                    "sourcetype": sourcetype,
                                    "timestamp_type": "event",
                                    "host_type": host_type,
                                }
                                events.append(
                                    SampleEvent(
                                        escaped_ingest, metadata, "requirement_test"
                                    )
                                )

                            else:
                                # if there is no model in event do not ingest that event
                                continue
                    else:
                        LOGGER.error(
                            "Requirement event ingestion failure: Invalid XML {}".format(
                                filename
                            )
                        )
                else:
                    LOGGER.error(
                        "Requirement event ingestion failure: Invalid file format not .log or .xml {}".format(
                            filename
                        )
                    )
        else:
            LOGGER.error(
                "Requirement event ingestion failure: Invalid requirement file path {}".format(
                    req_file_path
                )
            )
        return events
