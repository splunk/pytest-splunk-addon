from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

from . import EventgenParser
from . import SampleStanza
class SampleGenerator(object):
    """
    Main Class
    Generate sample objects 
    """
    def __init__(self, addon_path, process_count=4):
        self.addon_path = addon_path
        self.process_count = process_count

    def get_samples(self):
        """
        Generate SampleEvent object 
        """
        eventgen_parser = EventgenParser(self.addon_path)
        sample_stanzas = list(eventgen_parser.get_sample_stanzas())
        with ThreadPoolExecutor(min(20, len(sample_stanzas))) as t:
            t.map(SampleStanza.get_raw_events, sample_stanzas)
        # with ProcessPoolExecutor(self.process_count) as p:
        _ = list(map(SampleStanza.tokenize, sample_stanzas))

        for each_sample in sample_stanzas:
            yield from each_sample.get_tokenized_events()
def main():
    sample_generator = SampleGenerator(r'G:\My Drive\TA-Factory\automation\testing\package')
    print(sample_generator.get_samples())
