from os import path
import re
import rule


class SampleParser(object):

    path_to_samples = "path_to_samples"

    def __init__(self, name, rules, ingest_type):
        self.sample_name = name  # name of sample from stanza
        self.earliest = str
        self.latest = str
        self.timezone = str
        self.ingest_type = ingest_type
        self.sample_rules = rules  # tokens for each sample from eventgen.conf
        self.sample_raw_data = self._get_raw_sample(self.sample_name)

    def _get_raw_sample(self, sample_name):

        with open(path.join(self.path_to_samples, sample_name), 'r') as sample_file:
            return sample_file.read()
    
    def tokenize(self):

        for each_token in self.sample_rules:
            self.sample_raw_data = each_token.apply(self.sample_raw_data)
