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
            LOGGER.info("Parsing eventtype stanza=%s",
                eventtype_section
            )
            yield {
                "stanza": eventtype_section
            }
