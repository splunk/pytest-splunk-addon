import unittest
import pytest
import os


from pytest_splunk_addon.standard_lib.cim_compliance import JunitParser

test_data = [
    {
        "data_model": "datamodel_1",
        "fields": "field_1",
        "data_set": "dataset_1",
        "fields_type": "required",
        "tag_stanza": "dataset_name=&quot;dataset_1&quot;",
        "status": "failed",
        "test_property": "splunklib.binding.HTTPError: HTTP 400 Bad Request",
    },
    {
        "data_model": "datamodel_2",
        "fields": "field_2",
        "data_set": "dataset_2",
        "fields_type": "required",
        "tag_stanza": "dataset_name=&quot;dataset_2&quot;",
        "status": "failed",
        "test_property": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    },
    {
        "data_model": "datamodel_3",
        "fields": "field_3",
        "data_set": "dataset_3",
        "fields_type": "conditional",
        "tag_stanza": "dataset_name=&quot;dataset_3&quot;",
        "status": "passed",
        "test_property": "-",
    },
    {
        "data_model": "datamodel_4",
        "fields": "field_4",
        "data_set": "dataset_4",
        "fields_type": "required",
        "tag_stanza": "dataset_name=&quot;dataset_4&quot;",
        "status": "skipped",
        "test_property": "-",
    },
]


@pytest.mark.docker
def test_data_generation():
    jp = JunitParser(
        os.path.join(os.path.dirname(__file__), "test_data", "sample_junit.xml")
    )
    jp.parse_junit()
    assert jp.data == test_data
