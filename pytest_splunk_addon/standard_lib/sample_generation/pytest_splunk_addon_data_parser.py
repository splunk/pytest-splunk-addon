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
import os
import re
import logging
from .rule import raise_warning
from . import SampleStanza

import addonfactory_splunk_conf_parser_lib as conf_parser

LOGGER = logging.getLogger("pytest-splunk-addon")


PSA_DATA_CONFIG_FILE = "pytest-splunk-addon-data.conf"


class PytestSplunkAddonDataParser:
    """
    This class parses pytest-splunk-addon-data.conf file.

    Args:
        addon_path: Path to the Splunk App
    """

    conf_name = " "

    def __init__(self, addon_path: str, config_path: str):
        self._conf_parser = conf_parser.TABConfigParser()
        self.config_path = config_path
        self._psa_data = None
        self.addon_path = addon_path
        self.match_stanzas = set()

    def _path_to_samples(self):
        if os.path.exists(os.path.join(self.config_path, "samples")):
            LOGGER.info(
                "Samples path is: {}".format(os.path.join(self.config_path, "samples"))
            )
            return os.path.join(self.config_path, "samples")
        elif os.path.exists(
            os.path.join(
                os.path.abspath(os.path.join(self.config_path, os.pardir)), "samples"
            )
        ):
            LOGGER.info(
                "Samples path is: {}".format(
                    os.path.join(
                        os.path.abspath(os.path.join(self.config_path, os.pardir)),
                        "samples",
                    )
                )
            )
            return os.path.join(
                os.path.abspath(os.path.join(self.config_path, os.pardir)), "samples"
            )
        else:
            LOGGER.info(
                "Samples path is: {}".format(os.path.join(self.addon_path, "samples"))
            )
            return os.path.join(self.addon_path, "samples")

    @property
    def psa_data(self):
        psa_data_path = os.path.join(self.config_path, PSA_DATA_CONFIG_FILE)
        if os.path.exists(psa_data_path):
            self._conf_parser.read(psa_data_path)
            self.conf_name = "psa-data-gen"
            self._psa_data = self._conf_parser.item_dict()
            return self._psa_data
        else:
            LOGGER.warning(f"{PSA_DATA_CONFIG_FILE} not found")
            raise FileNotFoundError(f"{PSA_DATA_CONFIG_FILE} not found")

    def get_sample_stanzas(self):
        """
        Converts a stanza in pytest-splunk-addon-data.conf to an object of SampleStanza.

        Returns:
            List of SampleStanza objects.
        """
        _psa_data = self._get_psa_data_stanzas()
        self._check_samples()
        results = []
        for sample_name, stanza_params in sorted(_psa_data.items()):
            sample_path = os.path.join(self._path_to_samples(), sample_name)
            results.append(SampleStanza(sample_path, stanza_params))
        return results

    def _get_psa_data_stanzas(self):
        """
        Parses the pytest-splunk-addon-data.conf file and converts it into a dictionary.

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
            Dictionary representing pytest-splunk-addon-data.conf in the above format.
        """
        psa_data_dict = {}
        if os.path.exists(self._path_to_samples()):
            for sample_file in os.listdir(self._path_to_samples()):
                for stanza, fields in sorted(self.psa_data.items()):
                    stanza_match_obj = re.search(stanza, sample_file)
                    if stanza_match_obj and stanza_match_obj.group(0) == sample_file:
                        self.match_stanzas.add(stanza)
                        psa_data_dict.setdefault(sample_file, {"tokens": {}})
                        for key, value in fields.items():
                            if key.startswith("token"):
                                _, token_id, token_param = key.split(".")
                                token_key = f"{stanza}_{token_id}"
                                if (
                                    not token_key
                                    in psa_data_dict[sample_file]["tokens"].keys()
                                ):
                                    psa_data_dict[sample_file]["tokens"][token_key] = {}
                                psa_data_dict[sample_file]["tokens"][token_key][
                                    token_param
                                ] = value
                            else:
                                psa_data_dict[sample_file][key] = value
        return psa_data_dict

    def _check_samples(self):
        """
        Gives a user warning when sample file is not found for the stanza
        present in the configuration file.
        """
        if os.path.exists(self._path_to_samples()):
            for stanza in self.psa_data.keys():
                if stanza not in self.match_stanzas:
                    raise_warning(f"No sample file found for stanza : {stanza}")
                LOGGER.info(f"Sample file found for stanza : {stanza}")
