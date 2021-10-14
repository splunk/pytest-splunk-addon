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
import logging
import pytest
from .standard_lib.sample_generation.sample_xdist_generator import SampleXdistGenerator
import traceback
from .standard_lib import AppTestGenerator
from .standard_lib.cim_compliance import CIMReportPlugin
from filelock import FileLock

LOG_FILE = "pytest_splunk_addon.log"

test_generator = None


def pytest_configure(config):
    global test_generator
    """
    Setup configuration after command-line options are parsed
    """
    config.addinivalue_line(
        "markers", "splunk_searchtime_internal_errors: Check Errors in logs"
    )
    config.addinivalue_line(
        "markers", "splunk_searchtime_fields: Test search time fields only"
    )
    config.addinivalue_line(
        "markers",
        "splunk_searchtime_fields_positive: Test search time fields positive scenarios only",
    )
    config.addinivalue_line(
        "markers",
        "splunk_searchtime_fields_negative: Test search time fields negative scenarios only",
    )
    config.addinivalue_line(
        "markers", "splunk_searchtime_fields_tags: Test search time tags only"
    )
    config.addinivalue_line(
        "markers",
        "splunk_searchtime_fields_eventtypes: Test search time eventtypes only",
    )
    config.addinivalue_line(
        "markers",
        "splunk_searchtime_fields_savedsearches: Test search time savedsearches only",
    )
    config.addinivalue_line(
        "markers", "splunk_searchtime_cim: Test CIM compatibility only"
    )
    config.addinivalue_line(
        "markers", "splunk_searchtime_cim_fields: Test CIM required fields only"
    )
    config.addinivalue_line(
        "markers",
        "splunk_searchtime_cim_fields_not_allowed_in_props: Test CIM fields for mapped datamodels whose extractions should not be defined in the addon.",
    )
    config.addinivalue_line(
        "markers",
        "splunk_searchtime_cim_fields_not_allowed_in_search:  Test CIM fields for mapped datamodels which should not be extracted in splunk. i.e expected event count for the fields: 0",
    )
    config.addinivalue_line(
        "markers",
        "splunk_searchtime_cim_mapped_datamodel: Test an eventtype is mapped with only one data models",
    )
    config.addinivalue_line(
        "markers",
        "splunk_searchtime_requirements: Test an requirement test only  is mapped with only one data models",
    )
    if config.getoption("splunk_app", None):
        test_generator = AppTestGenerator(config)

    cim_report = config.getoption("cim_report")
    if cim_report and not hasattr(config, "slaveinput"):
        # prevent opening markdown on slave nodes (xdist)
        config._markdown = CIMReportPlugin(config)
        config.pluginmanager.register(config._markdown)


def pytest_unconfigure(config):
    markdown = getattr(config, "_markdown", None)
    if markdown:
        del config._markdown
        config.pluginmanager.unregister(markdown)


def pytest_sessionstart(session):

    SampleXdistGenerator.event_path = session.config.getoption("event_path")
    SampleXdistGenerator.event_stored = False
    SampleXdistGenerator.tokenized_event_source = session.config.getoption(
        "tokenized_event_source"
    ).lower()
    if (
        SampleXdistGenerator.tokenized_event_source == "store_new"
        and session.config.getoption("ingest_events").lower()
        in ["no", "n", "false", "f"]
        and session.config.getoption("execute_test").lower()
        in ["no", "n", "false", "f"]
    ):
        app_path = session.config.getoption("splunk_app")
        config_path = session.config.getoption("splunk_data_generator")
        store_events = session.config.getoption("store_events")
        sample_generator = SampleXdistGenerator(app_path, config_path)
        sample_generator.get_samples(store_events)


def pytest_generate_tests(metafunc):
    """
    Parse the fixture dynamically.
    """
    if metafunc.config.getoption("execute_test").lower() in ["no", "n", "false", "f"]:
        return
    global test_generator
    for fixture in metafunc.fixturenames:
        if fixture.startswith("splunk_searchtime") or fixture.startswith(
            "splunk_indextime"
        ):
            LOGGER.info(
                "generating testcases for splunk_app_searchtime. fixture=%s", fixture
            )

            try:
                # Load associated test data
                with FileLock("generator.lock"):
                    if test_generator is None:
                        test_generator = AppTestGenerator(metafunc.config)
                metafunc.parametrize(fixture, test_generator.generate_tests(fixture))
            except Exception as e:
                log_message = ""
                try:
                    with open(LOG_FILE) as log_f:
                        log_message = log_f.read()
                except Exception as log_err:
                    log_message = f"Could not capture the logs: {log_err}"
                log_message = "\n".join(log_message.split("\n")[-50:])
                raise type(e)(
                    f"{e}.\nStacktrace:\n{traceback.format_exc()}"
                    f"\nLogs:\n{log_message}"
                )


def pytest_collection_modifyitems(config, items):
    ingest_events_flag = config.getoption("ingest_events")
    is_ingest_false = ingest_events_flag.lower() in ["no", "n", "false", "f"]
    execute_test_flag = config.getoption("execute_test")
    if execute_test_flag.lower() in ["no", "n", "false", "f"]:
        for item in items.copy():
            item.add_marker(
                pytest.mark.skipif(
                    item.name != "test_events_with_untokenised_values"
                    or is_ingest_false,
                    reason=f"--execute-test={execute_test_flag} provided",
                )
            )


def init_pytest_splunk_addon_logger():
    """
    Configure file based logger for the plugin
    """
    fh = logging.FileHandler(LOG_FILE)
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(message)s"
    )
    fh.setFormatter(formatter)
    logger = logging.getLogger("pytest-splunk-addon")
    logger.addHandler(fh)
    logging.root.propagate = False
    logger.setLevel(logging.INFO)
    return logger


init_pytest_splunk_addon_logger()
LOGGER = logging.getLogger("pytest-splunk-addon")
