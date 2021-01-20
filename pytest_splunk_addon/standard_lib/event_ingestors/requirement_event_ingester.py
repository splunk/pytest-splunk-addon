# ******* Input - requirement_log file, Transforms.conf of the addon Function:  parse and extract events from
# requirement files from path TA/requirement_files/abc.log Example
# TA_broken/requirement_files/sample_requirement_file.log
# Function:  Sourcetype the event before ingesting  to Splunk by using
# transforms.conf regex in config [Metadata: Sourcetype]

import requests
import logging
import os
from xml.etree import cElementTree as ET
from ..sample_generation.sample_event import SampleEvent

LOGGER = logging.getLogger("pytest-splunk-addon")


class RequirementEventIngestor(object):

    def __init__(self, app_path):
        """
        app_path to drill down to requirement file folder in package/tests/requirement_files/
        """
        self.app_path = app_path
        pass

    def extract_raw_events(self):
        """
        This function returns raw events in <raw> section of the requirement files
        Iterate over all the requirement files and then send all the events to ingestor helper class
        """
        pass

    def extract_sourcetype(self):
        """
        Using app path extract sourcetype of the events
        From tranforms.conf [Metadata: Sourcetype] Regex
        This only works for syslog apps with this section
        """
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

    def get_event(self, root):
        """
        Input: Root of the xml file
        Function to return raw event string
        """
        event = None
        for raw in root.iter('raw'):
            event = raw.text
        return event

    def get_events(self):
        req_file_path = os.path.join(self.app_path, "requirement_files")
        if os.path.isdir(req_file_path):
            for file1 in os.listdir(req_file_path):
                filename = os.path.join(req_file_path, file1)
                if filename.endswith(".log"):
                    LOGGER.info(filename)
                    if self.check_xml_format(filename):
                        LOGGER.info("XML check")
                        root = self.get_root(filename)
                        for event_tag in root.iter('event'):
                            unescaped_event = self.get_event(event_tag)
                            LOGGER.info("before return")
                            metadata ={'input_type': 'default',
                                      'sourcetype': 'sourcetype::juniper:idp',
                                        'index' : 'main'
                                     }
                            e = SampleEvent(unescaped_event,metadata, "requirement_test" )

                            return [e]
                            """
        Send Sourcetyped events to event ingestor
        """
        pass


