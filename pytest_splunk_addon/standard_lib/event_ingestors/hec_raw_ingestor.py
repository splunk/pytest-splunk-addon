"""
HEC Event Ingestor class
"""
from base_event_ingestor import EventIngestor
import requests

requests.urllib3.disable_warnings()


class HECRawEventIngestor(EventIngestor):
    """
    Class to ingest event via HEC
    """

    def __init__(self, hec_uri, session_headers):
        """
        init method for the class

        Args:
            hec_uri(str): {splunk_hec_scheme}://{splunk_host}:{hec_port}/services/collector
            session_headers(dict): requesr header info.

            format::
                {
                    "Authorization": f"Splunk <hec-token>",
                }
        """
        self.hec_uri = hec_uri
        self.session_headers = session_headers

    def ingest(self, event_str, params):
        """
        Ingests data into splunk via raw endpoint.

        Args:
            event_str(str): Data string to be ingested

            params(dict): dict with the info of the data to be ingested.
            format::
                {
                    "sourcetype": "sample_HEC",
                    "source": "sample_source",
                    "host": "sample_host",
                }

        For batch ingestion of events in a single request at raw endpoint provide a list of dict in data to be ingested.

        format::

            [{"event": "raw_event_str1"}, {"event": "raw_event_str2"}]
        """
        try:
            response = requests.post(
                "{}/{}".format(self.hec_uri, "raw"),
                auth=None,
                data=event_str,
                params=params,
                headers=self.session_headers,
                verify=False,
            )
            if response.status_code not in (200, 201):
                print(
                    "Status code: {} \nReason: {} \ntext:{}".format(
                        response.status_code, response.reason, response.text
                    )
                )
                raise Exception

        except Exception as e:
            print(e)
