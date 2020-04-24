# -*- coding: utf-8 -*-
"""
Generates test cases to verify the CIM compatibility . 
"""
import pytest
import json
import os.path as op
from . import DataModelHandler
from ..addon_parser import AddonParser
from ..addon_parser import Field


class CIMTestGenerator(object):
    """
    Generates test cases to verify the CIM compatibility.

    Args:
        addon_path (str): 
            Relative or absolute path to the add-on
        data_model_path (str): 
            Relative or absolute path to the data model json files
        test_field_type (list): 
            For which types of fields, the test cases should be generated
        common_fields_path (str): 
            Relative or absolute path of the json file with common fields
    """

    COMMON_FIELDS_PATH = "CommonFields.json"

    def __init__(
        self,
        addon_path,
        data_model_path,
        test_field_type=["required", "conditional"],
        common_fields_path=None,
    ):

        self.data_model_handler = DataModelHandler(data_model_path)
        self.addon_parser = AddonParser(addon_path)
        self.test_field_type = test_field_type
        self.common_fields_path = common_fields_path or op.join(
            op.dirname(op.abspath(__file__)), self.COMMON_FIELDS_PATH
        )

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
        """
        Get all mapped data_sets for each tags stanza from an add-on

        Yields:
            tuple: Tag Stanza, mapped DataSet
        """
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
                {"tag_stanza": tag_stanza, "data_set": dataset_list, "fields": []},
                id=f"{tag_stanza}::{test_dataset}",
            )
            # Test for each required fields
            for each_field in test_dataset.fields:
                if each_field.type in self.test_field_type:
                    yield pytest.param(
                        {
                            "tag_stanza": tag_stanza,
                            "data_set": dataset_list,
                            "fields": [each_field],
                        },
                        id=f"{tag_stanza}::{test_dataset}::{each_field}",
                    )

            # Test for the field cluster
            for each_fields_cluster in test_dataset.fields_cluster:
                yield pytest.param(
                    {
                        "tag_stanza": tag_stanza,
                        "data_set": dataset_list,
                        "fields": each_fields_cluster,
                    },
                    id=(
                        f"{tag_stanza}::{test_dataset}::"
                        f"{'+'.join([each_field.name for each_field in each_fields_cluster])}"
                    ),
                )

    def generate_not_allowed_tests(self):
        """
        1. Get a list of fields of type in ["not_extracted", "not_allowed"] from common fields json.
        2. Get a list of fields of type in ["not_extracted", "not_allowed"] from mapped datasets.
        3. Combine list1 and list2
        4. Get a list of fields whose extractions are defined in props.
        5. Compare and get the list of fields whose extractions are not allowed but defined.
        6. yield the field list
        """
        common_fields_list = self.get_common_fields(
            test_type=["not_extracted", "not_allowed"]
        )
        for tag_stanza, dataset_list in self.get_mapped_datasets():
            test_dataset = dataset_list[-1]
            common_fields_list.extend(
                [
                    each_field
                    for each_field in test_dataset.fields
                    if each_field.type in ["not_extracted", "not_allowed"]
                ]
            )

        addon_stanzas = self.addon_parser.get_props_fields()
        not_allowed_fields = []
        for field_group in addon_stanzas:
            test_group = field_group.copy()
            not_allowed_fields.extend(
                [
                    {
                        "name": each_common_field.name,
                        "stanza": test_group.get("stanza"),
                        "classname": test_group.get("classname"),
                    }
                    for each in test_group["fields"]
                    for each_common_field in common_fields_list
                    if each_common_field.name == each.name
                ]
            )

        yield pytest.param(
            {"fields": not_allowed_fields}, id=f"searchtime_cim_fields",
        )

    def generate_not_extracted_tests(self):
        """
        1. Get the list of type="not_extracted" fields from common fields json.
        2. Get the list of type="not_extracted" fields from mapped datasets.
        3. Combine list1 and list2
        4. yield the field list
        5. Expected event_count for the fields: 0
        """

        not_extracted_fields = self.get_common_fields(test_type=["not_extracted"])
        for tag_stanza, dataset_list in self.get_mapped_datasets():
            test_dataset = dataset_list[-1]
            not_extracted_fields.extend(
                [
                    each_field
                    for each_field in test_dataset.fields
                    if each_field.type == "not_extracted"
                ]
            )
            yield pytest.param(
                {
                    "tag_stanza": tag_stanza,
                    "data_set": dataset_list,
                    "fields": not_extracted_fields,
                },
                id=f"{tag_stanza}::{test_dataset}",
            )

    def get_common_fields(self, test_type=[]):
        """
        To obtain list object of common fields mentioned in COMMON_FIELDS_PATH
        """
        with open(self.common_fields_path, "r") as cf_json:
            common_fields_json = json.load(cf_json)
        common_fields_list = list(Field.parse_fields(common_fields_json["fields"]))
        if len(test_type) == 1:
            return [
                each_field
                for each_field in common_fields_list
                if each_field.type in test_type
            ]
        else:
            return common_fields_list
