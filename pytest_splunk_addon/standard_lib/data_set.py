from .fields import Field

class DataSet(object):
    def __init__(self, data_set_json):
        # Attrs 
        self.fields = [] # Field 
        self.child_dataset = []

        self._parse_fields(data_set_json)
        self._parse_constraint(data_set_json["constraint"]["search"])


    def add_child_dataset(self, dataset):
        self.child_dataset.append(dataset)

    def get_child_datasets(self):
        return self.child_dataset

    def _parse_constraint(self, constraint_search):
        self.consraint = [  ] # List of tag tuples 

    def _parse_fields(self, data_set_json):
        field_json = data_set_json["fields"]
        self.fields.append( Field(field_json) )

    def match_tags(self, addon_tag_list):
        return (addon_tag_list in self.consraint)
            
