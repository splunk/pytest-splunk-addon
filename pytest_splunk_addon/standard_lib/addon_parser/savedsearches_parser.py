# -*- coding: utf-8 -*-
"""
Provides savedsearches.conf parsing mechanism
"""


class SavedSearchParser(object):
    """
    Parses savedsearches.conf and extracts savedsearches

    Args:
        splunk_app_path (str): Path of the Splunk app
        app (splunk_appinspect.App): Object of Splunk app
    """

    def __init__(self, splunk_app_path, app):
        self.app = app
        self.splunk_app_path = splunk_app_path
        self._savedsearches = None

    @property
    def savedsearches(self):
        try:
            if not self._savedsearches:
                self._savedsearches = self.app.get_config("savedsearches.conf")
            return self._savedsearches
        except OSError:
            return None

    def get_savedsearches(self):
        """
        Parse the App configuration files & yield savedsearches

        Yields:
            generator of list of savedsearches
        """
        if not self.savedsearches:
            return None
        for stanza in self.savedsearches.sects:
            savedsearch_sections = self.savedsearches.sects[stanza]
            savedsearch_container = {
                "stanza": stanza,
                "search": 'index = "main"',
                "dispatch.earliest_time": "0",
                "dispatch.latest_time": "now",
            }
            for key in savedsearch_sections.options:
                empty_value = ["None", "", " "]
                if (
                    key == "search"
                    and savedsearch_sections.options[key].value not in empty_value
                ):
                    savedsearch_container[key] = savedsearch_sections.options[key].value
                elif (
                    key == "dispatch.earliest_time"
                    and savedsearch_sections.options[key].value not in empty_value
                ):
                    savedsearch_container[key] = savedsearch_sections.options[key].value
                elif (
                    key == "dispatch.latest_time"
                    and savedsearch_sections.options[key].value not in empty_value
                ):
                    savedsearch_container[key] = savedsearch_sections.options[key].value
            yield savedsearch_container
