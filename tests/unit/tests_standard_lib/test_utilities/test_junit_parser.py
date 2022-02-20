import os
import tempfile

import pytest

from pytest_splunk_addon.standard_lib.utilities.junit_parser import JunitParser


def test_parse_junit_raises_exception_when_not_fields_are_present_in_testcase():
    jp = JunitParser(
        os.path.join(
            os.path.dirname(__file__), "test_data", "sample_junit_without_datamodel.xml"
        )
    )
    with pytest.raises(Exception):
        jp.parse_junit()


def test_junit_parser_parser_junit():
    expected_result = [
        {
            "data_model": "datamodel_1",
            "fields": "field_1",
            "data_set": "dataset_1",
            "fields_type": "required",
            "tag_stanza": 'dataset_name="dataset_1"',
            "status": "failed",
            "test_property": "splunklib.binding.HTTPError: HTTP 400 Bad Request",
        },
        {
            "data_model": "datamodel_2",
            "fields": "field_2",
            "data_set": "dataset_2",
            "fields_type": "required",
            "tag_stanza": 'dataset_name="dataset_2"',
            "status": "failed",
            "test_property": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        },
        {
            "data_model": "datamodel_3",
            "fields": "field_3",
            "data_set": "dataset_3",
            "fields_type": "conditional",
            "tag_stanza": 'dataset_name="dataset_3"',
            "status": "passed",
            "test_property": "-",
        },
        {
            "data_model": "datamodel_4",
            "fields": "field_4",
            "data_set": "dataset_4",
            "fields_type": "required",
            "tag_stanza": 'dataset_name="dataset_4"',
            "status": "skipped",
            "test_property": "-",
        },
    ]
    jp = JunitParser(
        os.path.join(os.path.dirname(__file__), "test_data", "sample_junit.xml")
    )
    jp.parse_junit()
    assert jp.data == expected_result


def test_junit_parser_init_with__directory():
    with tempfile.TemporaryDirectory() as tempdir:
        with pytest.raises(Exception):
            JunitParser(tempdir)


def test_junit_parser_init_with_not_found_file():
    with pytest.raises(Exception):
        JunitParser("file-does-not-exist")
