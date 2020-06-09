from sample_event import SampleEvent
from os import path
import re
import rule


class SampleParser(object):
    '''
    This class represents a stanza of the eventgen.conf.
    It contains all the parameters for the stanza such as:
        ->Sample Name
        ->Sample ingestion type
        ->Tokens
        ->Sample file's raw data
        ->Tokenised events
    '''
    path_to_samples = "path_to_samples"

    def __init__(self, name, rules, ingest_type):
        self.sample_name = name  # name of sample from stanza
        self.earliest = str
        self.latest = str
        self.timezone = str
        self.ingest_type = ingest_type
        self.sample_rules = rules  # tokens for each sample from eventgen.conf
        self.sample_raw_data = list(self._get_raw_sample(self.sample_name))  # [SampleEvent1, SampleEvent2] #Raw Data
        self.tokenized_events = [] # [SampleEvent1, SampleEvent2] #Tokenised events

    def _get_raw_sample(self, sample_name):
        '''
        Converts a sample file into raw events based on the input type.
        Input: Name of the sample file for which events have to be generated.
        Output: Yields object of SampleEvent.

        If the input type is 'modinput', a new event will be generated for all the lines in the file.
        If the input type is 'file monitor' a single event will be generated for the entire file.
        '''
        with open(path.join(self.path_to_samples, sample_name), 'r') as sample_file:

            if(self.ingest_type == 'modinput'):
                for each_line in sample_file:
                    yield SampleEvent(
                        each_line
                    )

            if(self.ingest_type == 'file_monitor'):
                yield SampleEvent(
                    sample_file.read()
                )
            # More input types to be added here.

    def tokenize(self):
        '''
        Tokensised the raw events(self.sample_raw_data) and stores them into self.tokenized_events.
        '''
        for each_event in self.sample_raw_data:
            tokenised_event = each_event.event
            for each_token in self.sample_rules:
                tokenised_event = each_token.apply(tokenised_event)

            self.tokenized_events.append(SampleEvent(tokenised_event))
