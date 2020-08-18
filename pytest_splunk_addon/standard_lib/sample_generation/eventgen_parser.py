import os
import re
import logging
from splunk_appinspect import App
from .rule import Rule, raise_warning
from . import SampleStanza

LOGGER = logging.getLogger("pytest-splunk-addon")
import warnings


class EventgenParser:
    """
    This class represents the entire eventgen.conf file and handles parsing mechanism of eventgen and the rules.

    Args:
        addon_path (str): Path to the Splunk App 
    """

    conf_name = " "

    def __init__(self, addon_path, config_path=None):
        self._app = App(addon_path, python_analyzer_enable=False)
        self.config_path = config_path
        self._eventgen = None
        self.addon_path = addon_path
        self.match_stanzas = set()

    @property
    def path_to_samples(self):
        if os.path.exists(os.path.join(self.config_path, "samples")):
            return os.path.join(self.config_path, "samples")
        elif os.path.exists(
            os.path.join(
                os.path.abspath(os.path.join(self.config_path, os.pardir)), "samples"
            )
        ):
            return os.path.join(
                os.path.abspath(os.path.join(self.config_path, os.pardir)), "samples"
            )
        else:
            return os.path.join(self.addon_path, "samples")

    @property
    def eventgen(self):
        try:
            relative_path = os.path.relpath(self.config_path, self.addon_path)
            if os.path.exists(
                os.path.join(
                    self.config_path,
                    "pytest-splunk-addon-data.conf"
                )
            ):
                self._eventgen = self._app.get_config(
                    "pytest-splunk-addon-data.conf", dir=relative_path
                )
                self.conf_name = "psa-data-gen"

            elif os.path.exists(
                os.path.join(
                    self.config_path,
                    'eventgen.conf'
                    )
                ):

                self._eventgen = self._app.get_config(
                    "eventgen.conf", dir=relative_path
                )
                self.conf_name = "eventgen"

            else:
                self._eventgen = self._app.get_config("eventgen.conf")
                self.conf_name = "eventgen"
            return self._eventgen

        except OSError:
            LOGGER.warning("pytest-splunk-addon-data.conf/eventgen.conf not Found")
            raise FileNotFoundError("pytest-splunk-addon-data.conf/eventgen.conf not Found")

    def get_sample_stanzas(self):
        """
        Converts a stanza in eventgen.conf to an object of SampleStanza.

        Yields:
            SampleStanza Object
        """
        eventgen_dict = self.get_eventgen_stanzas()
        self.check_samples()
        for sample_name, stanza_params in sorted(eventgen_dict.items()):
            sample_path = os.path.join(self.path_to_samples, sample_name)
            yield SampleStanza(
                sample_path, stanza_params,
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
        if os.path.exists(self.path_to_samples):
            for sample_file in os.listdir(self.path_to_samples):
                for stanza in sorted(self.eventgen.sects):
                    stanza_match_obj = re.search(stanza, sample_file)
                    if stanza_match_obj and stanza_match_obj.group(0) == sample_file:
                        self.match_stanzas.add(stanza)
                        eventgen_sections = self.eventgen.sects[stanza]
                        eventgen_dict.setdefault((sample_file), {"tokens": {}})
                        for stanza_param in eventgen_sections.options:
                            eventgen_property = eventgen_sections.options[stanza_param]
                            if eventgen_property.name.startswith("token"):
                                _, token_id, token_param = eventgen_property.name.split(
                                    "."
                                )
                                token_key = "{}_{}".format(stanza, token_id)
                                if (
                                    not token_key
                                    in eventgen_dict[sample_file]["tokens"].keys()
                                ):
                                    eventgen_dict[sample_file]["tokens"][token_key] = {}
                                eventgen_dict[sample_file]["tokens"][token_key][
                                    token_param
                                ] = eventgen_property.value
                            else:
                                eventgen_dict[sample_file][
                                    eventgen_property.name
                                ] = eventgen_property.value
        return eventgen_dict

    def check_samples(self):
        """
        Gives a user warning when sample file is not found for the stanza peresent in the configuration file.
        """
        if os.path.exists(self.path_to_samples):
            for stanza in self.eventgen.sects:
                if stanza not in self.match_stanzas:
                    raise_warning("No sample file found for stanza : {}".format(stanza))
