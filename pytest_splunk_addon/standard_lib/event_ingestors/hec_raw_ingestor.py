"""
HEC Event Ingestor class
"""
from .base_event_ingestor import EventIngestor
import requests

requests.urllib3.disable_warnings()


class HECRawEventIngestor(EventIngestor):
    """
    Class to ingest event via HEC
    """

    def __init__(self, required_configs):
        """
        init method for the class

        Args:
            required_configs(dict): {
                hec_uri: {splunk_hec_scheme}://{splunk_host}:{hec_port}/services/collector,
                session_headers(dict): {
                    "Authorization": f"Splunk <hec-token>",
                }
            }
        """
        self.hec_uri = required_configs['splunk_hec_uri']
        self.session_headers = required_configs['session_headers']

    def ingest(self, event):
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
        params = {
            "sourcetype": event.metadata.get('sourcetype', 'pytest_splunk_addon'),
            "source": event.metadata.get('source', 'pytest_splunk_addon:hec:raw'),
            "host": event.metadata.get('host', 'default'),
        }
        try:
            response = requests.post(
                "{}/{}".format(self.hec_uri, "raw"),
                auth=None,
                data=event.event,
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
