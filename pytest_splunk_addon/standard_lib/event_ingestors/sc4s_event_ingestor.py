import socket
from time import sleep
import os
import re
import concurrent.futures
from .base_event_ingestor import EventIngestor


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
        self.sc4s_host = required_configs['sc4s_host']
        self.sc4s_port = required_configs['sc4s_port']
        self.server_address = (required_configs['sc4s_host'], required_configs['sc4s_port'])

    def ingest(self, events, thread_count):
        """
        Ingests events in the splunk via sc4s (Single/Batch of Events)

        Args:
            events (list): Events with newline character or LineBreaker as separator

        """
        raw_events = list()
        for event in events:
            raw_events.extend(event.event.splitlines())

        with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
            _ = list(executor.map(self.ingest_event, raw_events))

    def ingest_event(self, event):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)        
        tried = 0
        while True:
            try:
                sock.connect(self.server_address)
                break
            except Exception as e:
                tried += 1
                if tried > 90:
                    raise e
                sleep(1)
        #sendall sends the entire buffer you pass or throws an exception.
        sock.sendall(str.encode(event))
