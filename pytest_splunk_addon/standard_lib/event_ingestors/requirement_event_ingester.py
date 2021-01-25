# ******* Input - requirement_log file, Transforms.conf of the addon Function:  parse and extract events from
# requirement files from path TA/requirement_files/abc.log Example
# TA_broken/requirement_files/sample_requirement_file.log
# Function:  Sourcetype the event before ingesting  to Splunk by using
# transforms.conf regex in config [Metadata: Sourcetype]

import requests
import logging
import os
import configparser, re
from xml.etree import cElementTree as ET
from ..sample_generation.sample_event import SampleEvent

LOGGER = logging.getLogger("pytest-splunk-addon")


class SrcRegex(object):
    def __init__(self):
        self.regex_src = None
        self.source_type = None


class RequirementEventIngestor(object):

    def __init__(self, app_path):
        """
        app_path to drill down to requirement file folder in package/tests/requirement_files/
        """
        self.app_path = app_path
        pass

    def check_xml_format(self, file_name):
        if ET.parse(file_name):
            return True
        else:
            return False

    def get_root(self, filename):
        """
        Input: Filename ending with .log extension
        Function to return raw event string
        """
        tree = ET.parse(filename)
        root = tree.getroot()
        return root

    def extract_raw_events(self, root):
        """
        This function returns raw events in <raw> section of the requirement files
        Iterate over all the requirement files and then send all the events to ingestor helper class
        Input: Root of the xml file
        Function to return raw event string
        """
        event = None
        for raw in root.iter('raw'):
            event = raw.text
        return event

    def extract_regex_transforms(self):
        """
        Requirement : app transform.conf
        Return: SrcRegex objects list containing pair of regex and sourcetype
        """
        parser = configparser.ConfigParser(interpolation=None)
        transforms_path = os.path.join(str(self.app_path), "default/transforms.conf")
        parser.read_file(open(transforms_path))
        list_src_regex = []
        for stanza in parser.sections():
            stanza_keys = list(parser[stanza].keys())
            obj = SrcRegex()
            if "dest_key" in stanza_keys:
                if str(parser[stanza]["dest_key"]) == "MetaData:Sourcetype":
                    for key in stanza_keys:
                        key_value = str(parser[stanza][key])
                        if key == "regex":
                            obj.regex_src = key_value
                        if key == "format":
                            obj.source_type = key_value
                    list_src_regex.append(obj)
        return list_src_regex

    def extract_sourcetype(self, list_src_regex, event):
        """
        Using app path extract sourcetype of the events
        From tranforms.conf [Metadata: Sourcetype] Regex
        This only works for syslog apps with this section
        Input: event, List of SrcRegex
        Return:Sourcetype of the event
        """
        sourcetype = None
        for regex_src_obj in list_src_regex:
            regex_match = re.search(regex_src_obj.regex_src, event)
            if regex_match:
                _, sourcetype = str(regex_src_obj.source_type).split('::', 1)
        return sourcetype

    def get_events(self):
        req_file_path = os.path.join(self.app_path, "requirement_files")
        src_regex = self.extract_regex_transforms()
        events = []
        if os.path.isdir(req_file_path):
            for file1 in os.listdir(req_file_path):
                filename = os.path.join(req_file_path, file1)
                if filename.endswith(".log"):
                    LOGGER.info(filename)
                    if self.check_xml_format(filename):
                        root = self.get_root(filename)
                        for event_tag in root.iter('event'):
                            unescaped_event = self.extract_raw_events(event_tag)
                            sourcetype = self.extract_sourcetype(src_regex, unescaped_event)
                            metadata = {'input_type': 'default',
                                        'sourcetype': sourcetype,
                                        'index': 'main'
                                        }
                            events.append(SampleEvent(unescaped_event, metadata, "requirement_test"))
                        return events
