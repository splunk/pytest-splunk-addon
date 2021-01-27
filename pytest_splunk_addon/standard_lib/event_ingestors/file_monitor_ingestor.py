from .base_event_ingestor import EventIngestor
import requests
import logging
import os
from time import sleep

LOGGER = logging.getLogger("pytest-splunk-addon")
MONITOR_DIR = "uf_files"

class FileMonitorEventIngestor(EventIngestor):
    """
    Class to ingest event via File monitor
    This ingestor will only work if splunk_type is docker and container of universal forwarder is linked with container 
    of splunk instance as 'splunk' service.

    The format for required_configs is::

        {
            uf_host: Host of universal forwarder
            uf_port: Management port of universal forwarder
            uf_username: Name of user for universal forwarder
            uf_password: Password of universal forwarder
        }

    Args:
        required_configs (dict): Dictionary containing information about universal forwarder

    """
    def __init__(self, required_configs):
        self.uf_host = required_configs.get("uf_host")
        self.uf_port = required_configs.get("uf_port")
        self.uf_username = required_configs.get("uf_username")
        self.uf_password = required_configs.get("uf_password")
        # Container of universal forwarder is linked with splunk instance.
        # So using splunk_host as splunk and port 9997 directly.
        self.splunk_host = "splunk"
        self.splunk_s2s_port = "9997"
        self.uf_rest_uri = "https://{}:{}".format(self.uf_host, self.uf_port)
        self.outputs_endpoint = "{}/services/data/outputs/tcp/group".format(self.uf_rest_uri)
        self.inputs_endpoint = "{}/servicesNS/nobody/search/data/inputs/monitor".format(self.uf_rest_uri)

    def ingest(self, events, thread_count):
        """
        Ingests data into splunk via file monitor. 
        """
        self.create_output_conf()
        for each_event in events:
            self.create_event_file(each_event)
            sleep(10)
            self.create_inputs_stanza(each_event)

    def create_output_conf(self):
        """
        Create stanza in outputs.conf file of universal forwarder to send on splunk(indexer).  
        """
        tcp_out_dict = {"name":"uf_monitor", "servers":"{}:{}".format(self.splunk_host, self.splunk_s2s_port)}
        response = requests.post(self.outputs_endpoint, tcp_out_dict, auth=(self.uf_username, self.uf_password), verify=False)
        if response.status_code not in (200, 201):
            LOGGER.warning("Unable to create stanza in outputs.conf\nStatus code: {} \nReason: {} \ntext:{}".format(response.status_code, response.reason, response.text))

    def create_event_file(self, event):
        """
        Write each tokenized event in files with host name as name of file. The host of all events will be unique.
        """
        try:
            with open(self.get_file_path(event), "w+") as fp:
                fp.write(event.event)
        except Exception as e:
            LOGGER.warning("Unable to create event file for host : {}, Reason : {}".format(event.metadata.get("host")), e)

    def create_inputs_stanza(self, event):
        """
        Create stanza in inputs.conf on universal forwarder for each tokenized event. 
        """
        file_path = self.get_file_path(event)
        sourcetype = event.metadata.get("sourcetype")
        if not sourcetype:
            sourcetype = event.metadata.get("sourcetype_to_search", "pytest_splunk_addon")
        stanza = {
            "name": file_path,
            "sourcetype": sourcetype,
            "index": event.metadata.get("index", "main"),
            "disabled": False,
            "crc-salt": "<SOURCE>"
        }
        if event.metadata.get("host_type") in ("plugin"):
            stanza["host"] = event.metadata.get("host")
        if event.metadata.get("source"):
            stanza["rename-source"] = event.metadata.get("source")
        response = requests.post(self.inputs_endpoint, stanza, auth=(self.uf_username, self.uf_password), verify=False)
        if response.status_code not in (200, 201):
            LOGGER.warning("Unable to add stanza in inputs.conf\nStatus code: {} \nReason: {} \ntext:{}".format(response.status_code, response.reason, response.text))

    def get_file_path(self, event):
        """
        Returns absolute path for tokenized events.
        """
        return "{}/{}/{}".format(os.getcwd(), MONITOR_DIR, event.metadata.get("host"))
