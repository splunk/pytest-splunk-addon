import logging
import pytest
import sys
import traceback
from .standard_lib import AppTestGenerator

LOG_FILE = 'pytest_splunk_addon.log'

def pytest_configure(config):
    """
    Setup configuration after command-line options are parsed
    """
    config.addinivalue_line("markers", "splunk_app_internal_errors: Check Errors in logs")
    config.addinivalue_line("markers", "splunk_app_searchtime: Test search time only")
    config.addinivalue_line("markers", "splunk_app_fields: Test search time fields only")
    config.addinivalue_line("markers", "splunk_app_negative: Test search time negative scenarios only")
    config.addinivalue_line("markers", "splunk_app_tags: Test search time tags only")
    config.addinivalue_line("markers", "splunk_app_eventtypes: Test search time eventtypes only")
    config.addinivalue_line("markers", "splunk_app_cim: Test CIM compatibility only")
    config.addinivalue_line("markers", "splunk_app_cim_fields: Test CIM required fields only")


def pytest_generate_tests(metafunc):
    """
    Parse the fixture dynamically.
    """
    test_generator = None
    for fixture in metafunc.fixturenames:
        if fixture.startswith("splunk_app"):
            LOGGER.info("generating testcases for splunk_app. fixture=%s", fixture)

            try:
                # Load associated test data
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
                raise type(e)(f"{e}.\nStacktrace:\n{traceback.format_exc()}"
                              f"\nLogs:\n{log_message}"
                            )


def init_pytest_splunk_addon_logger():
    """
    Configure file based logger for the plugin
    """
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

