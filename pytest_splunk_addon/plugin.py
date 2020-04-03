# -*- coding: utf-8 -*-
"""
Module usage:
- splunk_appinspect: To parse the configuration files from Add-on package
"""
import os
import logging
import re
import pytest
import csv
from urllib.parse import unquote
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
        transforms = app.transforms_conf()
        LOGGER.info("Successfully parsed props configurations")
        yield from load_splunk_fields(app, props, transforms)
    elif fixture.endswith("tags"):
        tags = app.get_config("tags.conf")
        yield from load_splunk_tags(tags)
    elif fixture.endswith("eventtypes"):
        eventtypes = app.eventtypes_conf()
        LOGGER.info("Successfully parsed eventtypes configurations")
        yield from load_splunk_eventtypes(eventtypes)
    else:
        yield None


def load_splunk_tags(tags):
    """
    Parse the tags.conf of the App & yield stanzas

    Args:
        tags(splunk_appinspect.configuration_file.ConfigurationFile):
            The configuration object of tags.

    Yields:
        generator of stanzas from the tags
    """
    for stanza in tags.sects:
        kv = tags.sects[stanza]
        stanza = stanza.replace("=", '="')
        stanza += '"'
        for key in kv.options:
            tags_property = kv.options[key]
            yield return_tags(tags_property, unquote(stanza))


def return_tags(tags_property, stanza_name):
    """
    Returns the fields parsed from tags as pytest parameters

    Args:
        stanza_name(str): Name of Stanza
        tags_property(
            splunk_appinspect.configuration_file.ConfigurationSetting
            ):
                The configuration setting object of tags.
                properties used:
                    name : key in the configuration settings
                    value : value of the respective name in the configuration

    Returns:
        List of pytest parameters
    """
    return pytest.param(
        {"tag_query": stanza_name, tags_property.value + "_tag": tags_property.name,},
        id=stanza_name + " | " + tags_property.name + "=" + tags_property.value,
    )


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
            LOGGER.info("Parsing source stanza=%s", props_section)
            for props_source in list(get_list_of_sources(props_section)):
                yield return_props_stanza_param(props_section, props_source, "source")
        else:
            LOGGER.info("parsing sourcetype stanza=%s", props_section)
            yield return_props_stanza_param(props_section, props_section, "sourcetype")


def return_props_stanza_param(stanza_id, stanza_value, stanza_type):
    """
    Convert sourcetype/source to pytest parameters

    Args:
        stanza_id: source/sourcetype field details
        stanza_value(str): source/sourcetype value
        stanza_type: Stanza type (source/sourcetype)
    Return:
        List of pytest parameters
    """
    if stanza_type == "sourcetype":
        test_name = f"sourcetype::{stanza_id}"
    else:
        test_name = f"{stanza_id}"
    LOGGER.info(
        (
            "Generated pytest.param for source/sourcetype."
            "stanza_type=%s, stanza_value=%s, stanza_id=%s"
        ),
        stanza_type,
        stanza_value,
        str(test_name),
    )
    return pytest.param({"field": stanza_type, "value": stanza_value}, id=test_name)


def load_splunk_fields(app, props, transforms):
    """
    Parse the props.conf of the App & yield stanzas

    Args:
        props(
            splunk_appinspect.configuration_file.ConfigurationFile
            ): The configuration object of props
        transforms(
            splunk_appinspect.configuration_file.ConfigurationFile
            ): The configuration object of transforms
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
                elif current.startswith("FIELDALIAS-"):
                    yield from return_props_field_alias(
                        stanza_type, each_stanza_name, props_property
                    )
                elif current.startswith("sourcetype"):
                    # Sourcetype assignment configuration
                    yield return_props_sourcetype(
                        stanza_type, each_stanza_name, props_property
                    )
                elif current.startswith("REPORT-"):
                    yield from return_transforms_report(
                        transforms, stanza_type, each_stanza_name, props_property,
                    )
                elif re.match("LOOKUP", current, re.IGNORECASE):
                    yield from return_props_lookup(
                        stanza_type, each_stanza_name, props_property, app
                    )


def get_params_from_regex(regex, property_value, stanza_type, stanza_name, fields):
    """
    Returns the fields captured using regex as pytest parameters

    Args:
        regex(str):
            The regular expression used to capture the fields
        property_value(str):
            The property string on which regex will be applied to extract fields.
        stanza_type(str):
            stanza type (source/sourcetype)
        stanza_name(str):
            source/sourcetype name
        fields(list):
            list of fields preset in a props property.

    Yields:
        generator of fields as pytest parameters
    """
    matches = re.finditer(regex, property_value, re.MULTILINE)
    for matchNum, match in enumerate(matches, start=1):
        for groupNum in range(0, len(match.groups())):
            groupNum = groupNum + 1
            field_test_name = "{}_field::{}".format(stanza_name, match.group(groupNum))
            yield pytest.param(
                {
                    "stanza_type": stanza_type,
                    "stanza_name": stanza_name,
                    "fields": [match.group(groupNum)],
                },
                id=field_test_name,
            )
            fields.append(match.group(groupNum))


def return_transforms_report(transforms, stanza_type, stanza_name, report_property):
    """
    Returns the fields parsed from transforms.conf  as pytest parameters

    Args:
        transforms(): The configuration object of transforms
        stanza_type(str): stanza type (source/sourcetype)
        stanza_name(str): source/sourcetype name
        report_property(splunk_appinspect.configuration_file.ConfigurationSetting): The configuration setting object of REPORT.
            properties used:
                    name : key in the configuration settings
                    value : value of the respective name in the configuration
    Yields:
        generator of fields as pytest parameters
    """
    try:
        for transforms_section in [
            each_stanza.strip() for each_stanza in report_property.value.split(",")
        ]:
            report_test_name = (
                f"{stanza_name}::{report_property.name}::{transforms_section}"
            )
            fields = []
            section = transforms.sects[transforms_section]
            if (
                "SOURCE_KEY" in section.options
                and section.options["SOURCE_KEY"].value != ""
            ):
                yield pytest.param(
                    {
                        "stanza_type": stanza_type,
                        "stanza_name": stanza_name,
                        "fields": [section.options["SOURCE_KEY"].value],
                    },
                    id="{}_field::{}".format(
                        stanza_name, section.options["SOURCE_KEY"].value
                    ),
                )
                fields.append(section.options["SOURCE_KEY"].value)
            if "REGEX" in section.options and section.options["REGEX"].value != "":
                regex = r"\(\?P?(?:[<'])([^\>'\s]+)[\>']"
                yield from get_params_from_regex(
                    regex,
                    section.options["REGEX"].value,
                    stanza_type,
                    stanza_name,
                    fields,
                )
            if "FIELDS" in section.options and section.options["FIELDS"].value != "":
                fields_list = [
                    each_field.strip()
                    for each_field in section.options["FIELDS"].value.split(",")
                ]
                for each_field in fields_list:
                    yield pytest.param(
                        {
                            "stanza_type": stanza_type,
                            "stanza_name": stanza_name,
                            "fields": [each_field],
                        },
                        id="{}_field::{}".format(stanza_name, each_field),
                    )
                    fields.append(each_field)
            if "FORMAT" in section.options and section.options["FORMAT"].value != "":
                regex = r"(\S*)::"
                yield from get_params_from_regex(
                    regex,
                    section.options["FORMAT"].value,
                    stanza_type,
                    stanza_name,
                    fields,
                )
            yield pytest.param(
                {
                    "stanza_type": stanza_type,
                    "stanza_name": stanza_name,
                    "fields": fields,
                },
                id=report_test_name,
            )
    except KeyError:
        LOGGER.error(
            "The stanza {} doesnot exists in transforms.conf.".format(
                transforms_section
            ),
        )


def return_props_extract(stanza_type, stanza_name, props_property):
    """
    Returns the fields parsed from EXTRACT as pytest parameters
    Args:
        stanza_type(str): stanza type (source/sourcetype)
        stanza_name(str): source/sourcetype name
        props_property(
            splunk_appinspect.configuration_file.ConfigurationSetting
            ): The configuration setting object of EXTRACT.
            properties used:
                    name : key in the configuration settings
                    value : value of the respective name in the configuration
    Yields:
        generator of fields as pytest parameters
    """
    test_name = f"{stanza_name}::{props_property.name}"
    regex = r"\(\?P?(?:[<'])([^\>'\s]+)[\>']"
    fields = []
    yield from get_params_from_regex(
        regex, props_property.value, stanza_type, stanza_name, fields,
    )
    # If SOURCE_KEY is used in EXTRACT, generate the test for the same.
    regex_for_source_key = r"(?:(?i)in\s+(\w+))\s*$"
    extract_source_key = re.search(
        regex_for_source_key, props_property.value, re.MULTILINE
    )
    if extract_source_key:
        yield pytest.param(
            {
                "stanza_type": stanza_type,
                "stanza_name": stanza_name,
                "fields": extract_source_key.group(1),
            },
            id="{}_field::{}".format(stanza_name, extract_source_key.group(1)),
        )
        fields.insert(0, extract_source_key.group(1))
    if fields:
        LOGGER.info(
            "(Generated pytest.param for extract."
            "stanza_type=%s stanza_name=%s, fields=%s)",
            stanza_type,
            stanza_name,
            str(fields),
        )
        yield pytest.param(
            {"stanza_type": stanza_type, "stanza_name": stanza_name, "fields": fields,},
            id=test_name,
        )


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
    """

    input_output_field_list = []
    lookup_stanza = lookup_str.split(" ")[0]
    lookup_str = " ".join(lookup_str.split(" ")[1:])

    # 0: Take the left side of the OUTPUT as input fields
    # -1: Take the right side of the OUTPUT as output fields
    for input_output_index in [0, -1]:
        if " OUTPUT " not in lookup_str and " OUTPUTNEW " not in lookup_str:
            lookup_str += " OUTPUT "

        # Take input fields or output fields depending on the input_output_index
        input_output_str = lookup_str.split(" OUTPUT ")[input_output_index].split(
            " OUTPUTNEW "
        )[input_output_index]

        field_parser = r"(\"(?:\\\"|[^\"])*\"|\'(?:\\\'|[^\'])*\'|[^\s,]+)\s*(?:[aA][sS]\s*(\"(?:\\\"|[^\"])*\"|\'(?:\\\'|[^\'])*\'|[^\s,]+))?"
        # field_groups: Group of max 2 fields - (source, destination) for "source as destination"
        field_groups = re.findall(field_parser, input_output_str)

        field_list = []
        # Take the last non-empty field from a field group.
        # Taking last non-empty field ensures that the aliased value will have
        # higher priority
        for each_group in field_groups:
            field_list.append(
                [each_field for each_field in reversed(each_group) if each_field][0]
            )

        input_output_field_list.append(field_list)

    return {
        "input_fields": input_output_field_list[0],
        "output_fields": input_output_field_list[1],
        "lookup_stanza": lookup_stanza,
    }


def return_props_lookup(stanza_type, stanza_name, props_property, app):
    """
    This extracts the lookup fields in which we will use for testing later on.

    Args:
        stanza_type: Stanza type (source/sourcetype)
        stanza_name(str): source/sourcetype name
        props_property(splunk_appinspect.configuration_file.ConfigurationSetting):
            The configuration setting object of eval
            properties used:
                name : key in the configuration settings
                value : value of the respective name in the configuration
        app(object): App Inspect object for current app

    Variables:
        test_name(str): The id of the test created
        lookup_stanza(str): The stanza in transforms.conf corresponding to the lookup
        lookup_file(str): The name of the lookup file that is being used
        lookup_field_list(list): The list of lookup fields we want to return
        transforms(object): Splunk app object/dictionary holding information of the apps transforms.conf file

    returns:
        List of pytest parameters containing fields
    """
    test_name = f"{stanza_name}::{props_property.name}"
    parsed_fields = get_lookup_fields(props_property.value)
    lookup_field_list = parsed_fields["input_fields"] + parsed_fields["output_fields"]
    transforms = app.transforms_conf()

    # If the OUTPUT or OUTPUTNEW argument is never used, then get the fields from the csv file
    if not parsed_fields["output_fields"]:

        if parsed_fields["lookup_stanza"] in transforms.sects:
            stanza = transforms.sects[parsed_fields["lookup_stanza"]]
            if "filename" in stanza.options:
                lookup_file = stanza.options["filename"].value
                try:
                    location = os.path.join(
                        app.package.working_app_path, "lookups", lookup_file
                    )
                    with open(location, "r") as csv_file:
                        reader = csv.DictReader(csv_file)
                        fieldnames = reader.fieldnames
                        for items in fieldnames:
                            items = items.strip()
                            if items not in lookup_field_list:
                                lookup_field_list.append(items.strip())
                # If there is an error. the test should fail with the current fields
                # This makes sure the test doesn't exit prematurely
                except (OSError, IOError, UnboundLocalError, TypeError) as e:
                    LOGGER.info(
                        "Could not read the lookup file, skipping test. error=%s",
                        str(e),
                    )

    # Test individual fields
    for each_field in lookup_field_list:
        field_test_name = f"{stanza_name}_field::{each_field}"
        yield pytest.param(
            {
                "stanza_type": stanza_type,
                "stanza_name": stanza_name,
                "fields": [each_field],
            },
            id=field_test_name,
        )

    # Test Lookup as a whole
    yield pytest.param(
        {
            "stanza_type": stanza_type,
            "stanza_name": stanza_name,
            "fields": lookup_field_list,
        },
        id=test_name,
    )


def return_props_eval(stanza_type, stanza_name, props_property):
    """
    Return the fields parsed from EVAL as pytest parameters

    Args:
        stanza_type: Stanza type (source/sourcetype)
        stanza_name(str): source/sourcetype name
        props_property(
            splunk_appinspect.configuration_file.ConfigurationSetting
            ): The configuration setting object of eval
            properties used:
                name : key in the configuration settings
                value : value of the respective name in the configuration

    Return:
        List of pytest parameters
    """
    regex = r"EVAL-(?P<FIELD>.*)"
    fields = re.findall(regex, props_property.name, re.IGNORECASE)

    LOGGER.info(
        (
            "Generated pytest.param for eval. stanza_type=%s,"
            "stanza_name=%s, fields=%s"
        ),
        stanza_type,
        stanza_name,
        str(fields),
    )
    test_name = f"{stanza_name}_field::{fields[0]}"
    return pytest.param(
        {"stanza_type": stanza_type, "stanza_name": stanza_name, "fields": fields,},
        id=test_name,
    )


def return_props_sourcetype(stanza_type, stanza_name, props_property):
    """
    Return the fields parsed from sourcetype as pytest parameters

    Args:
        stanza_type: stanza type (source/sourcetype)
        stanza_name(str): source/sourcetype name
        props_property(object): sourcetype field details

    Return:
        List of pytest parameters
    """
    test_name = f"{stanza_name}::{props_property.value}"
    fields = [props_property.name]
    LOGGER.info(
        (
            "Generated pytest.param for sourcetype."
            "stanza_type=%s, stanza_name=%s, fields=%s"
        ),
        stanza_type,
        stanza_name,
        str(fields),
    )
    return pytest.param(
        {"stanza_type": stanza_type, "stanza_name": stanza_name, "fields": fields,},
        id=test_name,
    )


def return_props_field_alias(stanza_type, stanza_name, props_property):
    """
    Return the fields parsed from FIELDALIAS as pytest parameters

    Args:
        stanza_type: Stanza type (source/sourcetype)
        stanza_name(str): source/sourcetype name
        props_property(splunk_appinspect.configuration_file.ConfigurationSetting):
            The configuration setting object of FIELDALIAS
            properties used:
                name : key in the configuration settings
                value : value of the respective name in the configuration

    Regex:
        Description:
            Find all field alias group separated by space or comma
        Examples:
            field_source AS field_destination
            "Field Source" as "Field Destination"
            field_source ASNEW 'Field Destination'
            field_source asnew field_destination

    Return:
        List of pytest parameters
    """
    regex = (
        r"(\"(?:\\\"|[^\"])*\"|\'(?:\\\'|[^\'])*\'|[^\s,]+)"
        r"\s+(?i)(?:as(?:new)?)\s+"
        r"(\"(?:\\\"|[^\"])*\"|\'(?:\\\'|[^\'])*\'|[^\s,]+)"
    )
    fields_tuples = re.findall(regex, props_property.value, re.IGNORECASE)
    # Convert list of tuples into list
    fields = set([item for t in fields_tuples for item in t])

    LOGGER.info(
        (
            "Genrated pytest.param for FIELDALIAS. "
            "stanza_type=%s, stanza_name=%s, fields=%s"
        ),
        stanza_type,
        id,
        str(fields),
    )
    for field in fields:
        test_name = f"{stanza_name}_field::{field}"
        yield pytest.param(
            {
                "stanza_type": stanza_type,
                "stanza_name": stanza_name,
                "fields": [field],
            },
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


def load_splunk_eventtypes(eventtypes):
    """
    Parse the App configuration files & yield eventtypes
    Args:
        eventtypes(splunk_appinspect.configuration_file.ConfigurationFile):
        The configuration object of eventtypes.conf
    Yields:
        generator of list of eventtypes
    """

    for eventtype_section in eventtypes.sects:
        LOGGER.info("parsing eventtype stanza=%s", eventtype_section)
        yield return_eventtypes_param(eventtype_section)


def return_eventtypes_param(stanza_id):

    """
    Returns the eventtype parsed from the eventtypes.conf as pytest parameters
    Args:
        stanza_id(str): parameter from the stanza
    Returns:
        List of pytest parameters
    """

    LOGGER.info(
        "Generated pytest.param of eventtype with id=%s", f"eventtype::{stanza_id}",
    )
    return pytest.param(
        {"field": "eventtype", "value": stanza_id}, id=f"eventtype::{stanza_id}",
    )
