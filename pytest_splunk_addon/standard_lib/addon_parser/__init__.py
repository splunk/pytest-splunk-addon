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
# -*- coding: utf-8 -*-
"""
The module provides the Add-on parsing mechanism. It can
parse the knowledge objects from an Add-on's configuration files

Supports: fields from props & transforms, tags, eventtypes
"""
import os
import re
import logging

from .fields import convert_to_fields, Field
from .transforms_parser import TransformsParser
from .props_parser import PropsParser
from .tags_parser import TagsParser
from .eventtype_parser import EventTypeParser
from .savedsearches_parser import SavedSearchParser

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
        self._props_parser = None
        self._tags_parser = None
        self._eventtype_parser = None
        self._savedsearch_parser = None

    @property
    def props_parser(self):
        if not self._props_parser:
            self._props_parser = PropsParser(self.splunk_app_path)
        return self._props_parser

    @property
    def tags_parser(self):
        if not self._tags_parser:
            self._tags_parser = TagsParser(self.splunk_app_path)
        return self._tags_parser

    @property
    def eventtype_parser(self):
        if not self._eventtype_parser:
            self._eventtype_parser = EventTypeParser(self.splunk_app_path)
        return self._eventtype_parser

    @property
    def savedsearch_parser(self):
        if not self._savedsearch_parser:
            self._savedsearch_parser = SavedSearchParser(self.splunk_app_path)
        return self._savedsearch_parser

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

    def get_savedsearches(self):
        """
        Parse the App configuration files & yield searchedservices

        Yields:
            generator of list of searchedservices
        """
        return self.savedsearch_parser.get_savedsearches()
