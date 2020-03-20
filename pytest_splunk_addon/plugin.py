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
from time import sleep
import re

logger = logging.getLogger()

@pytest.fixture(scope="session")
def docker_compose_files(pytestconfig):
    """Get an absolute path to the  `docker-compose.yml` file. Override this
    fixture in your tests if you need a custom location."""
    print(os.path.join(str(pytestconfig.invocation_dir), "docker-compose.yml"))

    return [os.path.join(str(pytestconfig.invocation_dir), "docker-compose.yml")]


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
