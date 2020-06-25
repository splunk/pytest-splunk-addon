import os
import re
import copy
from . import Rule
from . import SampleEvent


class SampleStanza(object):
    """
    This class represents a stanza of the eventgen.conf.
    It contains all the parameters for the stanza such as:
        
        * Sample Name
        * Tokens
        * Sample file's raw data
        * Tokenised events
        * Sample ingestion type
    """

    def __init__(self, sample_path, eventgen_params):
        """
        init method for the class
        
        Args:
            sample_path(str): Path to the sample file 
            eventgen_params(dict): Eventgen stanzas dictionary
        """
        self.sample_path = sample_path
        self.sample_name = os.path.basename(sample_path)
        self.sample_rules = list(self._parse_rules(eventgen_params, self.sample_path))
        # self.input_type = eventgen_params.get('input_type')
        self.metadata = self._parse_meta(eventgen_params)
        self.input_type = self.metadata.get("input_type", "default")
        self.host_count = 0

    def get_raw_events(self):
        """
        This method initialize the tokenize event with raw sample
        """
        # self.sample_raw_data = list(self._get_raw_sample())
        self.tokenized_events = self._get_raw_sample()

    def get_tokenized_events(self):
        """
        Yield the tokenize event
        """
        for event in self.tokenized_events:
            event.event, event.metadata = SampleEvent.update_metadata(
                self, event.event, event.metadata
            )
            yield event

    def tokenize(self):
        """
        Tokenize the raw events(self.sample_raw_data) and stores them into self.tokenized_events.
        For backward compatibility added required count support.
        """
        required_event_count =self.metadata.get("count", 1)
        event = list(self.tokenized_events)
        for each_rule in self.sample_rules:
            event = each_rule.apply(event)
        while event and (int(required_event_count)) > len((event)):
            for each_rule in self.sample_rules:
                event = each_rule.apply(event)    
            event.extend(event)
        self.tokenized_events = event

    def _parse_rules(self, eventgen_params, sample_path):
        """
        Yield the rule instance based token replacement type.

        Args:
            eventgen_params(dict): Eventgen stanzas dictionary
            sample_path(str): Path to the sample file 
        """
        for each_token, token_value in eventgen_params['tokens']:
            yield Rule.parse_rule(token_value, eventgen_params, sample_path)

    def _parse_meta(self, eventgen_params):
        """
        Return the metadata from eventgen stanzas.

        Args:
            eventgen_params(dict): Eventgen stanzas dictionary
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
                "other",
                "default"
            ]
        """
        with open(self.sample_path, "r") as sample_file:
            if self.input_type in ["modinput", "windows_input"]:
                for each_line in sample_file:
                    event_metadata = self.get_eventmetadata()
                    yield SampleEvent(
                        each_line, event_metadata, self.sample_name
                    )

            if self.input_type in [
                "file_monitor",
                "scripted_input",
                "syslog_tcp",
                "syslog_udp",
                "other",
                "default"
            ]:
                yield SampleEvent(
                    sample_file.read(), self.metadata, self.sample_name
                )

            if not self.input_type:
                # TODO: input_type not found scenario
                pass
            # More input types to be added here.
