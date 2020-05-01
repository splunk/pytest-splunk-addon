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
        self._app = None
        self._props_parser = None
        self._tags_parser = None
        self._eventtype_parser = None

    @property
    def app(self):
        if not self._app:
            self._app = App(self.splunk_app_path, python_analyzer_enable=False)
        return self._app

    @property
    def props_parser(self):
        if not self._props_parser:
            self._props_parser = PropsParser(self.splunk_app_path, self.app)
        return self._props_parser

    @property
    def tags_parser(self):
        if not self._tags_parser:
            self._tags_parser = TagsParser(self.splunk_app_path, self.app)
        return self._tags_parser

    @property
    def eventtype_parser(self):
        if not self._eventtype_parser:
            self._eventtype_parser = EventTypeParser(self.splunk_app_path, self.app)
        return self._eventtype_parser

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
