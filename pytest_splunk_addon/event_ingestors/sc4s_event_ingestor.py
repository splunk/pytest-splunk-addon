#
# Copyright 2025 Splunk Inc.
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
import socket
from time import sleep
import logging

from typing import Dict

from .base_event_ingestor import EventIngestor

LOGGER = logging.getLogger("pytest-splunk-addon")


class SC4SEventIngestor(EventIngestor):
    """
    Class to ingest events via SC4S (supports both IPv4 and IPv6)

    Args:
        required_configs (dict): Dictionary containing splunk host and sc4s port
    """

    def __init__(self, required_configs: Dict[str, str]) -> None:
        self.sc4s_host = required_configs["sc4s_host"]
        self.sc4s_port = required_configs["sc4s_port"]

    def _create_socket(self):
        """Try all addresses (IPv4 and IPv6) and return a connected socket."""
        last_exc = None
        for res in socket.getaddrinfo(
            self.sc4s_host, self.sc4s_port, socket.AF_UNSPEC, socket.SOCK_STREAM
        ):
            af, socktype, proto, _, sa = res
            try:
                sock = socket.socket(af, socktype, proto)
                if af == socket.AF_INET6:
                    # Attempt dual-stack if supported
                    try:
                        sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
                    except (AttributeError, OSError):
                        pass
                sock.connect(sa)
                return sock
            except Exception as e:
                last_exc = e
                LOGGER.debug(f"Failed to connect to {sa}: {e}")
                try:
                    sock.close()
                except Exception:
                    pass
                continue
        raise ConnectionError(
            f"Could not connect to SC4S at {self.sc4s_host}:{self.sc4s_port} via IPv4 or IPv6"
        ) from last_exc

    def ingest(self, events, thread_count):
        """
        Ingests events in Splunk via SC4S (single/batch of events)

        Args:
            events (list): Events with newline character or LineBreaker as separator
        """

        # Retry loop to establish connection
        tried = 0
        while True:
            try:
                sock = self._create_socket()
                break
            except Exception as e:
                tried += 1
                LOGGER.debug(f"Attempt {tried} to ingest data with SC4S")
                if tried > 90:
                    LOGGER.error(f"Failed to ingest event with SC4S {tried} times")
                    raise e
                sleep(1)

        # Send events
        try:
            for event in events:
                for se in event.event.splitlines():
                    try:
                        sock.sendall(str.encode(se + "\n"))
                    except Exception as e:
                        LOGGER.debug(f"Attempt ingest data with SC4S: {se}")
                        LOGGER.exception(e)
                        sleep(1)
        finally:
            sock.close()
