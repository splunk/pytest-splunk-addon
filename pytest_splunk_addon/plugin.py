# -*- coding: utf-8 -*-
"""
Module usage:
- splunk_appinspect: To parse the configuration files from Add-on package
"""

import logging
import re
import pytest
from splunk_appinspect import App

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
            tests = load_splunk_tests(metafunc.config.getoption("splunk_app"), fixture)
            metafunc.parametrize(fixture, tests)


def load_splunk_tests(splunk_app_path, fixture):
    """
    Utility function to load the test cases with the App fields

    Args:
        splunk_app_path(string): Path of the Splunk App
        fixture: The list of fixtures

    Yields:
        List of knowledge objects as pytest parameters
    """
    LOGGER.info("Initializing App parsing mechanism.")
    app = App(splunk_app_path, python_analyzer_enable=False)
    if fixture.endswith("props"):
        props = app.props_conf()
        LOGGER.info("Successfully parsed props configurations")
        yield from load_splunk_props(props)
    elif fixture.endswith("fields"):
        props = app.props_conf()
        LOGGER.info("Successfully parsed props configurations")
        yield from load_splunk_fields(props)
    elif fixture.endswith("eventtypes"):
        eventtypes = app.eventtypes_conf()
        yield from load_splunk_eventtypes(eventtypes)
    else:
        yield None


def load_splunk_props(props):
    """
    Parse the props.conf of the App & yield stanzas

    Args:
        props(): The configuration object of props

    Yields:
        generator of stanzas from the props
    """
    for props_section in props.sects:
        if props_section.startswith("host::"):
            LOGGER.info("Skipping host:: stanza=%s", props_section)
            continue
        elif props_section.startswith("source::"):
            LOGGER.info("Skipping source:: stanza=%s", props_section)
            continue
        else:
            LOGGER.info("parsing sourcetype stanza=%s", props_section)
            yield return_props_sourcetype_param(props_section, props_section)


def return_props_sourcetype_param(id, value):
    """
    Convert sourcetype to pytest parameters
    """
    idf = f"sourcetype::{id}"
    LOGGER.info("Generated pytest.param of sourcetype with id=%s", idf)
    return pytest.param({"field": "sourcetype", "value": value}, id=idf)


def load_splunk_fields(props):
    """
    Parse the App configuration files & yield fields

    Args:
        props(): The configuration object of props

    Yields:
        generator of fields
    """
    for props_section in props.sects:
        section = props.sects[props_section]
        for current in section.options:
            LOGGER.info("Parsing parameter=%s of stanza=%s", current, props_section)
            options = section.options[current]
            if current.startswith("EXTRACT-"):
                yield return_props_extract(props_section, options)


def return_props_extract(id, value):
    """
    Returns the fields parsed from EXTRACT as pytest parameters

    Args:
        id(str): parameter from the stanza
        value(str): value of the parmeter

    Returns:
        List of pytest parameters
    """
    name = f"{id}_field::{value.name}"

    regex = r"\(\?<([^\>]+)\>"
    matches = re.finditer(regex, value.value, re.MULTILINE)
    fields = []
    for matchNum, match in enumerate(matches, start=1):
        for groupNum in range(0, len(match.groups())):
            groupNum = groupNum + 1

            fields.append(match.group(groupNum))
    LOGGER.info("Genrated pytest.param for extract. stanza_name=%s, fields=%s", id, str(fields))
    return pytest.param({"sourcetype": id, "fields": fields}, id=name)

def load_splunk_eventtypes(eventtypes):
    """
    Parse the App configuration files & yield eventtypes
    Args:
        eventtypes(): The configuration object of eventtypes.conf
    Yields:
        generator of list of eventtypes
    """

    for eventtype_section in eventtypes.sects:
        yield return_eventtypes_param(eventtype_section, eventtype_section)
            
def return_eventtypes_param(id, value):

    """
    Returns the eventtype parsed from the eventtypes.conf file as pytest parameters
    Args:
        id(str): parameter from the stanza
        value(str): value of the parmeter
    Returns:
        List of pytest parameters
    """
    regex = r"(^[a-zA-Z_]+)(-%[a-zA-Z]+%)+$"
    result = re.match(regex, value)

    if result:
        value = "{}{}".format(result.group(1),'-*')

    idf = f"eventtype::{id}" 
    return pytest.param({
        "field": "eventtype", "value": value},
        id=idf
        )