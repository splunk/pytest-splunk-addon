# -*- coding: utf-8 -*-
"""
Provides Data Model handling functionalities. Such as\n
* Parse all the data model JSON files
* Get Mapped data model for an eventtype 
"""
import os
import json
from .data_model import DataModel

class DataModelHandler(object):
    """
    Provides Data Model handling functionalities. Such as\n
    * Parse all the data model JSON files
    * Get Mapped data model for an eventtype  

    Args:
        data_model_path(str): path to the data model JSON files
    """
    def __init__(self, data_model_path):
        self.data_models = self.load_data_models(data_model_path)

    def load_data_models(self, data_model_path):
        """
        Parse all the data model JSON files one by one

        Yields:
            (data_model.DataModel): parsed data model object 
        """
        # Parse each fields and load data models
        json_list = [each for each in os.listdir() if each.endswith(".json")]
        for each_json in json_list:
            with open(each_json) as json_f:
                each_json = json.load(json_f)

            yield DataModel(each_json)

    def get_mapped_data_models(self, addon_parser):
        """
        Get list of eventtypes mapped with Data-Sets.
        The reason addon_parser is an argument & not attribute of the class 
        is that, the loaded handler should be used with multiple addons. 

        Args:
            addon_parser(addon_parser.AddonParser): Object of Addon_parser

        Yields:
            tag stanza mapped with list of data sets 
            {
                tag_stanza: "eventtype=sample",
                "data_sets": DataSet(performance)
            }
        """
        for each_tag_stanza in addon_parser.get_tags():
            for each_data_model in self.data_models:
                for each_mapped_dataset in each_data_model.get_mapped_datasets():
                    yield {
                        "tag_stanza": each_tag_stanza,
                        "data_sets": each_mapped_dataset
                    }
