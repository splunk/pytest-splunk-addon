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
        self.samples =  list(eventgen_parser.parse_eventgen())

    def parse_samples(self):
        """
        Input: List of all samples
        """
        executor = ProcessPoolExecutor(max_workers=3)
        result = list(executor.map(self.tokenize, self.samples))

    def tokenize(self, sample):
        sample.tokenize()


if __name__ == "__main__":
    sample_generator = SampleGenerator('C:\\Users\\zahra.sidhpuri\\Documents\\Mission Team Automation\\PSA-Eventgen\\pytest-splunk-addon\\package_zeek')
    sample_generator.get_samples()
    sample_generator.parse_samples()
