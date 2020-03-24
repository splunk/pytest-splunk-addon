# -*- coding: utf-8 -*-

import logging
import os
import pytest
import requests
from splunk_appinspect import App

from .helmut.manager.jobs import Jobs
from .helmut.splunk.cloud import CloudSplunk
from .helmut_lib.SearchUtil import SearchUtil

import pytest
import requests
import urllib3
import splunklib.client as client
import re

logger = logging.getLogger()


def pytest_configure(config):
    config.addinivalue_line("markers", "splunk_addon_internal_errors: Check Errors")
    config.addinivalue_line("markers", "splunk_addon_searchtime: Test search time only")


def pytest_generate_tests(metafunc):
    for fixture in metafunc.fixturenames:
        if fixture.startswith("splunk_app"):
            # Load associated test data
            tests = load_splunk_tests(metafunc.config.getoption("splunk_app"), fixture)
            if tests:
                metafunc.parametrize(fixture, tests)


def load_splunk_tests(splunk_app_path, fixture):
    app = App(splunk_app_path, python_analyzer_enable=False)
    if fixture.endswith("props"):
        props = app.props_conf()
        yield from load_splunk_props(props)
    elif fixture.endswith("fields"):
        props = app.props_conf()
        yield from load_splunk_fields(props)
    elif fixture.endswith("eventtypes"):
        eventtypes = app.eventtypes_conf()
        yield from load_splunk_eventtypes(eventtypes)
    else:
        yield None


def load_splunk_props(props):
    for p in props.sects:
        if p.startswith("host::"):
            continue
        elif p.startswith("source::"):
            continue
        else:
            yield return_props_sourcetype_param(p, p)


def return_props_sourcetype_param(id, value):
    idf = f"sourcetype::{id}"
    return pytest.param({"field": "sourcetype", "value": value}, id=idf)


def load_splunk_fields(props):
    for p in props.sects:
        section = props.sects[p]
        for current in section.options:
            options = section.options[current]
            if current.startswith("EXTRACT-"):
                yield return_props_extract(p, options)


def return_props_extract(id, value):
    name = f"{id}_field::{value.name}"

    regex = r"\(\?<([^\>]+)\>"
    matches = re.finditer(regex, value.value, re.MULTILINE)
    fields = []
    for matchNum, match in enumerate(matches, start=1):
        for groupNum in range(0, len(match.groups())):
            groupNum = groupNum + 1

            fields.append(match.group(groupNum))

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