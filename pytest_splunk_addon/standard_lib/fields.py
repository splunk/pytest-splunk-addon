# -*- coding: utf-8 -*-

class Field(object):
    """
        Contains the field properties 
    """

    def __init__(self, field_json=None):
        self.name = field_json.get("name")
        self.field_type = field_json.get("field_type")
        self.expected_values = field_json.get("expected_values", ["*"])
        self.negative_values = field_json.get("negative_values", ["-", ""])
        self.condition = field_json.get("condition", ["-", ""])
        self.validity = field_json.get("condition", "")

    def __str__(self):
        return self.name

    @classmethod
    def parse_fields(cls, field_list):
        for each_fields in field_list:
            yield Field(each_fields)

def convert_to_fields(func):
    """
    Decorator to initialize the list of fields 
    """
    def inner_func(*args, **kwargs):
        for each_field in func(*args, **kwargs):
            if each_field:
                yield Field({"name": each_field})
    return inner_func
