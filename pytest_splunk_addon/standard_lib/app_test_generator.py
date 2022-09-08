#
# Copyright 2021 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# -*- coding: utf-8 -*-
"""
Test Generator for an App.
Generates test cases of Fields and CIM.
"""
import logging
import os
from .fields_tests import FieldTestGenerator
from .cim_tests import CIMTestGenerator
from .index_tests import IndexTimeTestGenerator
from .sample_generation import SampleXdistGenerator

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

        store_events = self.pytest_config.getoption("store_events")
        config_path = self.pytest_config.getoption("splunk_data_generator")
        sample_generator = SampleXdistGenerator(
            self.pytest_config.getoption("splunk_app"), config_path
        )
        store_sample = sample_generator.get_samples(store_events)
        self.tokenized_events = store_sample.get("tokenized_events")
        LOGGER.debug("Initializing FieldTestGenerator to generate the test cases")
        self.fieldtest_generator = FieldTestGenerator(
            self.pytest_config.getoption("splunk_app"),
            self.tokenized_events,
            field_bank=self.pytest_config.getoption("field_bank", False),
        )

        data_model_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "data_models"
        )
        LOGGER.debug("Initializing CIMTestGenerator to generate the test cases")
        self.cim_test_generator = CIMTestGenerator(
            self.pytest_config.getoption("splunk_app"),
            self.pytest_config.getoption("splunk_dm_path") or data_model_path,
            self.tokenized_events,
        )
        self.indextime_test_generator = IndexTimeTestGenerator()

    def generate_tests(self, fixture):
        """
        Generate the test cases based on the fixture provided
        supported fixtures:

        * splunk_app_searchtime_*
        * splunk_app_cim_*
        * splunk_indextime

        Args:
            fixture(str): fixture name
        """
        if fixture in (
            "splunk_searchtime_fields_requirements",
            "splunk_searchtime_fields_datamodels",
        ):
            yield from self.fieldtest_generator.generate_tests(fixture)
        elif fixture == "splunk_searchtime_cim_fields_recommended":
            yield from self.cim_test_generator.generate_tests(fixture)
        elif fixture.startswith("splunk_searchtime_fields"):
            yield from self.dedup_tests(
                self.fieldtest_generator.generate_tests(fixture),
                fixture,
            )
        elif fixture.startswith("splunk_searchtime_cim"):
            yield from self.dedup_tests(
                self.cim_test_generator.generate_tests(fixture),
                fixture,
            )

        elif fixture.startswith("splunk_indextime"):
            # TODO: What should be the id of the test case?
            # Sourcetype + Host + Key field + _count

            pytest_params = None

            store_events = self.pytest_config.getoption("store_events")
            app_path = self.pytest_config.getoption("splunk_app")
            config_path = self.pytest_config.getoption("splunk_data_generator")

            if "key_fields" in fixture:
                pytest_params = list(
                    self.indextime_test_generator.generate_tests(
                        store_events,
                        app_path=app_path,
                        config_path=config_path,
                        test_type="key_fields",
                    )
                )

            elif "_time" in fixture:
                pytest_params = list(
                    self.indextime_test_generator.generate_tests(
                        store_events,
                        app_path=app_path,
                        config_path=config_path,
                        test_type="_time",
                    )
                )

            elif "line_breaker" in fixture:
                pytest_params = list(
                    self.indextime_test_generator.generate_tests(
                        store_events,
                        app_path=app_path,
                        config_path=config_path,
                        test_type="line_breaker",
                    )
                )

            yield from sorted(pytest_params, key=lambda param: param.id)

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
