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
Provides eventtypes.conf parsing mechanism
"""
import logging

LOGGER = logging.getLogger("pytest-splunk-addon")


class EventTypeParser(object):
    """
    Parses eventtypes.conf and extracts eventtypes

    Args:
        splunk_app_path (str): Path of the Splunk app
        app (splunk_appinspect.App): Object of Splunk app
    """

    def __init__(self, splunk_app_path, app):
        self.app = app
        self.splunk_app_path = splunk_app_path
        self._eventtypes = None

    @property
    def eventtypes(self):
        try:
            if not self._eventtypes:
                LOGGER.info("Parsing eventtypes.conf")
                self._eventtypes = self.app.eventtypes_conf()
            return self._eventtypes
        except OSError:
            LOGGER.warning("eventtypes.conf not found.")
            return None

    def get_eventtypes(self):
        """
        Parse the App configuration files & yield eventtypes

        Yields:
            generator of list of eventtypes
        """
        if not self.eventtypes:
            return None
        for eventtype_section in self.eventtypes.sects:
            LOGGER.info("Parsing eventtype stanza=%s", eventtype_section)
            yield {"stanza": eventtype_section}
