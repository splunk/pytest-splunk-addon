"""
HEC Event Ingestor class
"""
from base_event_ingestor import EventIngestor
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
            hec_uri(str): {splunk_hec_scheme}://{splunk_host}:{hec_port}/services/collector
            session_headers(dict): requesr header info.

            format::
                {
                    "Authorization": f"Splunk <hec-token>",
                }
        """
        self.hec_uri = hec_uri
        self.session_headers = session_headers

    def ingest_at_raw(self, event_str, params):
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
            self.__check_resp_status(response)

        except Exception as e:
            print(e)

    def ingest(self, data):
        """
        Ingests event and metric data into splunk using HEC token via event endpoint.
        Args:
            is_metric_data(boolean): If True data is metric data .
            data(dict): data dict with the info of the data to be ingested.

            format::
                {
                    "sourcetype": "sample_HEC",
                    "source": "sample_source",
                    "host": "sample_host",
                    "event": "event_str"
                }

            Metric Data format::
                {
                    "sourcetype": "sample_HEC",
                    "source": "sample_source",
                    "host": "sample_host",
                    "event": "metric"
                    "index": "metric_index"
                    "fields":{
                        "metric_name": "metric1",
                        "_value": 1,
                    }
                }

            For batch ingestion of events in a single request at event endpoint provide a list of event dict to be ingested.
            format::
                [ 
                    {
                        "sourcetype": "sample_HEC",
                        "source": "sample_source",
                        "host": "sample_host",
                        "event": "event_str1"
                    },
                    {
                        "sourcetype": "sample_HEC",
                        "source": "sample_source",
                        "host": "sample_host",
                        "event": "metric"
                        "index": "metric_index"
                        "fields":{
                            "metric_name": "metric1",
                            "_value": 1,
                        }
                    }
                ]
        """
        try:
            response = requests.post(
                "{}/{}".format(self.hec_uri, "event"),
                auth=None,
                json=data,
                headers=self.session_headers,
                verify=False,
            )
            self.__check_resp_status(response)

        except Exception as e:
            print(e)

    def __check_resp_status(self, response):
        """
        Raises an exception if status code is not 200 or 201
        """
        if response.status_code not in (200, 201):
            print(
                "Status code: {} \nReason: {} \ntext:{}".format(
                    response.status_code, response.reason, response.text
                )
            )
            raise Exception
