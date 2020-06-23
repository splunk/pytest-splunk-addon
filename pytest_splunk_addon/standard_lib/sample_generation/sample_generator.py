import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

from . import EventgenParser
from . import SampleStanza

class SampleGenerator(object):
    """
    Main Class
    Generate sample objects 
    """
    sample_stanzas = []
    
    def __init__(self, addon_path, process_count=4):
        self.addon_path = addon_path
        self.process_count = process_count

    def get_samples(self):
        """
        Generate SampleEvent object
        """
        if not SampleGenerator.sample_stanzas:
            eventgen_parser = EventgenParser(self.addon_path)
            SampleGenerator.sample_stanzas = list(eventgen_parser.get_sample_stanzas())
            with ThreadPoolExecutor(min(20, len(SampleGenerator.sample_stanzas))) as t:
                t.map(SampleStanza.get_raw_events, SampleGenerator.sample_stanzas)
            # with ProcessPoolExecutor(self.process_count) as p:
            _ = list(map(SampleStanza.tokenize, SampleGenerator.sample_stanzas))
            map(add_time, SampleGenerator.sample_stanzas)
        for each_sample in SampleGenerator.sample_stanzas:
            yield from each_sample.get_tokenized_events()


def add_time(sample_stanza):
    for event in sample_stanza.get_tokenized_events():
        if (event.metadata.get("timestamp_type") == "plugin"):
            time_to_ingest = int(time.time())
            event.key_fields["_time"] = [str(time_to_ingest)]

def main():
    sample_generator = SampleGenerator(r'G:\My Drive\TA-Factory\automation\testing\package')
    print(sample_generator.get_samples())
