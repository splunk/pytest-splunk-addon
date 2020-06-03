# -*- coding: utf-8 -*-
"""
Provides the Field class containing all the field properties and a decorator 
to convert a list to field list
"""

from functools import wraps
class Field(object):
    """
    Contains the field properties

    * name (str): name of the field
    * type (str): Field type. Supported [required, conditional, optional]
    * expected_values (list): The field should have this expected values
    * negative_values (list): The field should not have negative values
    * condition (spl): The field should only be checked if the condition satisfies
    * validity (eval): eval statement to extract the valid fields only 

    Args:
        field_json (dict): dictionary containing field properties 
    """
    SUPPORTED_TYPES = ["required", "conditional", "optional"]

    def __init__(self, field_json=None):
        self.name = field_json.get("name")
        self.type = field_json.get("type") or "required"
        self.multi_value = field_json.get("multi_value") or False
        self.expected_values = field_json.get("expected_values", ["*"])
        self.negative_values = field_json.get("negative_values", ["-", ""])
        self.condition = field_json.get("condition") or ""
        self.validity = field_json.get("validity") or self.name

    def __str__(self):
        return str(self.name)

    def get_type(self):
        return self.type

    @classmethod
    def parse_fields(cls, field_list, **kwargs):
        """
        Parse the fields from a list 

        Args:
            field_list (list): list of field names 
        """
        for each_fields in field_list:
            yield Field(dict(kwargs, **each_fields))

    def get_properties(self):
        return (
            f"{self.name}"
            f"\ntype={self.type}"
            f"\nmulti_value={self.multi_value}"
            f"\ncondition={self.condition}"
            f"\nvalidity={self.validity}"
            f"\nexpected_values={self.expected_values}"
            f"\nnegative_values={self.negative_values}"
        )


def convert_to_fields(func):
    """
    Decorator to initialize the list of fields 
    """
    @wraps(func)
    def inner_func(*args, **kwargs):
        for each_field in func(*args, **kwargs):
            if each_field:
                yield Field({"name": each_field})
    return inner_func
