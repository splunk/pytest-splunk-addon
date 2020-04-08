import logging
import pytest
from .standard_lib.app_test_generator import AppTestGenerator

LOGGER = logging.getLogger("pytest_splunk_addon")

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

            # Load associated test data
            test_generator = AppTestGenerator(metafunc.config)
            metafunc.parametrize(fixture, test_generator.generate_tests(fixture))


def pytest_collection_modifyitems(items):
    for item in items:
        if "splunk_app_cim" in item.fixturenames:
            field = item.callspec.params['splunk_app_cim']['field']
            if field.is_required:
                item.add_marker(pytest.mark.cim_required)
            elif field.is_recommended:
                item.add_marker(pytest.mark.cim_recommended)