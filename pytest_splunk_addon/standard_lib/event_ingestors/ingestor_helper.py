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
from .requirement_event_ingester import RequirementEventIngestor


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
            "uf_file_monitor": FileMonitorEventIngestor,
            "scripted_input": HECRawEventIngestor,
            "hec_metric": HECMetricEventIngestor,
            "syslog_tcp": SC4SEventIngestor,
            "syslog_udp": None,  # TBD
            "default": HECRawEventIngestor,
        }

        ingestor = ingest_methods.get(input_type)(ingest_meta_data)
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
        run_requirement_test,
    ):
        """
        Events are ingested in the splunk.
        Args:
            ingest_meta_data(dict): Dictionary of required meta_data.
            addon_path: Path to Splunk app package.
            config_path: Path to pytest-splunk-addon-sample-generator.conf.
            bulk_event_ingestion(bool): Boolean param for bulk event ingestion.
            run_requirement_test(bool) :Boolean to identify if we want to run the requirement tests
        """
        sample_generator = SampleXdistGenerator(addon_path, config_path)
        store_sample = sample_generator.get_samples(store_events)
        tokenized_events = store_sample.get("tokenized_events")
        ingestor_dict = cls.get_consolidated_events(tokenized_events)
        for input_type, events in ingestor_dict.items():
            LOGGER.debug(
                "Received the following input type for HEC event: {}".format(input_type)
            )
            event_ingestor = cls.get_event_ingestor(input_type, ingest_meta_data)
            event_ingestor.ingest(events, thread_count)

        if run_requirement_test != "None":
            requirement_events = RequirementEventIngestor(run_requirement_test)
            requirement_events_get = requirement_events.get_events()
            requirement_events_dict = cls.get_consolidated_events(
                requirement_events_get
            )
            for input_type, events in requirement_events_dict.items():
                LOGGER.debug(
                    "Received the following input type for HEC event: {}".format(
                        input_type
                    )
                )
                event_ingestor = cls.get_event_ingestor(input_type, ingest_meta_data)
                event_ingestor.ingest(events, thread_count)
            LOGGER.info("Ingestion Done")
