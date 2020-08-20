from . import (
    HECEventIngestor,
    HECRawEventIngestor,
    HECMetricEventIngestor,
    SC4SEventIngestor,
)
from ..sample_generation import SampleXdistGenerator

class IngestorHelper(object):
    """
    Module for helper methods for ingestors.
    """
    @classmethod
    def get_event_ingestor(cls, input_type, ingest_meta_data):
        """
        Based on the input_type of the event, it returns an appropriate ingestor.
        """
        ingest_methods = {
            "modinput": HECEventIngestor,
            "windows_input": HECEventIngestor,
            "file_monitor": HECRawEventIngestor,
            "scripted_input": HECRawEventIngestor,
            "hec_metric": HECMetricEventIngestor,
            "syslog_tcp": SC4SEventIngestor,
            "syslog_udp": None,  # TBD
            "default": HECRawEventIngestor
        }

        ingestor = ingest_methods.get(input_type)(ingest_meta_data)
        return ingestor

    @classmethod
    def ingest_events(cls, ingest_meta_data, addon_path, config_path, thread_count):
        """
        Events are ingested in the splunk.
        Args:
            ingest_meta_data(dict): Dictionary of required meta_data.
            addon_path: Path to Splunk app package.
            config_path: Path to pytest-splunk-addon-sample-generator.conf.
            bulk_event_ingestion(bool): Boolean param for bulk event ingestion.

        """
        sample_generator = SampleXdistGenerator(addon_path, config_path)
        store_sample = sample_generator.get_samples()
        tokenized_events = store_sample.get("tokenized_events")
        ingestor_dict = dict()
        for event in tokenized_events:
            input_type = event.metadata.get("input_type")
            if input_type in ["modinput", "windows_input", "syslog_tcp", "syslog_udp"]:
                event.event = event.event.encode("utf-8").decode()
            else:
                event.event = event.event.encode("utf-8")
            if input_type in ingestor_dict:
                ingestor_dict[input_type].append(event)
            else:
                ingestor_dict[input_type] = [event]
        for input_type, events in ingestor_dict.items():

            event_ingestor = cls.get_event_ingestor(input_type, ingest_meta_data)
            event_ingestor.ingest(events, thread_count)
