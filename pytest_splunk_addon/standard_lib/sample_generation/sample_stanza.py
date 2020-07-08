import os
import re
import copy
from . import Rule
from . import SampleEvent
import warnings
import logging

LOGGER = logging.getLogger("pytest-splunk-addon")

BULK_EVENT_COUNT = 100
MAXIMUM_EVENT_COUNT = 250
class SampleStanza(object):
    """
    This class represents a stanza of the eventgen.conf.
    It contains all the parameters for the stanza such as:
        
        * Sample Name
        * Tokens
        * Sample file's raw data
        * Tokenised events
        * Sample ingestion type

    Args:
        sample_path (str): Path to the sample file 
        eventgen_params (dict): Dictionary representing eventgen.conf
    """

    def __init__(self, sample_path, eventgen_params):
        self.sample_path = sample_path
        self.sample_name = os.path.basename(sample_path)
        self.sample_rules = list(self._parse_rules(eventgen_params, self.sample_path))
        self.metadata = self._parse_meta(eventgen_params)
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
            event.event, event.metadata = SampleEvent.update_metadata(
                self, event.event, event.metadata
            )
            yield event

    def tokenize(self, bulk_event_ingestion):
        """
        Tokenizes the raw events by replacing all the tokens in it.

        Args:
            bulk_event_ingestion (bool): 
                
                * True: For search time testing
                * False: For index time testing
        """
        event = list(self.tokenized_events)

        if bulk_event_ingestion:
            required_event_count = self.metadata.get("count")
            if required_event_count is None or int(required_event_count) == 0:
                required_event_count = BULK_EVENT_COUNT
                if int(required_event_count) > 250:
                    required_event_count = MAXIMUM_EVENT_COUNT     
            for each_rule in self.sample_rules:
                if each_rule:
                    event = each_rule.apply(event)

            bulk_event = event
            raw_event = []
            event_counter = 0
            while (int(required_event_count)) > len((bulk_event)):
                raw_event.insert(event_counter, list(self._get_raw_sample()))
                for each_rule in self.sample_rules:
                    if each_rule:
                        raw_event[event_counter] = each_rule.apply(raw_event[event_counter])
                bulk_event.extend(raw_event[event_counter])
                event_counter = event_counter+1
            event = bulk_event[:int(required_event_count)]
        
        else:
            for each_rule in self.sample_rules:
                event = each_rule.apply(event)     
        self.tokenized_events = event

    def _parse_rules(self, eventgen_params, sample_path):
        """
        Yield the rule instance based token replacement type.

        Args:
            eventgen_params (dict): Eventgen stanzas dictionary
            sample_path (str): Path to the sample file
        """
        token_list = self._sort_tokens_by_replacement_type_all(eventgen_params['tokens'])
        for each_token, token_value in token_list:
            yield Rule.parse_rule(token_value, eventgen_params, sample_path)

    def _parse_meta(self, eventgen_params):
        """
        Return the metadata from eventgen stanzas.

        Args:
            eventgen_params (dict): Eventgen stanzas dictionary
        """
        metadata = {
            key: eventgen_params[key]
            for key in eventgen_params
            if key != "tokens"
        }
        metadata.update(host=self.sample_name)
        if metadata.get("input_type") is None:
            metadata.update(input_type="default")        
        return metadata

    def get_eventmetadata(self):
        """
        Return the unique host metadata for event.
        """
        self.host_count += 1
        event_host = self.metadata.get("host") + "_" + str(self.host_count)
        event_metadata = copy.deepcopy(self.metadata)
        event_metadata.update(host=event_host)
        return event_metadata

    def _get_raw_sample(self):
        """
        Converts a sample file into raw events based on the input type.
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
        with open(self.sample_path, "r") as sample_file:
            if self.input_type in ["modinput", "windows_input"]:
                for each_line in sample_file:
                    if not each_line == '\n':
                        event_metadata = self.get_eventmetadata()
                        yield SampleEvent(
                            each_line, event_metadata, self.sample_name
                        )
            elif self.input_type in [
                "file_monitor",
                "scripted_input",
                "syslog_tcp",
                "syslog_udp",
                "default"
            ]:
                event = sample_file.read()
                while event[-1] == '\n': event = event[:-1]
                yield SampleEvent(
                    event, self.metadata, self.sample_name
                )
            else:
                LOGGER.warning("Unsupported input_type found: '{}' using default input_type".format(self.input_type))
                warnings.warn(UserWarning("Unsupported input_type found: '{}' using default input_type".format(self.input_type)))
                self.metadata["input_type"] = "default"
                yield SampleEvent(
                    sample_file.read(), self.metadata, self.sample_name
                )

            if not self.input_type:
                # TODO: input_type not found scenario
                pass
            # More input types to be added here.

    def _sort_tokens_by_replacement_type_all(self, tokens_dict):
        """
        Return the sorted token list by replacementType=all first in list.

        Args:
            tokens_dict (dict): tokens dictionary
        """
        token_list = []
        for token in tokens_dict.items():
            if token[1]['replacementType'] == 'all':
                token_list.insert(0, token) 
            else:
                token_list.append(token)
        return token_list
