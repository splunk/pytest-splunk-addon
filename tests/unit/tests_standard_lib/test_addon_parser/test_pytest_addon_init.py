import importlib
from unittest.mock import MagicMock, PropertyMock, patch

import pytest

EXAMPLE_PATH = "Example_Path"
APP_RETURN_VALUE = "App_return_value"
PROPS_RETURN_VALUE = "Props_return_value"
TAGS_RETURN_VALUE = "Tags_return_value"
EVENTTYPE_RETURN_VALUE = "Eventtype_return_value"
SAVEDSEARCH_RETURN_VALUE = "Savedsearch_return_value"
TEST_VALUE = "Test_value"
ADDON_PARSER_PATH = "pytest_splunk_addon.standard_lib.addon_parser"


@pytest.fixture
def addonparser():
    with patch("splunk_appinspect.App") as app_mock, patch(
        f"{ADDON_PARSER_PATH}.props_parser.PropsParser"
    ) as props_mock, patch(
        f"{ADDON_PARSER_PATH}.tags_parser.TagsParser"
    ) as tags_mock, patch(
        f"{ADDON_PARSER_PATH}.eventtype_parser.EventTypeParser"
    ) as eventtype_mock, patch(
        f"{ADDON_PARSER_PATH}.savedsearches_parser.SavedSearchParser"
    ) as savedsearch_mock:
        app_mock.return_value = APP_RETURN_VALUE
        props_mock.return_value = PROPS_RETURN_VALUE
        tags_mock.return_value = TAGS_RETURN_VALUE
        eventtype_mock.return_value = EVENTTYPE_RETURN_VALUE
        savedsearch_mock.return_value = SAVEDSEARCH_RETURN_VALUE
        import pytest_splunk_addon.standard_lib.addon_parser

        importlib.reload(pytest_splunk_addon.standard_lib.addon_parser)
        return pytest_splunk_addon.standard_lib.addon_parser.AddonParser


def test_addonparser_init(addonparser):
    ap = addonparser(EXAMPLE_PATH)
    assert ap.splunk_app_path == EXAMPLE_PATH
    assert ap.app == APP_RETURN_VALUE
    assert ap.props_parser == PROPS_RETURN_VALUE
    assert ap.tags_parser == TAGS_RETURN_VALUE
    assert ap.eventtype_parser == EVENTTYPE_RETURN_VALUE
    assert ap.savedsearch_parser == SAVEDSEARCH_RETURN_VALUE


@pytest.mark.parametrize(
    "function, obj_to_mock",
    [
        ("get_tags", "tags_parser"),
        ("get_props_fields", "props_parser"),
        ("get_eventtypes", "eventtype_parser"),
        ("get_savedsearches", "savedsearch_parser"),
    ],
)
def test_get_methods(addonparser, monkeypatch, function, obj_to_mock):
    attr_mock = MagicMock()
    gt = MagicMock()
    gt.return_value = TEST_VALUE
    setattr(attr_mock, function, gt)
    with patch(
        f"{ADDON_PARSER_PATH}.AddonParser.{obj_to_mock}",
        new_callable=PropertyMock,
        return_value=attr_mock,
    ):
        ap = addonparser(EXAMPLE_PATH)
        assert getattr(ap, function)() == TEST_VALUE
