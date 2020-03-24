# -*- coding: utf-8 -*-

import logging
import os
import pytest
import requests
from splunk_appinspect import App
from pytest_splunk_addon.splunk import *
from itertools import product

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
    for stanza_name in props.sects:
        section = props.sects[stanza_name]
        if section.name.startswith("source::"):
            stanza_type = "source"
            stanza_list = list(get_list_of_sources(stanza_name))
        else:
            stanza_type = "sourcetype"
            stanza_list = [stanza_name]
        for current in section.options:
            field_data = section.options[current]
            for stanza_name in stanza_list:
                if current.startswith("EXTRACT-"):
                    yield return_props_extract(stanza_name, field_data, stanza_type)
                elif current.startswith("EVAL-"):
                    yield return_props_eval(stanza_name, field_data, stanza_type)

def return_props_extract(stanza_name, value, stanza_type):
    name = f"{stanza_name}_field::{value.name}"

    regex = r"\(\?<([^\>]+)\>"
    matches = re.finditer(regex, value.value, re.MULTILINE)
    fields = []
    for matchNum, match in enumerate(matches, start=1):
        for groupNum in range(0, len(match.groups())):
            groupNum = groupNum + 1

            fields.append(match.group(groupNum))

    return pytest.param({'stanza_type': stanza_type, "stanza_name": stanza_name, "fields": fields}, id=name)

def return_props_eval(stanza_name, field_data, stanza_type):
    '''
    Return the fields parsed from EVAL as pytest parameters
      
    Args:
        @stanza_name(str): source/sourcetype name
        @field_data(object): Eval field details
        @stanza_type: Stanza type (source/sourcetype)

    Return:
        List of pytest parameters
    '''
    name = f"{stanza_type}_{stanza_name}_field::{field_data.name}"
    regex = r"EVAL-(?P<FIELD>.*)"
    fields = re.findall(regex, field_data.name, re.IGNORECASE)

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
