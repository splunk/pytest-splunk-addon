import json
from .base_parser import BaseParser

class JsonParser(BaseParser):
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

