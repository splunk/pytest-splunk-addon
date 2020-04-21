# -*- coding: utf-8 -*-
"""
Test Generator for an App.
Generates test cases of Fields and CIM.
"""
import logging

from .fields_tests import FieldTestGenerator
from .cim_tests import CIMTestGenerator

LOGGER = logging.getLogger("pytest-splunk-addon")


class AppTestGenerator(object):
    """
    Test Generator for an App.
    Generates test cases of Fields and CIM.

    Args:
        pytest_config: To get the options given to pytest
    """

    def __init__(self, pytest_config):
        self.pytest_config = pytest_config
        self.seen_tests = set()
        LOGGER.debug("Initializing FieldTestGenerator to generate the test cases")
        self.fieldtest_generator = FieldTestGenerator(
            self.pytest_config.getoption("splunk_app"),
            field_bank=self.pytest_config.getoption("field_bank", False),
        )
        self.test_generator = CIMTestGenerator(
            self.pytest_config.getoption("splunk_app"),
            self.pytest_config.getoption("dm_path"),
        )

    def generate_tests(self, fixture):
        """
        Generate the test cases based on the fixture provided 
        supported fixtures:

        *  splunk_app_positive_fields
        *  splunk_app_negative_fields
        *  splunk_app_tags
        *  splunk_app_eventtypes
        *  splunk_app_cim

        Args:
            fixture(str): fixture name
        """
        if fixture.endswith("fields"):
            is_positive = "positive" in fixture or not "negative" in fixture
            yield from self.dedup_tests(
                self.fieldtest_generator.generate_field_tests(is_positive=is_positive)
            )
        elif fixture.endswith("tags"):
            yield from self.dedup_tests(self.fieldtest_generator.generate_tag_tests())
        elif fixture.endswith("eventtypes"):
            yield from self.dedup_tests(
                self.fieldtest_generator.generate_eventtype_tests()
            )

        elif fixture.endswith("cim"):
            yield from self.dedup_tests(
                self.test_generator.generate_cim_tests()
            )

    def dedup_tests(self, test_list):
        """
        Deduplicate the test case parameters based on param.id

        Args:
            test_list(Generator): Generator of pytest.param

        Yields:
            Generator: De-duplicated pytest.param
        """
        for each_param in test_list:
            if each_param.id not in self.seen_tests:
                yield each_param
                self.seen_tests.add(each_param.id)
