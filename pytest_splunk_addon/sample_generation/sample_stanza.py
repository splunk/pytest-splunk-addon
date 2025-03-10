#
# Copyright 2025 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import re
import copy
from . import Rule
from . import raise_warning
from . import SampleEvent
import logging
import xmltodict
from collections import namedtuple

LOGGER = logging.getLogger("pytest-splunk-addon")

TIMEZONE_REX = "((\+1[0-2])|(-1[0-4])|[+|-][0][0-9])([0-5][0-9])"
BULK_EVENT_COUNT = 250

token_value = namedtuple("token_value", ["key", "value"])


class SampleStanza(object):
    """
    This class represents a stanza of the pytest-splunk-addon-data.conf.
    It contains all the parameters for the stanza such as:

        * Sample Name
        * Tokens
        * Sample file's raw data
        * Tokenized events
        * Sample ingestion type

    Args:
        sample_path (str): Path to the sample file
        psa_data_params (dict): Dictionary representing pytest-splunk-addon-data.conf
    """

    def __init__(self, sample_path, psa_data_params):
        self.sample_path = sample_path
        self.sample_name = os.path.basename(sample_path)
        self.metadata = self._parse_meta(psa_data_params)
        self.sample_rules = list(self._parse_rules(psa_data_params, self.sample_path))
        self.input_type = self.metadata.get("input_type", "default")
        self.host_count = 0

    def get_raw_events(self):
        """
        Gets the raw events from the sample file.
        """
        # self.sample_raw_data = list(self._get_raw_sample())
        self.tokenized_events = self._get_raw_sample()

    def get_tokenized_events(self):
        """
        Yields the tokenized events
        """
        for event in self.tokenized_events:
            event.event, event.metadata, event.key_fields = SampleEvent.update_metadata(
                self, event.event, event.metadata, event.key_fields
            )
            yield event

    def tokenize(self, conf_name):
        """
        Tokenizes the raw events by replacing all the tokens in it.

        Args:
            conf_name (str): Name of the conf file, "psa-data-gen"
        """
        if conf_name == "eventgen":
            required_event_count = self.metadata.get("count")
        else:
            required_event_count = 1

        if (
            required_event_count is None
            or int(required_event_count) == 0
            or int(required_event_count) > BULK_EVENT_COUNT
        ):
            required_event_count = BULK_EVENT_COUNT

        bulk_event = []
        raw_event = []
        event_counter = 0
        while (int(required_event_count)) > len((bulk_event)):
            raw_event.insert(event_counter, list(self._get_raw_sample()))
            if not raw_event[-1]:
                break
            for each_rule in self.sample_rules:
                if each_rule:
                    raw_event[event_counter] = each_rule.apply(raw_event[event_counter])
            for event in raw_event[event_counter]:
                host_value = event.metadata.get("host")
                host = token_value(key=host_value, value=host_value)
                event.update_requirement_test_field("host", "##host##", host)
            bulk_event.extend(raw_event[event_counter])
            event_counter = event_counter + 1

        if self.metadata.get("breaker") is not None:
            self.metadata.update(sample_count=1)
            for each in bulk_event:
                each.metadata.update(sample_count=1)

        if self.metadata.get("expected_event_count") is None:
            breaker = self.metadata.get("breaker")
            if breaker is not None:
                expected_events = 0
                for each_event in bulk_event:
                    expected_events += len(
                        list(filter(lambda x: x, self.break_events(each_event.event)))
                    )
            else:
                expected_events = len(bulk_event)
            self.metadata.update(expected_event_count=expected_events)
            for each in bulk_event:
                each.metadata.update(expected_event_count=expected_events)
        else:
            self.metadata.update(sample_count=1)
            for each in bulk_event:
                each.metadata.update(sample_count=1)

        self.tokenized_events = bulk_event

    def _parse_rules(self, psa_data_params, sample_path):
        """
        Yield the rule instance based token replacement type.

        Args:
            psa_data_params (dict): PSA data stanzas dictionary
            sample_path (str): Path to the sample file
        """
        token_list = self._sort_tokens_by_replacement_type_all(
            psa_data_params["tokens"]
        )
        for each_token, token_value in token_list:
            applied_rule = Rule.parse_rule(token_value, psa_data_params, sample_path)
            if not applied_rule:
                raise_warning(
                    "Unidentified Rule: '{}' for token '{}'".format(
                        token_value["replacement"], token_value["token"]
                    )
                )
            else:
                yield applied_rule

    def _parse_meta(self, psa_data_params):
        """
        Return the metadata from PSA data stanzas.

        Args:
            psa_data_params (dict): PSA data stanzas dictionary
        """
        metadata = {
            key: psa_data_params[key] for key in psa_data_params if key != "tokens"
        }
        host = metadata.get("host") or self.sample_name
        metadata.update(host=host)
        if (
            metadata.get("input_type")
            not in [
                "modinput",
                "windows_input",
                "file_monitor",
                "uf_file_monitor",
                "scripted_input",
                "syslog_tcp",
                "syslog_udp",
                "default",
            ]
            and not None
        ):
            raise_warning(
                "Invalid value for input_type found: '{}' using default input_type".format(
                    metadata.get("input_type")
                )
            )
            metadata.update(input_type="default")
        if metadata.get("host_type") not in ["event", "plugin", None]:
            raise_warning(
                "Invalid value for host_type: '{}' using host_type = plugin.".format(
                    metadata.get("host_type")
                )
            )
            metadata.update(host_type="plugin")
        if metadata.get("timestamp_type") not in ["event", "plugin", None]:
            raise_warning(
                "Invalid value for timestamp_type: '{}' using timestamp_type = plugin.".format(
                    metadata.get("timestamp_type")
                )
            )
            metadata.update(timestamp_type="plugin")
        if metadata.get("timezone") not in ["local", "0000", None] and not re.match(
            TIMEZONE_REX, metadata.get("timezone")
        ):
            raise_warning(
                "Invalid value for timezone: '{}' using timezone = 0000.".format(
                    metadata.get("timezone")
                )
            )
            metadata.update(timezone="0000")
            psa_data_params.update(timezone="0000")
        if metadata.get("timestamp_type") not in ["event", "plugin", None]:
            raise_warning(
                "Invalid value for timestamp_type: '{}' using timestamp_type = plugin.".format(
                    metadata.get("timestamp_type")
                )
            )
            metadata.update(timestamp_type="plugin")
        if (
            metadata.get("sample_count")
            and not metadata.get("sample_count").isnumeric()
        ):
            raise_warning(
                "Invalid value for sample_count: '{}' using sample_count = 1.".format(
                    metadata.get("sample_count")
                )
            )
            metadata.update(sample_count="1")
        if (
            metadata.get("expected_event_count")
            and not metadata.get("expected_event_count").isnumeric()
        ):
            raise_warning(
                "Invalid value for expected_event_count: '{}' using expected_event_count = 1.".format(
                    metadata.get("expected_event_count")
                )
            )
            metadata.update(expected_event_count="1")
        if metadata.get("count") and not metadata.get("count").isnumeric():
            raise_warning(
                "Invalid value for count: '{}' using count = 1.".format(
                    metadata.get("count")
                )
            )
            metadata.update(count="100")
        if metadata.get("index") is not None and metadata.get("input_type") in [
            "syslog_tcp",
            "tcp",
            "udp",
        ]:
            raise_warning(
                "For input_type '{}', there should be no index set".format(
                    metadata.get("input_type")
                )
            )
        if metadata.get("input_type") == "uf_file_monitor":
            metadata["host"] = metadata.get("host").replace("_", "-").replace(".", "-")
        return metadata

    def get_eventmetadata(self):
        """
        Return the unique host metadata for event.
        """
        self.host_count += 1
        event_host = self.metadata.get("host") + "_" + str(self.host_count)
        event_metadata = copy.deepcopy(self.metadata)
        event_metadata.update(host=event_host)
        LOGGER.info("event metadata: {}".format(event_metadata))
        return event_metadata

    def _get_raw_sample(self):
        """
        Converts a sample file into raw events based on the input type and breaker.
        Input: Name of the sample file for which events have to be generated.
        Output: Yields object of SampleEvent.

        If the input type is in ["modinput", "windows_input"], a new event will be generated for each line in the file.
        If the input type is in below categories, a single event will be generated for the entire file.
            [
                "file_monitor",
                "scripted_input",
                "syslog_tcp",
                "syslog_udp",
                "default"
            ]
        """
        with open(self.sample_path, "r", encoding="utf-8") as sample_file:
            sample_raw = sample_file.read()

        if self.metadata.get("requirement_test_sample"):
            samples = xmltodict.parse(sample_raw)
            events = (
                samples["device"]["event"]
                if type(samples["device"]["event"]) == list
                else [samples["device"]["event"]]
            )
            if self.metadata.get("sample_count") is None:
                self.metadata.update(sample_count="1")
            for each_event in events:
                event = each_event["raw"].strip()
                event_metadata = self.get_eventmetadata()
                requirement_test_data = self.populate_requirement_test_data(each_event)
                if "transport" in each_event.keys():
                    static_host = each_event["transport"].get("@host")
                    if static_host:
                        event_metadata.update(host=static_host)
                    static_source = each_event["transport"].get("@source")
                    if static_source:
                        event_metadata.update(source=static_source)
                yield SampleEvent(
                    event, event_metadata, self.sample_name, requirement_test_data
                )
        elif self.metadata.get("breaker"):
            for each_event in self.break_events(sample_raw):
                if each_event:
                    event_metadata = self.get_eventmetadata()
                    yield SampleEvent(each_event, event_metadata, self.sample_name)
        elif self.input_type in ["modinput", "windows_input"]:
            for each_line in sample_raw.split("\n"):
                if each_line:
                    event_metadata = self.get_eventmetadata()
                    yield SampleEvent(each_line, event_metadata, self.sample_name)
        elif self.input_type in [
            "file_monitor",
            "uf_file_monitor",
            "scripted_input",
            "syslog_tcp",
            "syslog_udp",
            "default",
        ]:
            event = sample_raw.strip()
            if not event:
                raise_warning("sample file: '{}' is empty".format(self.sample_path))
            else:
                yield SampleEvent(event, self.metadata, self.sample_name)
        if not self.input_type:
            # TODO: input_type not found scenario
            pass
        # More input types to be added here.

    def break_events(self, sample_raw):
        """
        Break sample file into list of raw events using breaker

        Args:
            sample_raw (str): Raw sample

        Return:
            event_list (list): List of raw events
        """

        sample_match = re.finditer(
            self.metadata.get("breaker"), sample_raw, flags=re.MULTILINE
        )
        pos = 0
        try:
            match_obj = next(sample_match)
            event_list = list()
            if match_obj.start() != 0:
                event_list.append(sample_raw[pos : match_obj.start()].strip())
                pos = match_obj.start()
            for _, match in enumerate(sample_match):
                event_list.append(sample_raw[pos : match.start()].strip())
                pos = match.start()
            event_list.append(sample_raw[pos:].strip())
            return event_list
        except:
            raise_warning("Invalid breaker for stanza {}".format(self.sample_name))
            return [sample_raw]

    def _sort_tokens_by_replacement_type_all(self, tokens_dict):
        """
        Return the sorted token list by replacementType=all first in list.

        Args:
            tokens_dict (dict): tokens dictionary
        """
        token_list = []
        for token in tokens_dict.items():
            if token[1]["replacementType"] == "all":
                token_list.insert(0, token)
            else:
                token_list.append(token)
        return token_list

    @staticmethod
    def populate_requirement_test_data(event):
        """
        Analyze event's datamodels, cim_fields, missing_recommended_fields, exception

        Args:
            event (dict): event data from xml file

        Return:
            requirement_test_data (dict): datamodels, cim_fields, missing_recommended_fields, exception
        """
        requirement_test_data = {}
        cim = event.get("cim")
        other_mappings = event.get("other_mappings")
        if other_mappings:
            other_fields = {}
            fields = other_mappings["field"]
            if type(fields) == list:
                for field in fields:
                    other_fields[field["@name"]] = field["@value"]
            elif type(fields) == dict:
                other_fields[fields["@name"]] = fields["@value"]
            requirement_test_data["other_fields"] = other_fields
        if cim:
            requirement_test_data["cim_version"] = cim.get("@version", "latest")
            requirement_test_data["datamodels"] = cim.get("models") or {}

            defined_fields = cim.get("cim_fields") or {}
            cim_fields = {}
            if defined_fields:
                fields = defined_fields["field"]
                if type(fields) == list:
                    for field in fields:
                        cim_fields[field["@name"]] = field["@value"]
                elif type(fields) == dict:
                    cim_fields[fields["@name"]] = fields["@value"]
            requirement_test_data["cim_fields"] = cim_fields

            missing_recommended_fields = cim.get("missing_recommended_fields") or []
            if missing_recommended_fields:
                missing_recommended_fields = (
                    missing_recommended_fields.get("field") or []
                )
                if type(missing_recommended_fields) != list:
                    missing_recommended_fields = [missing_recommended_fields]
            requirement_test_data[
                "missing_recommended_fields"
            ] = missing_recommended_fields

            defined_exceptions = cim.get("exceptions") or {}
            exceptions = {}
            if defined_exceptions:
                defined_fields = defined_exceptions["field"]
                defined_fields = (
                    defined_fields if type(defined_fields) == list else [defined_fields]
                )
                for field in defined_fields:
                    exceptions[field["@name"]] = field["@value"]
            requirement_test_data["exceptions"] = exceptions
        return requirement_test_data
