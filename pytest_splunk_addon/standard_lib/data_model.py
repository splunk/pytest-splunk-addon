from .data_set import DataSet

class DataModel(object):
    def __init__(self, data_model_json):

        self.root_data_set = None
        self.name = data_model_json.get("modelName")


    def _init_data_set(self, data_set_json):
        data_set_map = dict()
        for each_object in data_set_json["objects"]:
            data_set_map[each_object["objectName"]] = DataSet(each_object)

        for each_object in data_set_json["objects"]:
            # Maintain the dataset tree 
            if each_object["parentName"] == "BaseEvent":
                self.root_data_set = data_set_map[each_object["objectName"]]
            else:
                data_set_map[each_object["parentName"]].add_child_dataset(
                    data_set_map[each_object["objectName"]]
                )


    def _get_mapped_datasets(self, addon_tags, data_sets):
        for each_data_set in data_sets:
            if each_data_set.match_tags(addon_tags):
                yield each_data_set
                yield from self._get_mapped_datasets(addon_tags, each_data_set.get_child_datasets())




    def get_mapped_datasets(self, addon_tags):
        yield from self._get_mapped_datasets(addon_tags, self.root_data_set)
