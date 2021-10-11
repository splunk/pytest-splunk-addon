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
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

from . import EventgenParser
from . import SampleStanza
from itertools import cycle


class SampleGenerator(object):
    """
    Main Class
    Generate sample objects
    """

    sample_stanzas = []
    conf_name = " "

    def __init__(self, addon_path, config_path=None, process_count=4):
        """
        init method for the class

        Args:
            addon_path(str): path to the addon
            process_count(no): generate {no} process for execution
        """
        self.addon_path = addon_path
        self.process_count = process_count
        self.config_path = config_path

    def get_samples(self):
        """
        Generate SampleEvent object
        """
        if not SampleGenerator.sample_stanzas:
            eventgen_parser = EventgenParser(
                self.addon_path, config_path=self.config_path
            )
            sample_stanzas = list(eventgen_parser.get_sample_stanzas())
            SampleGenerator.conf_name = eventgen_parser.conf_name
            with ThreadPoolExecutor(min(20, max(len(sample_stanzas), 1))) as t:
                t.map(SampleStanza.get_raw_events, sample_stanzas)
            # with ProcessPoolExecutor(self.process_count) as p:
            _ = list(
                map(
                    SampleStanza.tokenize,
                    sample_stanzas,
                    cycle([SampleGenerator.conf_name]),
                )
            )
            SampleGenerator.sample_stanzas = sample_stanzas
        for each_sample in SampleGenerator.sample_stanzas:
            yield from each_sample.get_tokenized_events()

    @classmethod
    def clean_samples(cls):
        cls.sample_stanzas = list()
        cls.conf_name = str()
