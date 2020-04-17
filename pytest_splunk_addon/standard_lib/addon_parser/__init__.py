# -*- coding: utf-8 -*-
"""
The module provides the Add-on parsing mechanism. It can
parse the knowledge objects from an Add-on's configuration files

Supports: fields from props & transforms, tags, eventtypes

Dependencies: 
    splunk_appinspect.App: To parse the configuration files 
"""
import os
import re
import logging
from splunk_appinspect import App

from .fields import convert_to_fields, Field
from .transforms_parser import TransformsParser
from .props_parser import PropsParser
from .tags_parser import TagsParser
from .eventtype_parser import EventTypeParser

LOGGER = logging.getLogger("pytest-splunk-addon")


class AddonParser(object):
    """
    Parse the knowledge objects from an Add-on's configuration files.
    Supports: fields from props & transforms, tags, eventtypes

    Args:
        splunk_app_path (str): Path to the Splunk App
    """
    def __init__(self, splunk_app_path):
        self.splunk_app_path = splunk_app_path
        LOGGER.info(f"Initializing the splunk_appinspect.App from path={splunk_app_path}")
        self.app = App(splunk_app_path, python_analyzer_enable=False)
        self.props_parser = PropsParser(self.splunk_app_path, self.app)
        self.tags_parser = TagsParser(self.splunk_app_path, self.app)
        self.eventtype_parser = EventTypeParser(self.splunk_app_path, self.app)

    def get_props_fields(self):
        """
        Parse the props.conf and yield all supported fields

        Yields:
            generator of all the supported fields 
        """
        return self.props_parser.get_props_fields()

    def get_tags(self):
        """
        Parse the tags.conf of the App & yield stanzas

        Yields:
            generator of stanzas from the tags
        """
        return self.tags_parser.get_tags()

    def get_eventtypes(self):
        """
        Parse the App configuration files & yield eventtypes
        
        Yields:
            generator of list of eventtypes
        """
        return self.eventtype_parser.get_eventtypes()
