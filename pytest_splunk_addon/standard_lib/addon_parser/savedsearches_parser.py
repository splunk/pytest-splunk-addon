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
Provides savedsearches.conf parsing mechanism
"""
from typing import Dict
from typing import Generator
from typing import Optional
import logging
import os

import addonfactory_splunk_conf_parser_lib as conf_parser

LOGGER = logging.getLogger("pytest-splunk-addon")


class SavedSearchParser(object):
    """
    Parses savedsearches.conf and extracts savedsearches

    Args:
        splunk_app_path (str): Path of the Splunk app
    """

    def __init__(self, splunk_app_path: str):
        self._conf_parser = conf_parser.TABConfigParser()
        self.splunk_app_path = splunk_app_path
        self._savedsearches = None

    @property
    def savedsearches(self) -> Optional[Dict]:
        if self._savedsearches is not None:
            return self._savedsearches
        savedsearches_conf_path = os.path.join(
            self.splunk_app_path, "default", "savedsearches.conf"
        )
        LOGGER.info("Parsing savedsearches.conf")
        self._conf_parser.read(savedsearches_conf_path)
        self._savedsearches = self._conf_parser.item_dict()
        return self._savedsearches if self._savedsearches else None

    def get_savedsearches(self) -> Optional[Generator]:
        """
        Parse the App configuration files & yield savedsearches

        Yields:
            generator of list of savedsearches
        """
        if not self.savedsearches:
            return None
        for stanza_key, stanza_values in self.savedsearches.items():
            LOGGER.info(f"Parsing savedsearches of stanza={stanza_key}")
            savedsearch_container = {
                "stanza": stanza_key,
                "search": 'index = "main"',
                "dispatch.earliest_time": "0",
                "dispatch.latest_time": "now",
            }
            empty_value = ["None", "", " "]
            for key, value in stanza_values.items():
                if key in ("search", "dispatch.earliest_time", "dispatch.latest_time"):
                    if value not in empty_value:
                        savedsearch_container[key] = value
            yield savedsearch_container
