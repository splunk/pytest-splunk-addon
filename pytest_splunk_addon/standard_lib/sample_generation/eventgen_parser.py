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
    This class represents the entire eventgen.conf file and handles parsing mechanism of eventgen and the rules.

    Args:
        addon_path (str): Path to the Splunk App 
    """
    splunk_test_type = " "

    def __init__(self, addon_path, config_path=None):
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
        Converts a stanza in eventgen.conf to an object of SampleStanza.

        Yields:
            SampleStanza Object
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
        Parses the eventgen.conf file and converts it into a dictionary.
        
        Format::

            {
                "sample_file_name": # Not Stanza name
                {
                    "input_type": "str",
                    "tokens":
                    {
                        1:
                        {
                            token: #One#
                            replacementType: random
                            replacement: static
                        }
                    }
                }
            }

        Return:
            Dictionary representing eventgen.conf in the above format.
        """
        eventgen_dict = {}
        child_dict = {'tokens': {}}
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
                                if not eventgen_dict[sample_file]['tokens'][token_id].get(token_param) and sample_file != stanza:
                                    eventgen_dict[sample_file]['tokens'][token_id][token_param] = eventgen_property.value
                                else:
                                    if not token_id in child_dict['tokens'].keys():
                                        child_dict['tokens'][token_id] = {}    
                                    child_dict['tokens'][token_id][token_param] = eventgen_property.value
                            else:
                                eventgen_dict[sample_file][eventgen_property.name] = eventgen_property.value
                    if child_dict['tokens'].keys():
                        eventgen_dict[sample_file]['tokens'] = self.append_child_tokens(sample_file, eventgen_dict, child_dict)
                        child_dict['tokens'] = {}
        return eventgen_dict

    def append_child_tokens(self, sample_file, eventgen_dict, child_dict):
        """
        To combine all the pokens present in regex stanza and original stanza.

        Args:
            sample_file(str): sample file name.
            eventgen_dict(dict): Dict representation of a cofiguration file stanza
            child_dict(dict): dict containing token properties with intersecting token-id.
        """
        dict_len = len(eventgen_dict[sample_file]['tokens'].keys())
        random_dict = {'tokens': {}}
        cnt = 0
        for i in range(dict_len):
            if eventgen_dict[sample_file]['tokens'][str(i)] == {}:
                cnt = i
                break
            else:
                random_dict['tokens'][str(i)] = eventgen_dict[sample_file]['tokens'][str(i)]
        for i in range(0, dict_len):
            random_dict['tokens'][str(cnt + i)] = child_dict["tokens"][str(i)]
        return random_dict['tokens']

    def check_samples(self):
        """
        Gives a user warning when sample file is not found for the stanza peresent in the configuration file.
        """
        if os.path.exists(self.path_to_samples):
            for stanza in self.eventgen.sects:
                if stanza not in self.match_stanzas:
                    LOGGER.warning("No sample file found for stanza : {}".format(stanza))
                    warnings.warn(UserWarning("No sample file found for stanza : {}".format(stanza)))
