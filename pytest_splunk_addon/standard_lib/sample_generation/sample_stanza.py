import os
import re
from . import Rule
from . import SampleEvent

class SampleStanza(object):
    '''
    This class represents a stanza of the eventgen.conf.
    It contains all the parameters for the stanza such as:
        ->Sample Name
        ->Tokens
        ->Sample file's raw data
        ->Tokenised events
        ->Sample ingestion type
    '''

    def __init__(self, sample_name, sample_path, eventgen_params):
        self.sample_name = sample_name
        self.sample_path = sample_path
        self.sample_rules = list(self._parse_rules(eventgen_params))
        # self.ingest_type = eventgen_params.get('ingest_type')
        self.metadata = self._parse_meta(eventgen_params)
        self.ingest_type = self.metadata.get('ingest_type', None)

    def get_raw_events(self):
        # self.sample_raw_data = list(self._get_raw_sample()) 
        self.tokenized_events = self._get_raw_sample()

    def get_tokenized_events(self):
        yield from self.tokenized_events

    def tokenize(self):
        '''
        Tokenize the raw events(self.sample_raw_data) and stores them into self.tokenized_events.
        '''
        for each_rule in self.sample_rules:
            self.tokenized_events = each_rule.apply(self.tokenized_events)

    def _parse_rules(self, eventgen_params):
        for each_token, token_value in eventgen_params['tokens'].items():
            yield Rule.parse_rule(token_value, eventgen_params)

    def _parse_meta(self, eventgen_params):
        metadata = {key:eventgen_params[key] for key in eventgen_params if key != "tokens"}
        metadata.update(host = self.sample_name)
        return metadata

    def update_metadata(self, data, metadata):
        '''
        This method is to process the syslog formated samples data
        data: raw syslog data
            data_format::
                ***SPLUNK*** source=<source> sourcetype=<sourcetype>

                fiels_1   field2   field3
                value1    value2   value3
            metadata: dictionary of metadata
            params_format::
                {
                    "host": "sample_host",
                    "source": "sample_source"
                }
        Returns:
            syslog data and params that contains syslog_headers
        '''
        try:
            header = data.split("\n", 1)[0]
            event_string = data.split("\n", 1)[1]

            meta_fields = re.findall(r"[\w]+=[^\s]+", header)
            for meta_field in meta_fields:
                field = meta_field.split("=")[0]
                value = meta_field.split("=")[1]
                metadata[field] = value

            return event_string, metadata
        except IndexError as error:
            LOGGER.error(f"Unexpected data found. Error: {error}")
            raise Exception(error)

    def _get_raw_sample(self):
        '''
        Converts a sample file into raw events based on the input type.
        Input: Name of the sample file for which events have to be generated.
        Output: Yields object of SampleEvent.

        If the input type is 'modinput', a new event will be generated for all the lines in the file.
        If the input type is 'file monitor' a single event will be generated for the entire file.
        '''
        with open(self.sample_path, 'r') as sample_file:
            if self.ingest_type == 'modinput':
                for each_line in sample_file:
                    yield SampleEvent(
                        each_line,
                        self.metadata
                    )

            if self.ingest_type == 'file_monitor':
                data = sample_file.read()

                if isinstance(data, str) and data.startswith("***SPLUNK***"):
                    event_string, metadata = self.update_metadata(data, self.metadata)
                    yield SampleEvent(
                        event_string=event_string,
                        metadata=metadata
                    )
                else:
                    yield SampleEvent(
                        data,
                        self.metadata
                    )
            
            if not self.ingest_type:
                #TODO: ingest_type not found scenario
                pass
            # More input types to be added here.
