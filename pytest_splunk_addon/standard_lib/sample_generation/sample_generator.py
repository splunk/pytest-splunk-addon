import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

from . import EventgenParser
from . import SampleStanza
from itertools import cycle

class SampleGenerator(object):
    """
    Main Class
    Generate sample objects 
    """
    sample_stanzas = {}
    splunk_test_type = " "
    
    def __init__(self, addon_path, config_path=None, bulk_event_ingestion=True, process_count=4):
        """
        init method for the class
        
        Args:
            addon_path(str): path to the addon 
            process_count(no): generate {no} process for execution
        """
        self.addon_path = addon_path
        self.process_count = process_count
        self.config_path = config_path
        self.bulk_event_ingestion = bulk_event_ingestion

    def get_samples(self):
        """
        Generate SampleEvent object
        """
        if not SampleGenerator.sample_stanzas.get(self.bulk_event_ingestion):
            eventgen_parser = EventgenParser(self.addon_path, config_path=self.config_path)
            sample_stanzas = list(
                eventgen_parser.get_sample_stanzas()
            )
            SampleGenerator.splunk_test_type = eventgen_parser.splunk_test_type
            with ThreadPoolExecutor(min(20, max(len(sample_stanzas), 1))) as t:
                t.map(SampleStanza.get_raw_events, sample_stanzas)
            # with ProcessPoolExecutor(self.process_count) as p:
            _ = list(map(SampleStanza.tokenize, sample_stanzas, cycle([self.bulk_event_ingestion])))
            SampleGenerator.sample_stanzas[self.bulk_event_ingestion] = sample_stanzas
        for each_sample in SampleGenerator.sample_stanzas[self.bulk_event_ingestion]:
            each_sample = map(add_time, each_sample.get_tokenized_events())
            yield from each_sample


def add_time(tokenized_event):
    """
    Update _time field in event

    Args:
        sample_stanza(SampleStanza): Sample stanza instance 
    """
    if tokenized_event.metadata.get("timestamp_type") in ("plugin", None):
        time_to_ingest = time.time()
        tokenized_event.time_values = [str(time_to_ingest)]

    return tokenized_event
