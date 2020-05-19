# -*- coding: utf-8 -*-
"""
Test Generator for an App.
Generates test cases of Fields and CIM.
"""
import logging
import os
from .fields_tests import FieldTestGenerator
from .cim_tests import CIMTestGenerator

LOGGER = logging.getLogger("pytest-splunk-addon")

class AppTestGenerator(object):
    """
    Test Generator for an App.
    Generates test cases of Fields and CIM.
    The test generator is to include all the specific test generators. 

    AppTestGenerator should not have any direct generation methods, it should call a specific 
    test generator methods only. Make sure there is no heavy initialization in __init__, all the 
    configurations and operations should only take place in generate_tests method.

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

        data_model_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "data_models"
        )
        LOGGER.debug("Initializing CIMTestGenerator to generate the test cases")
        self.cim_test_generator = CIMTestGenerator(
            self.pytest_config.getoption("splunk_app"),
            self.pytest_config.getoption("splunk_dm_path") or data_model_path,
        )

    def generate_tests(self, fixture):
        """
        Generate the test cases based on the fixture provided 
        supported fixtures:

        * splunk_app_searchtime_*
        * splunk_app_cim_*

        Args:
            fixture(str): fixture name
        """
        if fixture.startswith("splunk_searchtime_fields"):
            yield from self.dedup_tests(
                self.fieldtest_generator.generate_tests(fixture),
                fixture
            )
        elif fixture.startswith("splunk_searchtime_cim"):
            yield from self.dedup_tests(
                self.cim_test_generator.generate_tests(fixture),
                fixture
            )

    def dedup_tests(self, test_list, fixture):
        """
        Deduplicate the test case parameters based on param.id

        Args:
            test_list (Generator): Generator of pytest.param
            fixture (str): fixture name

        Yields:
            Generator: De-duplicated pytest.param
        """
        param_list = []
        for each_param in test_list:
            if (fixture, each_param.id) not in self.seen_tests:
                param_list.append(each_param)
                self.seen_tests.add((fixture, each_param.id))

        # Sort the test generated.
        # ACD-4138: As pytest-xdist expects the tests to be ordered
        return sorted(param_list, key=lambda param: param.id)
