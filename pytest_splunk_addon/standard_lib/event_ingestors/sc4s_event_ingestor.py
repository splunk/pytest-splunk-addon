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
import socket
from time import sleep
import os
import re
import concurrent.futures
from .base_event_ingestor import EventIngestor
import logging

LOGGER = logging.getLogger("pytest-splunk-addon")


class SC4SEventIngestor(EventIngestor):
    """
    Class to Ingest Events via SC4S

    The format for required_configs is::

        {
            sc4s_host (str): Address of the Splunk Server. Do not provide http scheme in the host.
            sc4s_port (int): Port number of the above host address
        }

    Args:
        required_configs (dict): Dictionary containing splunk host and sc4s port
    """

    def __init__(self, required_configs):
        self.sc4s_host = required_configs["sc4s_host"]
        self.sc4s_port = required_configs["sc4s_port"]
        self.server_address = (
            required_configs["sc4s_host"],
            required_configs["sc4s_port"],
        )

    def ingest(self, events, thread_count):
        """
        Ingests events in the splunk via sc4s (Single/Batch of Events)

        Args:
            events (list): Events with newline character or LineBreaker as separator

        """

        # This loop just checks for a viable remote connection
        tried = 0
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                sock.connect(self.server_address)
                break
            except Exception as e:
                tried += 1
                LOGGER.debug("Attempt {} to ingest data with SC4S".format(str(tried)))
                if tried > 90:
                    LOGGER.error(
                        "Failed to ingest event with SC4S {} times".format(str(tried))
                    )
                    raise e
                sleep(1)
            finally:
                sock.close()

        raw_events = list()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(self.server_address)
        for event in events:
            # raw_events.extend()
            for se in event.event.splitlines():
                try:
                    sock.sendall(str.encode(se + "\n"))
                except Exception as e:
                    LOGGER.debug("Attempt ingest data with SC4S=".format(se))
                    LOGGER.exception(e)
                    sleep(1)
        sock.close()
