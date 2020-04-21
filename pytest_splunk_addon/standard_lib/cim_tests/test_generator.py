# -*- coding: utf-8 -*-
"""
Generates test cases to verify the CIM compatibility . 
"""
from . import DataModelHandler
from ..addon_parser import AddonParser


class CIMTestGenerator(object):
    """
    Generates test cases to verify the CIM compatibility.

    1. Parse the data model JSON
    2. Parse the add-on 
    3. Check which data model is mapped for each tags stanza
    4. Generate field based test cases for each data model mapped
    """

    def __init__(
        self, addon_path, data_model_path,
    ):

        self.data_model_handler = DataModelHandler(data_model_path)
        self.addon_parser = AddonParser(addon_path)

    def get_cim_models(self):
        yield from self.data_model_handler.get_mapped_data_models(self.addon_parser)

    def generate_cim_tests(self):
        """
        1. List CIM mapped models 
        2. Iterate through each field in CIM data model 
        3. Generate & Yield pytest.param for each test case
        4. Include the cluster test case as well. 
        """
        for each_model in self.get_cim_models():
            # get each fields from the model
            # Generate test case for each model
            print(each_model)
            yield True
