#
# Copyright 2024 Splunk Inc.
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
from concurrent.futures import ThreadPoolExecutor

from . import PytestSplunkAddonDataParser
from . import SampleStanza


class SampleGenerator(object):
    """
    Main Class
    Generate sample objects
    """

    def __init__(self, addon_path, config_path=None):
        """
        init method for the class

        Args:
            addon_path(str): path to the addon
        """
        self._sample_stanzas = []
        self._psa_data_parser = PytestSplunkAddonDataParser(addon_path, config_path=config_path)

    def get_samples(self):
        """
        Generate SampleEvent object
        """
        if not self._sample_stanzas:
            sample_stanzas = self._psa_data_parser.get_sample_stanzas()
            with ThreadPoolExecutor(min(20, max(len(sample_stanzas), 1))) as t:
                t.map(SampleStanza.get_raw_events, sample_stanzas)
            _ = list(
                map(
                    SampleStanza.tokenize,
                    sample_stanzas,
                )
            )
            SampleGenerator.sample_stanzas = sample_stanzas
        for each_sample in SampleGenerator.sample_stanzas:
            yield from each_sample.get_tokenized_events()

    def get_samples_store(self):
        tokenized_events = list(self.get_samples())
        return {
            "conf_name": self._psa_data_parser.conf_name,
            "tokenized_events": tokenized_events,
        }
