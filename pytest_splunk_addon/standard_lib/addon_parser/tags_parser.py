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
Provides tags.conf parsing mechanism
"""
import os
from typing import Optional, Dict, Generator
from urllib.parse import unquote
import logging

import addonfactory_splunk_conf_parser_lib as conf_parser

LOGGER = logging.getLogger("pytest-splunk-addon")


class TagsParser:
    """
    Parses tags.conf and extracts tags

    Args:
        splunk_app_path (str): Path of the Splunk app
    """

    def __init__(self, splunk_app_path: str):
        self._conf_parser = conf_parser.TABConfigParser()
        self.splunk_app_path = splunk_app_path
        self._tags = None

    @property
    def tags(self) -> Optional[Dict]:
        if self._tags is not None:
            return self._tags
        tags_conf_path = os.path.join(self.splunk_app_path, "default", "tags.conf")
        LOGGER.info("Parsing tags.conf")
        self._conf_parser.read(tags_conf_path)
        self._tags = self._conf_parser.item_dict()
        return self._tags if self._tags else None

    def get_tags(self) -> Optional[Generator]:
        """
        Parse the tags.conf of the App & yield stanzas

        Yields:
            generator of stanzas from the tags
        """
        if not self.tags:
            return
        for stanza_key, stanza_values in self.tags.items():
            LOGGER.info(f"Parsing tags of stanza={stanza_key}")
            stanza_key = stanza_key.replace("=", '="') + '"'
            stanza_key = unquote(stanza_key)
            LOGGER.debug(f"Parsed tags-stanza={stanza_key}")
            for key, value in stanza_values.items():
                LOGGER.info(f"Parsing tag={key} enabled={value} of stanza={stanza_key}")
                tag_container = {
                    "stanza": stanza_key,
                    "tag": key,
                    "enabled": True if value == "enabled" else False,
                }
                yield tag_container
