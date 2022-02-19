import os
from collections import namedtuple
from unittest.mock import mock_open, patch

import pytest

from pytest_splunk_addon.standard_lib.addon_parser.fields import Field
from pytest_splunk_addon.standard_lib.addon_parser.transforms_parser import (
    TransformsParser,
)


@pytest.mark.parametrize(
    "stanza, expected_outputs",
    [
        (
            "fiction-tsc-sk-delim-format",
            [
                Field({"name": "event_id"}),
                Field({"name": "server_contact_mode"}),
                Field({"name": "dest"}),
            ],
        ),
        (
            "fiction-tsc-regex-format",
            [
                Field({"name": "size1"}),
                Field({"name": "size2"}),
            ],
        ),
        (
            "fiction-tsc-regex",
            [
                Field({"name": "extractone"}),
            ],
        ),
    ],
)
def test_transforms_fields_can_be_parsed_and_returned(stanza, expected_outputs):
    transforms_conf_path = os.path.join(os.path.dirname(__file__), "testdata")
    transforms_parser = TransformsParser(transforms_conf_path)
    output = transforms_parser.get_transform_fields(stanza)
    assert expected_outputs == list(output)


def test_get_lookup_csv_fields():
    transforms_conf_path = os.path.join(os.path.dirname(__file__), "testdata")
    transforms_parser = TransformsParser(transforms_conf_path)
    fields = list(transforms_parser.get_lookup_csv_fields("ta_fiction_lookup"))
    expected_csv_fieldnames = [
        "component",
        "aliasone",
        "status.test",
        "fiction_context_test2",
    ]
    assert expected_csv_fieldnames == fields


def test_no_transforms_config_file():
    transforms_parser = TransformsParser("unused_path")
    assert transforms_parser.transforms is None


def test_stanza_does_not_exist_in_transforms(caplog):
    transforms_conf_path = os.path.join(os.path.dirname(__file__), "testdata")
    transforms_parser = TransformsParser(transforms_conf_path)
    for result in transforms_parser.get_transform_fields("dummy_stanza"):
        assert result is None
    assert (
        "The stanza dummy_stanza does not exists in transforms.conf." in caplog.messages
    )


def test_lookup_files_does_not_exist(caplog):
    transforms_conf_path = os.path.join(os.path.dirname(__file__), "testdata")
    transforms_parser = TransformsParser(transforms_conf_path)
    for _ in transforms_parser.get_lookup_csv_fields("ta_lookup_does_not_exits"):
        pass
    found_message = False
    for message in caplog.messages:
        if "Could not read the lookup file, skipping test." in message:
            found_message = True
            break
    assert found_message
