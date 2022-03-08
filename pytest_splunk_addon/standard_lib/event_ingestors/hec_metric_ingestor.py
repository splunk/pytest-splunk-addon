#
# Copyright 2021 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""
HEC Event Ingestor class for Metric data.
Indextime tests of Metric data will be covered in upcoming versions of the plugin. It is not supported in current version.
"""
from .base_event_ingestor import EventIngestor
import requests
import time
import logging

requests.urllib3.disable_warnings()
import os

LOGGER = logging.getLogger("pytest-splunk-addon")


class HECMetricEventIngestor(EventIngestor):
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
        self.hec_uri = required_configs.get("splunk_hec_uri")
        self.session_headers = required_configs.get("session_headers")

    def ingest(self, data, thread_count):
        """
        Ingests event and metric data into splunk using HEC token via event endpoint.
        Args:
            data(dict): data dict with the info of the data to be ingested.

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
                        "event": "metric"
                        "index": "metric_index"
                        "fields":{
                            "metric_name": "metric1",
                            "_value": 1,
                        }
                    },
                    {
                        "sourcetype": "sample_HEC",
                        "source": "sample_source",
                        "host": "sample_host",
                        "event": "metric"
                        "index": "metric_index"
                        "fields":{
                            "metric_name": "metric1",
                            "_value": 2,
                        }
                    }
                ]
        """
        try:
            LOGGER.info(
                "Making a HEC event request with the following params:\nhec_uri:{}\nheaders:{}".format(
                    str(self.hec_uri), str(self.session_headers)
                )
            )
            LOGGER.debug(
                "Creating the following sample event to be ingested via HEC event endoipnt:{}".format(
                    str(data)
                )
            )
            response = requests.post(  # nosemgrep: splunk.disabled-cert-validation
                self.hec_uri,
                auth=None,
                json=data,
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
            raise type(e)("An error occurred while data ingestion.{}".format(e))
