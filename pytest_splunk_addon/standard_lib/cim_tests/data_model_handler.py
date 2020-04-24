# -*- coding: utf-8 -*-
"""
Provides Data Model handling functionalities. Such as

* Parse all the data model JSON files
* Get Mapped data model for an eventtype 
"""
import os
import json
from . import DataModel
from . import JSONSchema


class DataModelHandler(object):
    """
    Provides Data Model handling functionalities. Such as

    * Parse all the data model JSON files
    * Get Mapped data model for an eventtype  

    Args:
        data_model_path (str): path to the data model JSON files
    """

    def __init__(self, data_model_path):
        self.data_models = list(self.load_data_models(data_model_path))

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
            (data_model.DataModel): parsed data model object 
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
            for each_data_model in self.data_models:
                for each_mapped_dataset in each_data_model.get_mapped_datasets(tags):
                    yield eventtype, each_mapped_dataset
