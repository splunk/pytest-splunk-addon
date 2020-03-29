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


def dedup_tests(test_list):
    """
    Deduplicate the test case parameters based on param.id
    Args:
        test_list(Generator): Generator of pytest.param
    Yields:
        Generator: De-duplicated pytest.param
    """
    seen_tests = set()
    for each_param in test_list:
        if each_param.id not in seen_tests:
            yield each_param
            seen_tests.add(each_param.id)


def pytest_generate_tests(metafunc):
    """
    Parse the fixture dynamically.
    """
    for fixture in metafunc.fixturenames:
        if fixture.startswith("splunk_app"):
            LOGGER.info("generating testcases for splunk_app. fixture=%s", fixture)
            # Load associated test data
            tests = load_splunk_tests(metafunc.config.getoption("splunk_app"), fixture)
            metafunc.parametrize(fixture, dedup_tests(tests))


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
    Parse the props.conf of the App & yield stanzas

    Args:
        props(splunk_appinspect.configuration_file.ConfigurationFile): The configuration object of props

    Yields:
        generator of stanzas from the props
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
            LOGGER.info(
                "Parsing %s parameter=%s of stanza=%s",
                stanza_type,
                current,
                stanza_name,
            )
            props_property = section.options[current]
            for each_stanza_name in stanza_list:
                if current.startswith("EXTRACT-"):
                    yield from return_props_extract(
                        stanza_type, each_stanza_name, props_property
                    )
                elif current.startswith("EVAL-"):
                    yield return_props_eval(
                        stanza_type, each_stanza_name, props_property
                    )


def return_props_extract(stanza_type, stanza_name, props_property):
    """
    Returns the fields parsed from EXTRACT as pytest parameters
    Args:
        stanza_type(str): stanza type (source/sourcetype)
        stanza_name(str): source/sourcetype name
        props_property(splunk_appinspect.configuration_file.ConfigurationSetting): The configuration setting object of EXTRACT.
            properties used:
                    name : key in the configuration settings
                    value : value of the respective name in the configuration
    Yields:
        generator of fields as pytest parameters
    """
    test_name = f"{stanza_name}::{props_property.name}"
    regex = r"\(\?<([^\>]+)\>(?:.*(?i)in\s+(.*))?"
    matches = re.finditer(regex, props_property.value, re.MULTILINE)
    fields = []
    for match_num, match in enumerate(matches, start=1):
        for group_num in range(0, len(match.groups())):
            group_num = group_num + 1
            if match.group(group_num):
                field_test_name = "{}_field::{}".format(
                    stanza_name, match.group(group_num)
                )
                yield pytest.param(
                    {
                        "stanza_type": stanza_type,
                        "stanza_name": stanza_name,
                        "fields": [match.group(group_num)],
                    },
                    id=field_test_name,
                )
                fields.append(match.group(group_num))
    if fields:
        fields.reverse()
        LOGGER.info(
            "Generated pytest.param for extract. stanza_type=%s stanza_name=%s, fields=%s",
            stanza_type,
            stanza_name,
            str(fields),
        )
        yield pytest.param(
            {"stanza_type": stanza_type, "stanza_name": stanza_name, "fields": fields},
            id=test_name,
        )


def return_props_eval(stanza_type, stanza_name, props_property):
    """
    Return the fields parsed from EVAL as pytest parameters

    Args:
        stanza_type: Stanza type (source/sourcetype)
        stanza_name(str): source/sourcetype name
        props_property(splunk_appinspect.configuration_file.ConfigurationSetting): The configuration setting object of eval
            properties used:
                name : key in the configuration settings
                value : value of the respective name in the configuration

    Return:
        List of pytest parameters
    """
    test_name = f"{stanza_name}::{props_property.name}"
    regex = r"EVAL-(?P<FIELD>.*)"
    fields = re.findall(regex, props_property.name, re.IGNORECASE)

    LOGGER.info(
        "Genrated pytest.param for eval. stanza_type=%s, stanza_name=%s, fields=%s",
        stanza_type,
        stanza_name,
        str(fields),
    )
    return pytest.param(
        {"stanza_type": stanza_type, "stanza_name": stanza_name, "fields": fields},
        id=test_name,
    )


def get_list_of_sources(source):
    """
    Implement generator object of source list

    Args:
        source(str): Source name

    Yields:
        generator of source name
    """
    match_obj = re.search(r"source::(.*)", source)
    value = match_obj.group(1).replace("...", "*")
    sub_groups = re.findall("\([^\)]+\)", value)
    sub_group_list = []
    for each_group in sub_groups:
        sub_group_list.append(each_group.strip("()").split("|"))
    template = re.sub(r"\([^\)]+\)", "{}", value)
    for each_permutation in product(*sub_group_list):
        yield template.format(*each_permutation)
