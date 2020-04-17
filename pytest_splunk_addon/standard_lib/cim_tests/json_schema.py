# -*- coding: utf-8 -*-
"""
Includes JSON schema for data models
"""
import json
from .base_schema import BaseSchema

class JSONSchema(BaseSchema):
    """
    Json Parser of the Data model files 
    """

    @classmethod
    def parse_data_model(cls, file_path):
        """
        Parse the Json file
        """
        with open(file_path) as json_f:
            return json.load(json_f)

