from concurrent.futures import ProcessPoolExecutor
from eventgen_parser import EventgenParser

class SampleGenerator(object):
    """
    Main Class
    Parse the eventgen, Generate sample objects 
    """
    PROCESS_COUNT = 4
    def __init__(self, addon_path):
        self.addon_path = addon_path

    def get_samples(self):
        """
        """
        eventgen_parser = EventgenParser(self.addon_path)
        self.samples = list(eventgen_parser.parse_eventgen())

    def parse_samples(self):
        """
        Input: List of all samples
        """
        self.get_samples()
        executor = ProcessPoolExecutor(max_workers=4)
        result = list(executor.map(self.tokenize, self.samples))

        for val in result:
            for sample in self.samples:
                if sample.sample_name in val.keys():
                    sample.tokenized_events = val[sample.sample_name]

    def tokenize(self, sample):
        tokenised_events = list(sample.tokenize())
        return {sample.sample_name: tokenised_events}


if __name__ == "__main__":
    sample_generator = SampleGenerator('C:\\Users\\zahra.sidhpuri\\Documents\\Mission Team Automation\\PSA-Eventgen\\pytest-splunk-addon\\package_zeek')
    sample_generator.parse_samples()
