from . import (
    HECEventIngestor,
    HECRawEventIngestor,
    HECMetricEventIngestor,
    SC4SEventIngestor,
)


class IngestorHelper(object):
    """
    Module for helper methods for ingestors.
    """
    @classmethod
    def get_event_ingestor(self, input_type, ingest_meta_data):
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
