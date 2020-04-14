# -*- coding: utf-8 -*-
"""
Module include class to generate the test cases
to test the knowledge objects of an Add-on.
"""
import pytest
import json
import logging
from itertools import chain

from ..addon_parser import Field
from ..addon_parser import AddonParser
from . import FieldBank

LOGGER = logging.getLogger("pytest-splunk-addon")
class FieldTestGenerator(object):
    """
    Generates test cases to test the knowledge objects of an Add-on.
    * Provides the pytest parameters to the test templates.
    * Supports field_bank: List of fields with patterns and expected
        values which should be tested for the Add-on.
    
    Args:
        app_path (str): Path of the app package
        field_bank (str): Path of the fields Json file 
    """

    def __init__(self, app_path, field_bank=None):
        LOGGER.debug("initializing AddonParser to parse the app")
        self.addon_parser = AddonParser(app_path)
        self.field_bank = field_bank
                
    def generate_field_tests(self, is_positive):
        """
        Generate test case for fields

        Args:
            is_positive (bool): Test type to generate 

        Yields:
            pytest.params for the test templates 
        """
        LOGGER.info("generating field tests")
        field_itr = chain(
            FieldBank.init_field_bank_tests(self.field_bank), 
            self.addon_parser.get_props_fields()
        )
        for fields_group in field_itr:
            # Generate test case for the stanza 
            # Do not generate if it is a negative test case
            if is_positive:
                stanza_test_group = fields_group.copy()
                stanza_test_group["fields"] = []
                yield pytest.param(
                    stanza_test_group,
                    id="{stanza}".format(**fields_group)
                )

            # Generate a test case for all the fields in the classname 
            if self._contains_classname(fields_group, ["EXTRACT", "REPORT"]):
                yield pytest.param( 
                    fields_group,
                    id="{stanza}::{classname}".format(**fields_group)
                )

            # For each field mentioned in field_bank, a separate 
            # test should be generated. 
            # Counter to make the test_id unique
            field_bank_id = 0 

            # Generate test-cases for each field in classname one by one 
            for each_field in fields_group["fields"]:

                # Create a dictionary for a single field with classname and stanza
                one_field_group = fields_group.copy()
                one_field_group["fields"] = [each_field]
                if fields_group["classname"] != "field_bank":
                    test_type = "field"
                else:
                    field_bank_id += 1
                    test_type = f"field_bank_{field_bank_id}"

                stanza = fields_group["stanza"]
                yield pytest.param(
                    one_field_group,
                    id=f"{stanza}::{test_type}::{each_field}"
                )

    def generate_tag_tests(self):
        """
        Generate test case for tags

        Yields:
            pytest.params for the test templates 
        """
        for each_tag_group in self.addon_parser.get_tags():
            yield pytest.param( 
                    each_tag_group,
                    id="{stanza}::tag::{tag}".format(**each_tag_group)
                )

    def generate_eventtype_tests(self):
        """
        Generate test case for eventtypes

        Yields:
            pytest.params for the test templates 

        """
        for each_eventtype in self.addon_parser.get_eventtypes():
            yield pytest.param( 
                    each_eventtype,
                    id="eventtype::{stanza}".format(**each_eventtype)
                )

    def _contains_classname(self, fields_group, criteria):
        """
        Check if the field_group dictionary contains the classname
        """
        return any([fields_group["classname"].startswith(each) for each in criteria])