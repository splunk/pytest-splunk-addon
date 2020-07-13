# -*- coding: utf-8 -*-
"""
Generates test cases to verify the CIM compatibility . 
"""
import logging
import pytest
import json
import os.path as op
from . import DataModelHandler
from ..addon_parser import AddonParser
from ..addon_parser import Field

LOGGER = logging.getLogger("pytest-splunk-addon")


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

            * splunk_searchtime_cim_fields
            * splunk_searchtime_cim_fields_not_allowed
            * splunk_searchtime_cim_fields_not_extracted

        Args:
            fixture(str): fixture name
        """
        if fixture.endswith("fields"):
            yield from self.generate_cim_fields_tests()
        elif fixture.endswith("not_allowed_in_props"):
            yield from self.generate_field_extractions_test()
        elif fixture.endswith("not_allowed_in_search"):
            yield from self.generate_fields_event_count_test()
        elif fixture.endswith("mapped_datamodel"):
            yield from self.generate_mapped_datamodel_tests()

    def get_mapped_datasets(self):
        """
        Get all mapped data_sets for each tags stanza from an add-on

        Yields:
            tuple: Tag Stanza, mapped DataSet
        """
        yield from self.data_model_handler.get_mapped_data_models(self.addon_parser)

    def generate_cim_fields_tests(self):
        """
        Generates the test cases for required/conditional/cluster fields.

        1. List CIM mapped models 
        2. Iterate through each field in CIM data model 
        3. Generate & Yield pytest.param for each test case
        4. Include the cluster test case as well. 
        """
        LOGGER.info("Generating cim fields tests")
        for tag_stanza, dataset_list in self.get_mapped_datasets():
            test_dataset = dataset_list[-1]
            LOGGER.info(
                "Generating cim tests for tag_stanza=%s, dataset_list=%s",
                tag_stanza,
                test_dataset,
            )
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

    def generate_field_extractions_test(self):
        """
        Generate tests for the fields which the extractions are not allowed in props.conf

        1. Get a list of fields of type in ["not_allowed_in_search_and_props", "not_allowed_in_props"] from common fields json.
        2. Get a list of fields whose extractions are defined in props.
        3. Compare and get the list of fields whose extractions are not allowed but defined.
        4. yield the field list
        """
        common_fields_list = self.get_common_fields(
            test_type=["not_allowed_in_search_and_props", "not_allowed_in_props"]
        )

        for _, dataset_list in self.get_mapped_datasets():
            test_dataset = dataset_list[-1]
            common_fields_list.extend(
                [
                    each_field
                    for each_field in test_dataset.fields
                    if each_field.type
                    in ["not_allowed_in_search_and_props", "not_allowed_in_props"]
                    and each_field not in common_fields_list
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
                    and each_common_field not in not_allowed_fields
                ]
            )

        yield pytest.param(
            {"fields": not_allowed_fields}, id=f"searchtime_cim_fields",
        )

    def generate_fields_event_count_test(self):
        """
        Generates the tests which should not be extracted in an add-on

        1. Get the list of type=["not_allowed_in_search_and_props", "not_allowed_in_search"] fields from common fields json.
        2. Get the list of type=["not_allowed_in_search_and_props", "not_allowed_in_search"] fields from mapped datasets.
        3. Combine list1 and list2
        4. yield the field list
        5. Expected event_count for the fields: 0
        """

        not_allowed_fields = self.get_common_fields(
            test_type=["not_allowed_in_search_and_props", "not_allowed_in_search"]
        )

        for tag_stanza, dataset_list in self.get_mapped_datasets():
            test_dataset = dataset_list[-1]
            if not test_dataset.fields:
                continue
            test_fields = not_allowed_fields[:]
            test_fields.extend(
                [
                    each_field
                    for each_field in test_dataset.fields
                    if each_field.type
                    in ["not_allowed_in_search_and_props", "not_allowed_in_search"]
                    and each_field not in test_fields
                ]
            )
            yield pytest.param(
                {
                    "tag_stanza": tag_stanza,
                    "data_set": dataset_list,
                    "fields": test_fields,
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
        return [
            each_field
            for each_field in common_fields_list
            if each_field.type in test_type
        ]

    def generate_mapped_datamodel_tests(self):
        """
            Generates the tests to check event type is not be mapped with more than one data model

            1. Get a list of eventtype which defined in eventtype configuration.
            2. yield the eventtype list
        """
        eventtypes = []
        for each_eventtype in self.addon_parser.get_eventtypes():
            eventtypes.append(each_eventtype.get("stanza"))

        yield pytest.param( 
                {"eventtypes" : eventtypes},
                id=f"mapped_datamodel_tests",
            )
