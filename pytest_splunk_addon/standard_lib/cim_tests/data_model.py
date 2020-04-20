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

        self.root_data_set = data_model_json.get("root_object")
        self.name = data_model_json.get("modelName")

    def _get_mapped_datasets(self, addon_tags, data_sets):
        """
        Recursive function to get the data_sets mapped with addon_tags
        If the parent data_set is mapped, check the child data_sets too

        Args:
            addon_tags(dict): {"stanza":str, "tags":list}
            data_sets(list): list of data sets to check with 
        
        Yields:
            data_set.DataSet: data set object mapped with the tags
        """
        for each_data_set in data_sets:
            if each_data_set.match_tags(addon_tags):
                yield each_data_set
                yield from self._get_mapped_datasets(addon_tags, each_data_set.get_child_datasets())


    def get_mapped_datasets(self, addon_tags):
        """
        Get all mapped dataSets for an Add-on's tags stanza

        Args:
            addon_tags(dict): {"stanza":str, "tags":list}

        Yields:
            data_set.DataSet: data set object mapped with the tags
        """
        yield from self._get_mapped_datasets(addon_tags, self.root_data_set)
