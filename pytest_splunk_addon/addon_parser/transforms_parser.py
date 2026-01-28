#
# Copyright 2026 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""
Provides transforms.conf parsing mechanism
"""
from typing import Dict
from typing import Generator
from typing import Optional
import logging
import re
import os
import csv

import addonfactory_splunk_conf_parser_lib as conf_parser

LOGGER = logging.getLogger("pytest-splunk-addon")

from . import convert_to_fields
from .parser_cache import ParserCache


class TransformsParser(object):
    """
    Parses transforms.conf and extracts fields

    Args:
        splunk_app_path (str): Path of the Splunk app
    """

    def __init__(self, splunk_app_path: str, transforms_data: Optional[Dict] = None):
        self._conf_parser = conf_parser.TABConfigParser()
        self.splunk_app_path = splunk_app_path
        self._transforms = transforms_data
        self._parser_cache = ParserCache()

    @property
    def transforms(self) -> Optional[Dict]:
        if self._transforms is not None:
            return self._transforms

        def _parse_transforms():
            transforms_conf_path = os.path.join(
                self.splunk_app_path, "default", "transforms.conf"
            )
            LOGGER.info("Parsing transforms.conf")
            self._conf_parser.read(transforms_conf_path)
            return self._conf_parser.item_dict()

        self._transforms = self._parser_cache.get_or_parse(
            _parse_transforms, "transforms"
        )
        return self._transforms if self._transforms else None

    @convert_to_fields
    def get_transform_fields(self, transforms_stanza: str) -> Optional[Generator]:
        """
        Parse the transforms.conf of the App & yield fields of
        a specific stanza.

        Supported extractions from transforms.conf are

        * SOURCE_KEY = _raw
        * REGEX = some regex with (capturing_group)
        * FIELDS = one,

        Args:
            transforms_stanza (str):
                The stanza of which the fields should be extracted

        Regex:
            Parse the fields from a regex. Examples::

                (?<name>regex)
                (?'name'regex)
                (?P<name>regex)

        Yields:
            generator of fields
        """

        try:
            if not self.transforms:
                return
            transforms_values = self.transforms[transforms_stanza]
            if "SOURCE_KEY" in transforms_values:
                LOGGER.info(f"Parsing source_key of {transforms_stanza}")
                yield transforms_values["SOURCE_KEY"]
            if "REGEX" in transforms_values:
                LOGGER.info(f"Parsing REGEX of {transforms_stanza}")

                regex = r"\(\?P?[<'](?!_KEY|_VAL)([A-Za-z0-9_]+)[>']"
                match_fields = re.findall(regex, transforms_values["REGEX"])
                for each_field in match_fields:
                    if not each_field.startswith(("_KEY_", "_VAL_")):
                        yield each_field.strip()
            if "FIELDS" in transforms_values:
                LOGGER.info(f"Parsing FIELDS of {transforms_stanza}")
                fields_values = transforms_values["FIELDS"]
                for each_field in fields_values.split(","):
                    yield each_field.strip()
            if "FORMAT" in transforms_values:
                LOGGER.info(f"Parsing FORMAT of {transforms_stanza}")
                regex = r"(\S*)::"
                match_fields = re.findall(regex, transforms_values["FORMAT"])
                for each_field in match_fields:
                    if "$" not in each_field:
                        yield each_field.strip()
        except KeyError:
            LOGGER.error(
                f"The stanza {transforms_stanza} does not exists in transforms.conf."
            )

    def get_lookup_csv_fields(self, lookup_stanza: str) -> Optional[Generator]:
        """
        Parse the fields from a lookup file for a specific lookup_stanza

        Args:
            lookup_stanza (str): A lookup stanza mentioned in transforms.conf

        Yields:
            string of field names
        """
        if not self.transforms:
            return
        if lookup_stanza in self.transforms.keys():
            stanza_values = self.transforms[lookup_stanza]
            if "filename" in stanza_values:
                lookup_file = stanza_values["filename"]
                try:
                    location = os.path.join(
                        self.splunk_app_path, "lookups", lookup_file
                    )
                    with open(location) as csv_file:
                        reader = csv.DictReader(csv_file)
                        fieldnames = reader.fieldnames
                        for items in fieldnames:
                            yield items.strip()
                # If there is an error. the test should fail with the current fields
                # This makes sure the test doesn't exit prematurely
                except (OSError, IOError, UnboundLocalError, TypeError) as e:
                    LOGGER.error(
                        "Could not read the lookup file, skipping test. error=%s",
                        str(e),
                    )

    def get_sourcetype_from_transform(self, transform_stanza: str) -> Optional[str]:
        """
        Extract sourcetype from a transform stanza's FORMAT field.

        Looks for FORMAT field with pattern: sourcetype::<sourcetype_name>

        Args:
            transform_stanza (str): Name of the transform stanza in transforms.conf

        Returns:
            Extracted sourcetype name or None if not found

        Example:
            If transforms.conf has:
            [gcp_pubsub_activity_sourcetype]
            FORMAT = sourcetype::google:gcp:pubsub:audit:admin_activity

            Then get_sourcetype_from_transform("gcp_pubsub_activity_sourcetype")
            returns "google:gcp:pubsub:audit:admin_activity"
        """
        if not self.transforms:
            return None

        try:
            transforms_values = self.transforms[transform_stanza]
            if "FORMAT" not in transforms_values:
                return None

            format_value = transforms_values["FORMAT"]
            
            # Skip if format contains $ variables (like $1, $2, etc.)
            if '$' in format_value:
                LOGGER.debug(
                    "Skipping transform %s: FORMAT contains variables (%s)",
                    transform_stanza,
                    format_value,
                )
                return None
            
            # Match pattern: sourcetype::<sourcetype_name>
            # Case-insensitive, handles whitespace, handles quoted values
            regex = r"(?i)sourcetype\s*::\s*([^\s]+)"
            match = re.search(regex, format_value)

            if match:
                sourcetype = match.group(1).strip()
                # Remove quotes if present
                sourcetype = sourcetype.strip("\"'")
                LOGGER.debug(
                    "Extracted sourcetype %s from transform %s",
                    sourcetype,
                    transform_stanza,
                )
                return sourcetype

            return None
        except KeyError:
            LOGGER.warning(
                "Transform stanza %s not found in transforms.conf", transform_stanza
            )
            return None
        except Exception as e:
            LOGGER.warning(
                "Error extracting sourcetype from transform %s: %s",
                transform_stanza,
                str(e),
            )
            return None
