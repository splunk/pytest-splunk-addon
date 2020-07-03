import os
import re
import logging
from splunk_appinspect import App

from .rule import Rule
from . import SampleStanza

LOGGER = logging.getLogger("pytest-splunk-addon")
import warnings


class EventgenParser:
    """
    This class represents the entire eventgen.conf file and handles parsing mechanism of eventgen and the rules
    """
    splunk_test_type = " "

    def __init__(self, addon_path, config_path=None):
        """
        init method for the class
    
        Args:
            addon_path(str): Path to the addon 
        """
        self._app = App(addon_path, python_analyzer_enable=False)
        self.config_path = config_path 
        self._eventgen = None
        self.addon_path = addon_path
        self.path_to_samples = os.path.join(addon_path, "samples")
        self.match_stanzas = set()

    @property
    def eventgen(self):
        try:
            relative_path = os.path.relpath(self.config_path, self.addon_path)
            if os.path.exists(os.path.join(self.config_path, "pytest-splunk-addon-data-generator.conf")):
                self._eventgen = self._app.get_config("pytest-splunk-addon-data-generator.conf", dir=relative_path)
                self.splunk_test_type = "splunk_indextime"
            else:
                self._eventgen = self._app.get_config("eventgen.conf")    
                self.splunk_test_type = "splunk_searchtime"
            return self._eventgen
        except OSError:
            LOGGER.warning("eventgen.conf not found.")
            return None

    def get_sample_stanzas(self):
        """
        Yields: SampleStanza Object
        """
        eventgen_dict = self.get_eventgen_stanzas()
        self.check_samples()
        for sample_name, stanza_params in eventgen_dict.items():
            sample_path = os.path.join(self.path_to_samples, sample_name)
            yield SampleStanza(
                sample_path,
                stanza_params,
            )

    def get_eventgen_stanzas(self):
        """
        Format::

            {
                "sample_file_name": {    # Not Stanza name
                    "input_type": "str",
                    "tokens": {
                        1: {
                            token: #One#
                            replacementType: random
                            replacement: static 
                        }
                    }
                }
            }

        Return: 
            Eventgen stanzas dictionary
        """
        eventgen_dict = {}
        if os.path.exists(self.path_to_samples):
            for sample_file in os.listdir(self.path_to_samples):
                for stanza in self.eventgen.sects:
                    if re.search(stanza, sample_file):
                        self.match_stanzas.add(stanza)
                        eventgen_sections = self.eventgen.sects[stanza]
                        eventgen_dict.setdefault((sample_file), {
                            'tokens': {}
                        })
                        for stanza_param in eventgen_sections.options:
                            eventgen_property = eventgen_sections.options[stanza_param]
                            if eventgen_property.name.startswith('token'):
                                _, token_id, token_param = eventgen_property.name.split('.')
                                if not token_id in eventgen_dict[sample_file]['tokens'].keys():
                                    eventgen_dict[sample_file]['tokens'][token_id] = {}
                                eventgen_dict[sample_file]['tokens'][token_id][token_param] = eventgen_property.value
                            else:
                                eventgen_dict[sample_file][eventgen_property.name] = eventgen_property.value
        return eventgen_dict
    
    def check_samples(self):
        for stanza in self.eventgen.sects:
            if stanza not in self.match_stanzas:
                LOGGER.warning("No sample file found for stanza : {}".format(stanza))
                warnings.warn(UserWarning("No sample file found for stanza : {}".format(stanza)))