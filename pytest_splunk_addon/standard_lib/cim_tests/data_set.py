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
Includes DataSet class which handles a single data set
"""
from ..addon_parser import Field


class DataSet(object):
    """
    Handles a single data set

    Args:
        data_set_json(dict): Json of a single DataSet
    """

    def __init__(self, data_set_json, data_model):
        self.name = data_set_json.get("name")
        self.tags = data_set_json.get("tags")
        self.data_model = data_model
        self.child_dataset = list(
            self.load_dataset(data_set_json.get("child_dataset"), self.data_model)
        )
        self.fields = list(
            Field.parse_fields(
                data_set_json.get("fields"),
                expected_values=[],
                negative_values=["", "-", "unknown", "null", "(null)"],
            )
        )
        self.fields_cluster = self._parse_fields_cluster(
            data_set_json.get("fields_cluster")
        )
        self.search_constraints = self._parse_constraint(
            data_set_json.get("search_constraints")
        )

    @classmethod
    def load_dataset(cls, dataset_list, data_model):
        """
        Parse all the fields from the data_model_json

        Args:
            dataset_list(list): Contains list of datasets
            data_model: Name of the data model

        Yields:
            data_set.DataSet: Dataset object for the given list
        """
        if dataset_list is not None:
            for each_dataset in dataset_list:
                yield cls(each_dataset, data_model)

    @classmethod
    def _parse_constraint(cls, constraint_search):
        """
        For future implementation when
        Constraint parsing mechanism should be added.
        This would come in picture while we parse data model Json.
        """
        return constraint_search

    def _parse_fields_cluster(self, fields_clusters):
        """
        Parse all the fields from the data_model_json
        """
        parsed_fields_clusters = []
        for each_cluster in fields_clusters:
            parsed_cluster = list(filter(lambda f: f.name in each_cluster, self.fields))
            assert len(each_cluster) == len(
                parsed_cluster
            ), f"Dataset={self.name}, Each cluster field should be included in fields list"
            parsed_fields_clusters.append(parsed_cluster)
        return parsed_fields_clusters

    def match_tags(self, addon_tag_list):
        """
        Check if the tags are mapped with this data set
        """
        for each_tag_group in self.tags:
            if set(each_tag_group).issubset(set(addon_tag_list)):
                return True

    def __str__(self):
        return str(self.name)
