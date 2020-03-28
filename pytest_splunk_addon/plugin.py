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
    Get list of lookup fields by parsing the lookup string.
    If a field is aliased to another field, take the aliased field into consideration

    Args:
        lookup_str(str): Lookup string from props.conf
    returns(dict):
        lookup_stanza(str): The stanza name for the lookup in question in transforms.conf
        input_fields(list): The fields in the input of the lookup
        output_fields(list): The fields in the output of the lookup
        output_flag(bool): Whether or not the lookup has a OUTPUT or OUTPUTNEW keyword in it
    """

    input_output_field_list = []
    lookup_stanza = lookup_str.split(" ")[0]
    lookup_str = " ".join(lookup_str.split(" ")[1:])
    output_flag = False
    if " OUTPUT " in lookup_str or " OUTPUTNEW " in lookup_str:
        output_flag = True

    # 0: Take the left side of the OUTPUT as input fields
    # -1: Take the right side of the OUTPUT as output fields
    for input_output_index in [0, -1]:
        if " OUTPUT " not in lookup_str and " OUTPUTNEW " not in lookup_str:
            lookup_str += " OUTPUT "

        # Take input fields or output fields depending on the input_output_index
        input_output_str = lookup_str.split(" OUTPUT ")[input_output_index].split(" OUTPUTNEW ")[input_output_index]

        
        field_parser = r"(\"(?:\\\"|[^\"])*\"|\'(?:\\\'|[^\'])*\'|[^\s,]+)\s*(?:[aA][sS]\s*(\"(?:\\\"|[^\"])*\"|\'(?:\\\'|[^\'])*\'|[^\s,]+))?"
        # field_groups: Group of max 2 fields - (source, destination) for "source as destination"
        field_groups = re.findall(field_parser, input_output_str)

        field_list = []
        # Take the last non-empty field from a field group.
        # Taking last non-empty field ensures that the aliased value will have
        # higher priority
        for each_group in field_groups:
            field_list.append([each_field for each_field in reversed(each_group) if each_field][0])

        input_output_field_list.append(field_list)

    return {"input_fields": input_output_field_list[0], "output_fields": input_output_field_list[1], "lookup_stanza": lookup_stanza, "output_flag": output_flag}


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
    skip = False
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
            with open(location, "r") as csvfile:
                reader = csv.DictReader(csvfile)
                fieldnames = reader.fieldnames
                for items in fieldnames:
                    if items not in lookup_field_list:
                        lookup_field_list.append(items.strip())
                csvfile.close()
        # If there is an error. the test should fail with the current fields
        # This makes sure the test doesn't exit prematurely
        except (OSError, IOError, UnboundLocalError, TypeError):
            skip = True
    if(skip):
        return None
    else:
        return pytest.param({"sourcetype": id, "fields": lookup_field_list}, id=name)