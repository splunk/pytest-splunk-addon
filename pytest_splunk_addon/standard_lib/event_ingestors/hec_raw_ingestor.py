"""
HEC Raw Ingestor class
"""
from .base_event_ingestor import EventIngestor
import requests
import concurrent.futures
import logging
import os

requests.urllib3.disable_warnings()

LOGGER = logging.getLogger("pytest-splunk-addon")

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

    def ingest(self, events):
        """
        Ingests data into splunk via raw endpoint.

        Args:
            event_str(str): Data string to be ingested
            format::
                '127.0.0.1 - admin [28/Sep/2016:09:05:26.875 -0700] "GET /servicesNS/admin/launcher/data/ui/views?count=-1 HTTP/1.0" 200 126721 - - - 6ms'


            params(dict): dict with the info of the data to be ingested.
            format::
                {
                    "sourcetype": "sample_HEC",
                    "source": "sample_source",
                    "host": "sample_host",
                }

        For batch ingestion of events in a single request at raw endpoint provide a string of events in data to be ingested.

        format::
            '''
                127.0.0.1 - admin [28/Sep/2016:09:05:26.875 -0700] "GET /servicesNS/admin/launcher/data/ui/views?count=-1 HTTP/1.0" 200 126721 - - - 6ms
                127.0.0.1 - admin [28/Sep/2016:09:05:26.917 -0700] "GET /servicesNS/admin/launcher/data/ui/nav/default HTTP/1.0" 200 4367 - - - 6ms
                127.0.0.1 - admin [28/Sep/2016:09:05:26.941 -0700] "GET /services/apps/local?search=disabled%3Dfalse&count=-1 HTTP/1.0" 200 31930 - - - 4ms
            '''
        """
        main_event = []
        param_list = []
        for event in events:
            param_list.append({
                "sourcetype": event.metadata.get('sourcetype', 'pytest_splunk_addon'),
                "source": event.metadata.get('source', 'pytest_splunk_addon:hec:raw'),
                "host": event.metadata.get('host', 'default'),
            })
            main_event.append(event.event)
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            executor.map(self.__ingest, main_event, param_list)

    def __ingest(self, event, params):
        try:
            response = requests.post(
                "{}/{}".format(self.hec_uri, "raw"),
                auth=None,
                data=event,
                params=params,
                headers=self.session_headers,
                verify=False,
            )
            if response.status_code not in (200, 201):
                LOGGER.debug(
                    "Status code: {} \nReason: {} \ntext:{}".format(
                        response.status_code, response.reason, response.text
                    )
                )
                raise Exception

        except Exception as e:
            LOGGER.error(e)
            os._exit(0)