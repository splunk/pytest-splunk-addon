from .base_event_ingestor import EventIngestor
import requests
import logging
import os
from time import sleep

LOGGER = logging.getLogger("pytest-splunk-addon")
MONITOR_DIR = "uf_files"

class FileMonitorEventIngestor(EventIngestor):
    
    def __init__(self, required_configs):
        self.uf_host = required_configs.get("uf_host")
        self.uf_port = required_configs.get("uf_port")
        self.uf_username = required_configs.get("uf_username")
        self.uf_password = required_configs.get("uf_password")
        self.splunk_host = required_configs.get("splunk_host")
        self.splunk_s2s_port = required_configs.get("splunk_s2s_port")
        self.uf_rest_uri = "https://{}:{}".format(self.uf_host, self.uf_port)
        self.outputs_endpoint = "{}/services/data/outputs/tcp/group".format(self.uf_rest_uri)
        self.inputs_endpoint = "{}/servicesNS/nobody/search/data/inputs/monitor".format(self.uf_rest_uri)

    def ingest(self, events, thread_count):
        self.create_output_conf()
        self.create_file_monitor_dir()
        for each_event in events:
            self.create_file(each_event)
            sleep(5)
            self.create_inputs_stanza(each_event)

    def create_output_conf(self):
        tcp_out_dict = {"name":"uf_monitor", "servers":"{}:{}".format(self.splunk_host, self.splunk_s2s_port)}
        response = requests.post(self.outputs_endpoint, tcp_out_dict, auth=(self.uf_username, self.uf_password), verify=False)
        if response not in (200, 201):
            print(response._content)

    def create_file_monitor_dir(self):
        monitor_dir = os.path.join(os.getcwd(), MONITOR_DIR)
        if not os.path.exists(monitor_dir):
            os.mkdir(monitor_dir)

    def create_file(self, event):
        with open(self.get_file_path(event), "w+") as fp:
            fp.write(event.event)

    def create_inputs_stanza(self, event):
        file_path = self.get_file_path(event)
        stanza = {
            "name": file_path,
            "sourcetype": event.metadata.get("sourcetype_to_search", "pytest_splunk_addon"),
            "index": event.metadata.get("index", "main"),
            "disabled": False
        }
        if event.metadata.get("host_type") in ("plugin"):
            stanza["host"] = event.metadata.get("host")
        response = requests.post(self.inputs_endpoint, stanza, auth=(self.uf_username, self.uf_password), verify=False)
        if response not in (200, 201):
            print(response._content)

    def get_file_path(self, event):
        return "{}/{}/{}".format(os.getcwd(), MONITOR_DIR, event.metadata.get("host"))
