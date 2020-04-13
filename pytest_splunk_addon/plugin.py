import logging
import pytest
import sys
import traceback
from .standard_lib.app_test_generator import AppTestGenerator

LOG_FILE = 'pytest_splunk_addon.log'

def pytest_configure(config):
    """
    Setup configuration after command-line options are parsed
    """
    config.addinivalue_line("markers", "splunk_addon_internal_errors: Check Errors")
    config.addinivalue_line("markers", "splunk_addon_searchtime: Test search time only")


def pytest_generate_tests(metafunc):
    """
    Parse the fixture dynamically.
    """
    for fixture in metafunc.fixturenames:
        if fixture.startswith("splunk_app"):
            LOGGER.info("generating testcases for splunk_app. fixture=%s", fixture)

            try:
                # Load associated test data
                test_generator = AppTestGenerator(metafunc.config)
                metafunc.parametrize(fixture, test_generator.generate_tests(fixture))
            except Exception as e:
                log_message = ""
                try:
                    with open(LOG_FILE) as log_f:
                        log_message = log_f.read()
                except Exception as log_err:
                    log_message = f"Could not capture the logs: {log_err}"

                raise type(e)(f"{e}.\nStacktrace:\n{traceback.format_exc()}"
                              f"\nLogs:\n{log_message}"
                            )

def pytest_collection_modifyitems(items):
    """
    To mark the Test cases dynamically 
    """
    for item in items:
        if "splunk_app_cim" in item.fixturenames:
            field = item.callspec.params['splunk_app_cim']['field']
            if field.is_required:
                item.add_marker(pytest.mark.cim_required)
            elif field.is_recommended:
                item.add_marker(pytest.mark.cim_recommended)

def init_pytest_splunk_addon_logger():
    fh = logging.FileHandler(LOG_FILE)
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(message)s')
    fh.setFormatter(formatter)
    logger = logging.getLogger('pytest-splunk-addon')
    logger.addHandler(fh)
    logging.root.propagate = False
    logger.setLevel(logging.DEBUG)
    return logger

init_pytest_splunk_addon_logger()
LOGGER = logging.getLogger("pytest-splunk-addon")

