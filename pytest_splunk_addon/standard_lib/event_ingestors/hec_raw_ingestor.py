from .base_event_ingestor import EventIngestor
from time import time
import requests
import concurrent.futures
import logging
import os
import time
requests.urllib3.disable_warnings()

LOGGER = logging.getLogger("pytest-splunk-addon")

class HECRawEventIngestor(EventIngestor):
    """
    Class to ingest event via HEC Raw

    The format for required_configs is::

        {
            hec_uri: {splunk_hec_scheme}://{splunk_host}:{hec_port}/services/collector,
            session_headers(dict):
            {
                "Authorization": f"Splunk <hec-token>",
            }
        }


    Args:
        required_configs(dict): Dictionary containing hec_uri and session headers
    """

    def __init__(self, required_configs):
        self.hec_uri = required_configs['splunk_hec_uri']
        self.session_headers = required_configs['session_headers']

    def ingest(self, events, thread_count):
        """
        Ingests data into splunk via raw endpoint.

        For batch ingestion of events in a single request at raw endpoint provide a string of events in data to be ingested.

        The format of event and params for ingesting a single event::

            '127.0.0.1 - admin [28/Sep/2016:09:05:26.875 -0700] "GET /servicesNS/admin/launcher/data/ui/views?count=-1 HTTP/1.0" 200 126721 - - - 6ms'

            {
                "sourcetype": "sample_HEC",
                "source": "sample_source",
                "host": "sample_host",
            }

        The format of event and params for ingesting a batch of events::

                '''127.0.0.1 - admin [28/Sep/2016:09:05:26.875 -0700] "GET /servicesNS/admin/launcher/data/ui/views?count=-1 HTTP/1.0" 200 126721 - - - 6ms
                127.0.0.1 - admin [28/Sep/2016:09:05:26.917 -0700] "GET /servicesNS/admin/launcher/data/ui/nav/default HTTP/1.0" 200 4367 - - - 6ms
                127.0.0.1 - admin [28/Sep/2016:09:05:26.941 -0700] "GET /services/apps/local?search=disabled%3Dfalse&count=-1 HTTP/1.0" 200 31930 - - - 4ms'''

            {
                "sourcetype": "sample_HEC",
                "source": "sample_source",
                "host": "sample_host",
            }

        Args:
            events (list): List of events (SampleEvent) to be ingested
            params (dict): dict with the info of the data to be ingested.

        """
        main_event = []
        param_list = []
        for event in events:
            event_dict = {
                "sourcetype": event.metadata.get('sourcetype', 'pytest_splunk_addon'),
                "source": event.metadata.get('source', 'pytest_splunk_addon:hec:raw'),
            }

            if event.metadata.get("host"):
                event_dict['host'] = event.metadata.get("host")

            param_list.append(event_dict)

            main_event.append(event.event)
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            _ = list(executor.map(self.__ingest, main_event, param_list))

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
            LOGGER.debug("Status code: {}".format(response.status_code))
            if response.status_code not in (200, 201):
                raise Exception("\nStatus code: {} \nReason: {} \ntext:{}".format(
                        response.status_code, response.reason, response.text
                    ))

        except Exception as e:
            LOGGER.error("\n\nAn error occurred while data ingestion.{}".format(e))
            raise type(e)("An error occurred while data ingestion.{}".format(e))
