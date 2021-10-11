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
Includes DataModel class which handles the DataSets within a data model. 
"""

from . import DataSet


class DataModel(object):
    """
    Handles the DataSets within a data model.

    Args:
        data_model_json(dict): Dictionary of the data model Json file
    """

    def __init__(self, data_model_json):

        self.name = data_model_json.get("model_name")
        self.root_data_set = list(
            DataSet.load_dataset(data_model_json.get("objects"), self.name)
        )

    def _get_mapped_datasets(self, addon_tags, data_sets, mapped_datasets=[]):
        """
        Recursive function to get the data_sets mapped with addon_tags
        If the parent data_set is mapped, check the child data_sets too

        Args:
            addon_tags(list): Contains tags mapped to a stanza
            data_sets(list): list of data sets to check with

        Yields:
            data_set.DataSet: data set object mapped with the tags
        """
        for each_data_set in data_sets:
            if each_data_set.match_tags(addon_tags):
                current_mapped_ds = mapped_datasets[:]
                current_mapped_ds.append(each_data_set)
                yield current_mapped_ds
                yield from self._get_mapped_datasets(
                    addon_tags, each_data_set.child_dataset, current_mapped_ds
                )

    def get_mapped_datasets(self, addon_tags):
        """
        Get all mapped dataSets for an Add-on's tags stanza

        Args:
            addon_tags(list): Contains tags mapped to a stanza

        Yields:
            data_set.DataSet: data set object mapped with the tags
        """
        yield from self._get_mapped_datasets(addon_tags, self.root_data_set)

    def __str__(self):
        return str(self.name)
