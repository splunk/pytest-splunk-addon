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
"""
Provides eventtypes.conf parsing mechanism
"""
from typing import Dict
from typing import Generator
from typing import Optional
import logging
import os

import addonfactory_splunk_conf_parser_lib as conf_parser

LOGGER = logging.getLogger("pytest-splunk-addon")


class EventTypeParser(object):
    """
    Parses eventtypes.conf and extracts eventtypes

    Args:
        splunk_app_path (str): Path of the Splunk app
    """

    def __init__(self, splunk_app_path: str):
        self._conf_parser = conf_parser.TABConfigParser()
        self.splunk_app_path = splunk_app_path
        self._eventtypes = None

    @property
    def eventtypes(self) -> Optional[Dict]:
        if self._eventtypes is not None:
            return self._eventtypes
        eventtypes_conf_path = os.path.join(
            self.splunk_app_path, "default", "eventtypes.conf"
        )
        LOGGER.info("Parsing eventtypes.conf")
        self._conf_parser.read(eventtypes_conf_path)
        self._eventtypes = self._conf_parser.item_dict()
        return self._eventtypes if self._eventtypes else None

    def get_eventtypes(self) -> Optional[Generator]:
        """
        Parse the App configuration files & yield eventtypes

        Yields:
            generator of list of eventtypes
        """
        if not self.eventtypes:
            return None
        for stanza_key in self.eventtypes.keys():
            LOGGER.info("Parsing eventtype stanza=%s", stanza_key)
            yield {"stanza": stanza_key}
