#
# Copyright 2026 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from . import (
    HECEventIngestor,
    HECRawEventIngestor,
    HECMetricEventIngestor,
    SC4SEventIngestor,
    FileMonitorEventIngestor,
)
import logging
from ..sample_generation import SampleXdistGenerator

LOGGER = logging.getLogger("pytest-splunk-addon")


class IngestorHelper(object):
    """
    Module for helper methods for ingestors.
    """

    # Mapping of input types to their corresponding ingestor classes
    INGEST_METHODS = {
        "modinput": HECEventIngestor,
        "windows_input": HECEventIngestor,
        "file_monitor": HECRawEventIngestor,
        "uf_file_monitor": FileMonitorEventIngestor,
        "scripted_input": HECRawEventIngestor,
        "hec_metric": HECMetricEventIngestor,
        "syslog_tcp": SC4SEventIngestor,
        "syslog_udp": None,  # TBD
        "default": HECRawEventIngestor,
    }

    @classmethod
    def get_ep_compatible_input_types(cls):
        """
        Dynamically determine which input types are compatible with Splunk Edge Processor mode.
        
        Returns input types that use HECEventIngestor, which is the only ingestor that supports
        UUID via indexed fields parameter. This is required for EP mode because EP transforms
        events, making literal content matching unreliable.
        
        Returns:
            tuple: Input types that use HECEventIngestor
        """
        # Return input types that use HECEventIngestor
        return tuple(
            input_type 
            for input_type, ingestor_class in cls.INGEST_METHODS.items() 
            if ingestor_class is HECEventIngestor
        )

    @classmethod
    def get_event_ingestor(cls, input_type, ingest_meta_data):
        """
        Based on the input_type of the event, it returns an appropriate ingestor.

        Args:
            input_type (str): input_type defined in pytest-splunk-addon-data.conf
            ingest_meta_data (dict): Dictionary of required meta_data.
        """
        ingestor = cls.INGEST_METHODS.get(input_type)(ingest_meta_data)
        LOGGER.debug("Using the following HEC ingestor: {}".format(str(ingestor)))
        return ingestor

    @classmethod
    def get_consolidated_events(cls, events):
        ingestor_dict = dict()
        for event in events:
            input_type = event.metadata.get("input_type")
            if input_type in [
                "modinput",
                "windows_input",
                "syslog_tcp",
                "syslog_udp",
                "uf_file_monitor",
            ]:
                event.event = event.event.encode("utf-8").decode()
            else:
                event.event = event.event.encode("utf-8")
            if input_type in ingestor_dict:
                ingestor_dict[input_type].append(event)
            else:
                ingestor_dict[input_type] = [event]
        return ingestor_dict

    @classmethod
    def ingest_events(
        cls,
        ingest_meta_data,
        addon_path,
        config_path,
        thread_count,
        store_events,
    ):
        """
        Events are ingested in the splunk.
        Args:
            ingest_meta_data (dict): Dictionary of required meta_data.
            addon_path (str): Path to Splunk app package.
            config_path (str): Path to pytest-splunk-addon-data.conf
            thread_count (int): number of threads to use for ingestion
            store_events (bool): Boolean param for generating json files with tokenised events
        """
        splunk_ep = ingest_meta_data.get("splunk_ep", False)
        sample_generator = SampleXdistGenerator(addon_path, splunk_ep, config_path)
        store_sample = sample_generator.get_samples(store_events)
        tokenized_events = store_sample.get("tokenized_events")
        ingestor_dict = cls.get_consolidated_events(tokenized_events)
        for input_type, events in ingestor_dict.items():
            LOGGER.debug(
                "Received the following input type for HEC event: {}".format(input_type)
            )
            event_ingestor = cls.get_event_ingestor(input_type, ingest_meta_data)
            event_ingestor.ingest(events, thread_count)
