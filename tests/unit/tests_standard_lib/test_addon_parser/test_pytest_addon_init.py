import importlib
import pytest
from unittest.mock import MagicMock, patch, PropertyMock

EXAMPLE_PATH = "Example_Path"
PROPS_RETURN_VALUE = "Props_return_value"
TAGS_RETURN_VALUE = "Tags_return_value"
EVENTTYPE_RETURN_VALUE = "Eventtype_return_value"
SAVEDSEARCH_RETURN_VALUE = "Savedsearch_return_value"
TEST_VALUE = "Test_value"
ADDON_PARSER_PATH = "pytest_splunk_addon.addon_parser"


@pytest.fixture
def addonparser():
    with patch(f"{ADDON_PARSER_PATH}.props_parser.PropsParser") as props_mock, patch(
        f"{ADDON_PARSER_PATH}.tags_parser.TagsParser"
    ) as tags_mock, patch(
        f"{ADDON_PARSER_PATH}.eventtype_parser.EventTypeParser"
    ) as eventtype_mock, patch(
        f"{ADDON_PARSER_PATH}.savedsearches_parser.SavedSearchParser"
    ) as savedsearch_mock:
        props_instance = MagicMock()
        props_instance.props = PROPS_RETURN_VALUE
        tags_instance = MagicMock()
        tags_instance.tags = TAGS_RETURN_VALUE
        eventtype_instance = MagicMock()
        eventtype_instance.eventtypes = EVENTTYPE_RETURN_VALUE
        savedsearch_instance = MagicMock()
        savedsearch_instance.savedsearches = SAVEDSEARCH_RETURN_VALUE

        props_mock.return_value = props_instance
        tags_mock.return_value = tags_instance
        eventtype_mock.return_value = eventtype_instance
        savedsearch_mock.return_value = savedsearch_instance
        import pytest_splunk_addon.addon_parser

        importlib.reload(pytest_splunk_addon.addon_parser)
        return pytest_splunk_addon.addon_parser.AddonParser


def test_addonparser_init(addonparser):
    ap = addonparser(EXAMPLE_PATH)
    assert ap.splunk_app_path == EXAMPLE_PATH
    assert ap.props_parser.props == PROPS_RETURN_VALUE
    assert ap.tags_parser.tags == TAGS_RETURN_VALUE
    assert ap.eventtype_parser.eventtypes == EVENTTYPE_RETURN_VALUE
    assert ap.savedsearch_parser.savedsearches == SAVEDSEARCH_RETURN_VALUE


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
        if function == "get_props_fields":
            gt.return_value = [TEST_VALUE]
            assert list(getattr(ap, function)()) == [TEST_VALUE]
        else:
            assert getattr(ap, function)() == TEST_VALUE
