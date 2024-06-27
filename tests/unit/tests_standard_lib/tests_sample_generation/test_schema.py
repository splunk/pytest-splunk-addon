import os.path

import pytest
from xmlschema import XMLSchema, XMLSchemaChildrenValidationError

from pytest_splunk_addon.standard_lib.sample_generation.pytest_splunk_addon_data_parser import (
    SCHEMA_PATH,
)


@pytest.fixture
def validator() -> XMLSchema:
    return XMLSchema(SCHEMA_PATH)


def get_xml(name: str) -> str:
    with open(os.path.join(os.path.dirname(__file__), "test_data", "xmls", name)) as fp:
        return fp.read()


def test_validate_schema(validator):
    validator.validate(get_xml("lr_without_notes.xml"))


def test_validate_schema_incorrect_event_element(validator):
    with pytest.raises(XMLSchemaChildrenValidationError):
        validator.validate(get_xml("lr_incorrect.xml"))


def test_validate_schema_notes(validator):
    validator.validate(get_xml("lr_notes.xml"))
