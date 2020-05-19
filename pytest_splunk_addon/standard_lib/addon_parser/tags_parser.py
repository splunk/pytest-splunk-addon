# -*- coding: utf-8 -*-
"""
Provides tags.conf parsing mechanism
"""
from urllib.parse import unquote
import logging
LOGGER = logging.getLogger("pytest-splunk-addon")

class TagsParser(object):
    """
    Parses tags.conf and extracts tags 

    Args:
        splunk_app_path (str): Path of the Splunk app
        app (splunk_appinspect.App): Object of Splunk app
    """
    def __init__(self, splunk_app_path, app):
        self.app = app 
        self.splunk_app_path = splunk_app_path
        self._tags = None

    @property
    def tags(self):
        try:
            if not self._tags:
                LOGGER.info("Parsing tags.conf")
                self._tags = self.app.get_config("tags.conf")
            return self._tags
        except OSError:
            LOGGER.warning("tags.conf not found.")
            return None

    def get_tags(self):
        """
        Parse the tags.conf of the App & yield stanzas

        Yields:
            generator of stanzas from the tags
        """
        if not self.tags:
            return
        for stanza in self.tags.sects:
            LOGGER.info(f"Parsing tags of stanza={stanza}")
            tag_sections = self.tags.sects[stanza]
            stanza = stanza.replace("=", '="') + '"'
            stanza = unquote(stanza)
            LOGGER.debug(f"Parsed tags-stanza={stanza}")
            for key in tag_sections.options:
                tags_property = tag_sections.options[key]
                LOGGER.info("Parsing tag=%s enabled=%s of stanza=%s ",
                    tags_property.name, tags_property.value, stanza
                )
                tag_container = {
                    "stanza": stanza,
                    "tag": tags_property.name,
                    # "enabled": True or False
                }
                if tags_property.value == "enabled":
                    tag_container["enabled"] = True
                else:
                    tag_container["enabled"]= False
                yield tag_container
