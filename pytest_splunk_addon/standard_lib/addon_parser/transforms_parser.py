# -*- coding: utf-8 -*-
"""
Provides transforms.conf parsing mechanism
"""
import logging
import re
import os
import csv 
from urllib.parse import unquote
LOGGER = logging.getLogger("pytest-splunk-addon")

from . import convert_to_fields

class TransformsParser(object):
    """
    Parses transforms.conf and extracts fields 

    Args:
        splunk_app_path (str): Path of the Splunk app
        app (splunk_appinspect.App): Object of Splunk app
    """
    def __init__(self, splunk_app_path, app):
        self.app = app 
        self.splunk_app_path = splunk_app_path
        self._transforms = None

    @property
    def transforms(self):
        try:
            if not self._transforms:
                LOGGER.info("Parsing transforms.conf")
                self._transforms = self.app.transforms_conf()
            return self._transforms
        except OSError:
            LOGGER.warning("transforms.conf not found.")
            return None

    @convert_to_fields
    def get_transform_fields(self, transforms_stanza):
        """
        Parse the tranforms.conf of the App & yield fields of 
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
            transforms_section = self.transforms.sects[transforms_stanza]
            if "SOURCE_KEY" in transforms_section.options:
                LOGGER.info("Parsing source_key of %s", transforms_stanza)
                yield transforms_section.options["SOURCE_KEY"].value

            if "REGEX" in transforms_section.options:
                LOGGER.info("Parsing REGEX of %s", transforms_stanza)

                regex = r"\(\?P?(?:[<'])([^\>'\s]+)[\>']"
                match_fields = re.findall(regex, transforms_section.options["REGEX"].value)
                for each_field in match_fields:
                    if not each_field.startswith(("_KEY_", "_VAL_")):
                        yield each_field.strip()

            if "FIELDS" in transforms_section.options:
                LOGGER.info("Parsing FIELDS of %s", transforms_stanza)
                for each_field in transforms_section.options["FIELDS"].value.split(","):
                    yield each_field.strip()

            if "FORMAT" in transforms_section.options:
                LOGGER.info("Parsing FORMAT of %s", transforms_stanza)
                regex = r"(\S*)::"
                match_fields = re.findall(regex, transforms_section.options["FORMAT"].value)
                for each_field in match_fields:
                    if not "$" in each_field:
                        yield each_field.strip()

        except KeyError:
            LOGGER.error(
                "The stanza {} does not exists in transforms.conf.".format(
                    transforms_stanza
                ),
            )

    def get_lookup_csv_fields(self, lookup_stanza):
        """
        Parse the fields from a lookup file for a specific lookup_stanza

        Args:
            lookup_stanza (str): A lookup stanza mentioned in transforms.conf
        
        Yields:
            string of field names  
        """
        if not self.transforms:
            return
        if lookup_stanza in self.transforms.sects:
            stanza = self.transforms.sects[lookup_stanza]
            if "filename" in stanza.options:
                lookup_file = stanza.options["filename"].value
                try:
                    location = os.path.join(
                        self.splunk_app_path, "lookups", lookup_file
                    )
                    with open(location, "r") as csv_file:
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
