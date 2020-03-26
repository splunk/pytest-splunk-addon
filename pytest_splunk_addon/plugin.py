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
import csv

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
        yield from load_splunk_fields(app, props, splunk_app_path)
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


def load_splunk_fields(app, props, splunk_app_path):
    """
    Parse the App configuration files & yield fields
    Args:
        app(object): App Inspect object for current app
        props(): The configuration object of props
        splunk_app_path (str): Local system filepath to lookup to be examined
    Yields:
        generator of fields
    """
    for props_section in props.sects:
        section = props.sects[props_section]
        for current in section.options:
            options = section.options[current]
            if current.startswith("EXTRACT-"):
                yield return_props_extract(props_section, options)
            if re.match('LOOKUP', current, re.IGNORECASE) is not None:
                yield return_lookup_extract(props_section, options, app, splunk_app_path)


def return_props_extract(id, value):
    """
    Returns the fields parsed from EXTRACT as pytest parameters
    Args:
        id(str): parameter from the stanza
        value(str): value of the parmeter
    Yields:
        List of pytest parameters containing fields
    """
    extract_test_name = f"{id}_field::{value.name}"

    regex = r"\(\?<([^\>]+)\>"
    matches = re.finditer(regex, value.value, re.MULTILINE)
    fields = []
    for matchNum, match in enumerate(matches, start=1):
        for groupNum in range(0, len(match.groups())):
            groupNum = groupNum + 1

            fields.append(match.group(groupNum))

    return pytest.param({"sourcetype": id, "fields": fields}, id=extract_test_name)

def get_lookup_fields(lookup_str):
    """
    Returns the fields parsed from the lookup string value
    Args:
        lookup_str(str): The string for the lookup KO, that we want to parse
    returns(dict):
        lookup_stanza(str): The stanza name for the lookup in question in transforms.conf
        input_fields(list): The fields in the input of the lookup
        output_fields(list): The fields in the output of the lookup
        output_flag(bool): Whether or not the lookup has a OUTPUT or OUTPUTNEW keyword in it
    """
    
    lookup_str = re.split(', | ', re.sub(' +', ' ', lookup_str))
    lookup_stanza = lookup_str[0]
    output_flag = False
    skip = 0
    input_list = []
    output_list = []

    # Parse out the fields we want from the props.conf lookup setting
    for iterator in range(1, len(lookup_str)):
        if skip > 0:
            skip -= 1
            continue

        if lookup_str[iterator] == "OUTPUT" or lookup_str[iterator] == "OUTPUTNEW":
            output_flag = True
            continue

        if output_flag is False:
            if iterator + 2 < len(lookup_str) and re.match("as", lookup_str[iterator+1], re.IGNORECASE) is not None:
                input_list.append(lookup_str[iterator+2].strip())
                skip = 2
                continue
            else:
                input_list.append(lookup_str[iterator].strip())
        else:
            if iterator + 2 < len(lookup_str) and re.match("as", lookup_str[iterator+1], re.IGNORECASE) is not None:
                output_list.append(lookup_str[iterator+2].strip())
                skip = 2
                continue
            else:
                output_list.append(lookup_str[iterator].strip())
    return {"input_fields": input_list, "output_fields": output_list, "lookup_stanza": lookup_stanza, "output_flag": output_flag}


def return_lookup_extract(id, value, app, splunk_app_path):
    """
    This extracts the lookup fields in which we will use for testing later on.

    Args:
        id(str): parameter from the stanza
        value(str): value of the parameter
        app(object): App Inspect object for current app
        splunk_app_path (str): Local system filepath to lookup to be examined

    Variables:
        name(str): The id of the test created
        string(list(str)): The string of the lookup value
        lookup_stanza(str): The stanza in transforms.conf corresponding to the lookup
        lookup_file(str): The name of the lookup fole that is being used
        output_flag(bool): A boolean to check when and if the lookup has a output argument
        skip(int): How many times we want our iterator to skip over the string
        lookup_field_list(list): The list of lookup fields we want to return
        transforms(object): Splunk app object/dictionary holding information of the apps transforms.conf file

    returns:
        List of pytest parameters containing fields
    """
    name = f"{id}lookup::{value.name}"
    fields = get_lookup_fields(value.value)
    lookup_field_list = fields["input_fields"] + fields["output_fields"]
    transforms = app.transforms_conf()

    # If the OUTPUT or OUTPUTNEW argument is never used, then get the fields from the csv file
    if fields["output_flag"] is False:
        for stanzas in transforms.sects:
            stanza = transforms.sects[stanzas]
            if(stanza.name == fields["lookup_stanza"]):
                for current in stanza.options:
                    if stanza.options[current].name == 'filename':
                        lookup_file = stanza.options[current].value
        try:
            location = os.path.join(splunk_app_path, "lookups", lookup_file)
            with open(location, "rU") as csvfile:
                reader = csv.DictReader(csvfile)
                fieldnames = reader.fieldnames
                for items in fieldnames:
                    lookup_field_list.append(items.strip())
                csvfile.close()
        # If there is an error. the test should fail with the current fields
        # This makes sure the test doesn't exit prematurely
        except (OSError, IOError, UnboundLocalError):
            pass
    return pytest.param({"sourcetype": id, "fields": lookup_field_list}, id=name)
