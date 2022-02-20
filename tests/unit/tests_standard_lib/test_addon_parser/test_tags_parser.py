import os
from unittest.mock import mock_open, patch

import pytest

from pytest_splunk_addon.standard_lib.addon_parser.tags_parser import TagsParser

TEST_TAGS_WITHOUT_STANZA_NAME = """tags_positive_event = enabled
tags_disabled_event = disabled
"""


@pytest.fixture()
def default_tags_parser():
    return TagsParser(os.path.join(os.path.dirname(__file__), "testdata"))


def test_tags_without_stanza_name():
    expected = []
    tags_parser = TagsParser("unused_path")
    with patch(
        "builtins.open", new_callable=mock_open, read_data=TEST_TAGS_WITHOUT_STANZA_NAME
    ):
        output = tags_parser.get_tags()
        assert expected == list(output)


def test_tags_can_be_parsed_and_returned(default_tags_parser):
    expected = [
        {
            "stanza": 'eventtype="fiction_for_tags_positive"',
            "tag": "tags_positive_event",
            "enabled": True,
        },
        {
            "stanza": 'eventtype="fiction_for_tags_positive"',
            "tag": "tags_disabled_event",
            "enabled": False,
        },
        {
            "stanza": 'source="/opt/splunk/var/log/splunk/splunkd.log"',
            "tag": "tags_positive_event",
            "enabled": True,
        },
        {
            "stanza": 'source="/opt/splunk/var/log/splunk/splunkd.log"',
            "tag": "tags_disabled_event",
            "enabled": False,
        },
    ]
    result = default_tags_parser.get_tags()
    assert expected == list(result)


def test_no_tags_config_file():
    tags_parser = TagsParser("unused_path")
    assert tags_parser.tags is None
