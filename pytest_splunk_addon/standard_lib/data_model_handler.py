import os
import json
from .data_model import DataModel

class DataModelHandler(object):
    def __init__(self, data_model_path):
        self.data_models = list()
        self.load_data_models(data_model_path)

    def load_data_models(self, data_model_path):
        # Parse each fields and load data models
        json_list = [each for each in os.listdir() if each.endswith(".json")]
        for each_json in json_list:
            with open(each_json) as json_f:
                each_json = json.load(json_f)

            self.data_models.append(DataModel(each_json))

    def get_mapped_data_models(self, addon_parser):
        """
        The reason addon_parser is an argument & not attribute of the class 
        is that, the loaded handler should be used with multiple addons 
        """
        for each_tag_stanza in addon_parser.get_tags():
            for each_data_model in self.data_models:
                for each_mapped_dataset in each_data_model.get_mapped_datasets():
                    yield {
                        "stanza": each_tag_stanza,
                        "data_set": each_mapped_dataset
                    }
