from sample_event import SampleEvent
import os 
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
        sample_files = [sample_file for sample_file in os.listdir(self.path_to_samples) if re.match(sample_name, sample_file)]
        
        for sample_file in sample_files:
            with open(os.path.join(self.path_to_samples, sample_file), 'r') as sample_file:

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
        for each_sample in self.sample_raw_data:
            tokenized_events = Rule.apply([each_sample.event], self.sample_rules)
            for each_event in tokenized_events:
                yield SampleEvent(
                    each_event
                )
