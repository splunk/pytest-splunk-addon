# -*- coding: utf-8 -*-
"""
Includes DataSet class which handles a single data set
"""
from ..addon_parser.fields import Field

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
        self.child_dataset = data_set_json.get("child_datasets")
        self.field_cluster = data_set_json.get("field_cluster")
        self._parse_fields(data_set_json)
        self.search_constraints = self._parse_constraint(data_set_json.get("search_constraints"))

    @classmethod
    def _parse_constraint(cls, constraint_search):
        """
        For future implementation when 
        Constraint parsing mechanism should be added.
        This would come in picture while we parse data model Json.
        """ 
        return constraint_search

    def _parse_fields(self, data_set_json):
        """
        Parse all the fields from the data_model_json
        """
        self.fields = Field.parse_fields(data_set_json["fields"])

    def match_tags(self, addon_tag_list):
        """
        Check if the tags are mapped with this data set
        """
        for each_tag_group in self.tags:
            return set(each_tag_group).issubset(set(addon_tag_list))
