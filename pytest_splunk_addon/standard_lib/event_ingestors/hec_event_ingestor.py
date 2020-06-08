"""
HEC Event Ingestor class
"""
from .base_event_ingestor import EventIngestor
import requests

requests.urllib3.disable_warnings()


class HECEventIngestor(EventIngestor):
    """
    Class to ingest event via HEC
    """

    def __init__(self, hec_uri, session_headers):
        """
        init method for the class

        Args:
            hec_uri(str): {splunk_hec_scheme}://{splunk_host}:{hec_port}/services/collector/{port_type}
                port_type can be "raw" or "event"
            session_headers(dict): requesr header info.
            header_format::
                    {
                        "Authorization": f"Splunk <hec-token>",
                    }
        """
        self.hec_uri = hec_uri
        self.session_headers = session_headers

    def ingest(self, data):
        """
        Ingests data into splunk using HEC token.

        Args:
            data(dict): data dict with the info of the data to be ingested.
            data_format::
                    {
                        "sourcetype": "sample_HEC",
                        "source": "sample_source",
                        "host": "sample_host",
                        "event": "data to be ingested, can be raw or json"
                    }
        """
        try:
            response = requests.post(
                self.hec_uri,
                auth=None,
                json=data,
                headers=self.session_headers,
                verify=False,
            )
            if response.status_code not in (200, 201):
                raise Exception

        except Exception:
            print(
                "Status code: {} Reason: {} ".format(
                    response.status_code, response.reason
                )
            )
            print(response.text)
