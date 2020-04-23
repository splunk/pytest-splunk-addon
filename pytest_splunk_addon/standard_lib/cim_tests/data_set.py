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
    def __init__(self, data_set_json):
        # TODO: Assign all required attrs  
        self.name = data_set_json.get("name")
        self.tags = data_set_json.get("tags")
        self.child_dataset = list(self.load_dataset(data_set_json.get("child_dataset")))
        self.fields = list(Field.parse_fields(data_set_json.get("fields")))
        self.fields_cluster = self._parse_fields_cluster(data_set_json.get("fields_cluster"))
        self.search_constraints = self._parse_constraint(data_set_json.get("search_constraints"))

    @classmethod
    def load_dataset(cls, dataset_list):
        if dataset_list is not None:
            for each_dataset in dataset_list:
                yield cls(each_dataset)


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
            parsed_cluster = list(filter(lambda f:f.name in each_cluster, self.fields))
            assert len(each_cluster) == len(parsed_cluster), (
                f"Dataset={self.name}, Each cluster field should be included in fields list"
            )
            parsed_fields_clusters.append(parsed_cluster)
        return parsed_fields_clusters

    def match_tags(self, addon_tag_list):
        """
        Check if the tags are mapped with this data set
        """
        for each_tag_group in self.tags:
            return set(each_tag_group).issubset(set(addon_tag_list))

    def __str__(self):
        return self.name
