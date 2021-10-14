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
# -*- coding: utf-8 -*-
"""
Provides Data Model handling functionalities. Such as

* Parse all the data model JSON files
* Get Mapped data model for an eventtype 
"""
import os
import logging

import json
from . import DataModel
from . import JSONSchema

LOGGER = logging.getLogger("pytest-splunk-addon")


class DataModelHandler(object):
    """
    Provides Data Model handling functionalities. Such as

    * Parse all the data model JSON files
    * Get Mapped data model for an eventtype

    Args:
        data_model_path (str): path to the data model JSON files
    """

    def __init__(self, data_model_path):
        self.data_model_path = data_model_path
        self._data_models = None

    @property
    def data_models(self):
        if not self._data_models:
            self._data_models = list(self.load_data_models(self.data_model_path))
        return self._data_models

    def _get_all_tags_per_stanza(self, addon_parser):
        """
        Get list of all tags mapped with single stanza in tags.conf

        Args:
            addon_parser (addon_parser.AddonParser): Object of Addon_parser

        Returns:
            tags mapped with stanzas in tags.conf

                {
                    stanza_name: [List of tags mapped to the stanza]
                }
        """

        tag_stanzas = {}
        for each_tag in addon_parser.get_tags():
            stanza_name = each_tag["stanza"]
            tags = each_tag["tag"]

            tag_stanzas.setdefault(stanza_name, []).append(tags)

        return tag_stanzas

    def load_data_models(self, data_model_path):
        """
        Parse all the data model JSON files one by one

        Yields:
            (cim_tests.data_model.DataModel): parsed data model object
        """
        # Parse each fields and load data models
        json_list = [
            each for each in os.listdir(data_model_path) if each.endswith(".json")
        ]
        for each_json in json_list:
            yield DataModel(
                JSONSchema.parse_data_model(os.path.join(data_model_path, each_json))
            )

    def get_mapped_data_models(self, addon_parser):
        """
        Get list of eventtypes mapped with Data-Sets.
        The reason addon_parser is an argument & not attribute of the class
        is that, the loaded handler should be used with multiple addons.

        Args:
            addon_parser (addon_parser.AddonParser): Object of Addon_parser

        Yields:
            tag stanza mapped with list of data sets

                "eventtype=sample", DataSet(performance)
        """

        tags_in_each_stanza = self._get_all_tags_per_stanza(addon_parser)
        for eventtype, tags in tags_in_each_stanza.items():
            is_mapped_datasets = False
            for each_data_model in self.data_models:
                mapped_datasets = list(each_data_model.get_mapped_datasets(tags))
                if mapped_datasets:
                    is_mapped_datasets = True
                    LOGGER.info(
                        "Data Model=%s mapped for %s", each_data_model, eventtype
                    )
                    for each_mapped_dataset in mapped_datasets:
                        yield eventtype, each_mapped_dataset
            if not is_mapped_datasets:
                LOGGER.info("No Data Model mapped for %s", eventtype)
