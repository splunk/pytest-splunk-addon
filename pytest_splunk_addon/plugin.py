# -*- coding: utf-8 -*-
"""
Module usage:
- splunk_appinspect: To parse the configuration files from Add-on package
"""

import logging
import re
import pytest
from splunk_appinspect import App
from itertools import product

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
            LOGGER.info("parsing source stanza=%s", props_section)
            list_of_sources = []
            list_of_sources = list(get_list_of_sources(props_section))
            for props_source in list_of_sources: 
                yield return_props_stanza_param(props_section, props_source, "source")
        else:
            LOGGER.info("parsing sourcetype stanza=%s", props_section)
            yield return_props_stanza_param(props_section, props_section, "sourcetype")


def return_props_stanza_param(stanza_id, stanza_value, stanza_type):
    """
    Convert sourcetype/source to pytest parameters
    """
    if stanza_type == "sourcetype":
        idf = f"sourcetype::{stanza_id}"
    else:
        idf = f"{stanza_id}"
    return pytest.param({"field": stanza_type, "value": stanza_value}, id=idf)


def load_splunk_fields(props):
    """
    Parse the App configuration files & yield fields

    Args:
        props(): The configuration object of props

    Yields:
        generator of fields
    """
    for stanza_name in props.sects:
        section = props.sects[stanza_name]
        if section.name.startswith("source::"):
            stanza_type = "source"
            stanza_list = list(get_list_of_sources(stanza_name))
        else:
            stanza_type = "sourcetype"
            stanza_list = [stanza_name]
        for current in section.options:
            LOGGER.info("Parsing parameter=%s of stanza=%s", current, props_section)
            field_data = section.options[current]
            for stanza_name in stanza_list:
                if current.startswith("EXTRACT-"):
                    yield return_props_extract(stanza_name, field_data, stanza_type)
                elif current.startswith("EVAL-"):
                    yield return_props_eval(stanza_name, field_data, stanza_type)
                elif current.startswith("sourcetype"):   
                    # Sourcetype assignment configuration
                    yield return_props_sourcetype(stanza_name, field_data, stanza_type)


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


def return_props_sourcetype(stanza_name, field_data, stanza_type):
    '''
    Return the fields parsed from sourcetype as pytest parameters
      
    Args:
        @stanza_name(str): source/sourcetype name
        @field_data(object): sourcetype field details
        @stanza_type: Stanza type (source/sourcetype)

    Return:
        List of pytest parameters
    '''
    name = f"{stanza_name}::{field_data.value}"
    fields = [field_data.name]
    LOGGER.info("Generated pytest.param for sourcetype. stanza_type=%s, stanza_name=%s, fields=%s", stanza_type, stanza_name, str(fields))
    return pytest.param({'stanza_type': stanza_type, 'stanza_name': stanza_name, 'fields': fields}, id=name)

def get_list_of_sources(source):
    '''
    Implement generator object of source list
      
    Args:
        @param source(str): Source name
    '''
    match_obj = re.search(r"source::(.*)", source)
    value = match_obj.group(1).replace("...", "*")
    sub_groups = re.findall("\([^\)]+\)", value)
    sub_group_list = []
    for each_group in sub_groups:
        sub_group_list.append(list(each_group.strip("()").split("|")))
    template = re.sub(r'\([^\)]+\)', "{}",value)
    for each_permutation in product(*sub_group_list):
        yield template.format(*each_permutation)
