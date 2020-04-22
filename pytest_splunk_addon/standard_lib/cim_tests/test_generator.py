# -*- coding: utf-8 -*-
"""
Generates test cases to verify the CIM compatibility . 
"""
import pytest

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
        test_field_type = ["required", "conditional"]
    ):

        self.data_model_handler = DataModelHandler(data_model_path)
        self.addon_parser = AddonParser(addon_path)
        self.test_field_type = test_field_type


    def generate_tests(self, fixture):
        """
        Generate the test cases based on the fixture provided 
        supported fixtures:
        * splunk_app_cim_fields
        * splunk_app_cim_not_allowed
        * splunk_app_cim_not_extracted

        Args:
            fixture(str): fixture name
        """
        if fixture.endswith("fields"):
            yield from self.generate_cim_fields_tests()
        elif fixture.endswith("not_allowed"):
            yield from self.generate_not_allowed_tests()
        elif fixture.endswith("not_extracted"):
            yield from self.generate_not_extracted_tests()


    def get_mapped_datasets(self):
        yield from self.data_model_handler.get_mapped_data_models(self.addon_parser)

    def generate_cim_fields_tests(self):
        """
        1. List CIM mapped models 
        2. Iterate through each field in CIM data model 
        3. Generate & Yield pytest.param for each test case
        4. Include the cluster test case as well. 
        """
        for tag_stanza, dataset_list in self.get_mapped_datasets():
            test_dataset = dataset_list[-1]

            # Test to check there is at least one event in the dataset
            yield pytest.param(
                {
                    "tag_stanza": tag_stanza,
                    "data_set": dataset_list,
                    "fields": []
                },
                id = f"{tag_stanza}::{test_dataset}"
            )
            # Test for each required fields 
            for each_field in test_dataset.fields:
                if each_field.type in self.test_field_type:
                    yield pytest.param(
                        {
                            "tag_stanza": tag_stanza,
                            "data_set": dataset_list,
                            "fields": [each_field]
                        }, 
                        id= f"{tag_stanza}::{test_dataset}::{each_field}"
                    )

            # Test for the field cluster 
            for each_fields_cluster in test_dataset.fields_cluster:
                yield pytest.param(
                    {
                        "tag_stanza": tag_stanza,
                        "data_set": dataset_list,
                        "fields": each_fields_cluster
                    }, 
                    id= (f"{tag_stanza}::{test_dataset}::"
                    f"{' + '.join([each_field.name for each_field in each_fields_cluster])}")
                )

    def generate_not_allowed_tests(self):
        pass

    def generate_not_extracted_tests(self):
        pass