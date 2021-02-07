import importlib
import pytest
from unittest.mock import MagicMock, patch, PropertyMock

EXAMPLE_PATH = "Example_Path"
APP_RETURN_VALUE = "App_return_value"
PROPS_RETURN_VALUE = "Props_return_value"
TAGS_RETURN_VALUE = "Tags_return_value"
EVENTTYPE_RETURN_VALUE = "Eventtype_return_value"
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
    ) as eventtype_mock:
        app_mock.return_value = APP_RETURN_VALUE
        props_mock.return_value = PROPS_RETURN_VALUE
        tags_mock.return_value = TAGS_RETURN_VALUE
        eventtype_mock.return_value = EVENTTYPE_RETURN_VALUE
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


def test_get_tags(addonparser, monkeypatch):
    get_tags_mock = MagicMock()
    get_tags_mock.get_tags.return_value = TEST_VALUE
    with patch(
        f"{ADDON_PARSER_PATH}.AddonParser.tags_parser",
        new_callable=PropertyMock,
        return_value=get_tags_mock,
    ):
        ap = addonparser(EXAMPLE_PATH)
        assert ap.get_tags() == TEST_VALUE


def test_get_props_fields(addonparser, monkeypatch):
    get_props_fields_mock = MagicMock()
    get_props_fields_mock.get_props_fields.return_value = TEST_VALUE
    with patch(
        f"{ADDON_PARSER_PATH}.AddonParser.props_parser",
        new_callable=PropertyMock,
        return_value=get_props_fields_mock,
    ):
        ap = addonparser(EXAMPLE_PATH)
        assert ap.get_props_fields() == TEST_VALUE


def test_get_eventtypes(addonparser, monkeypatch):
    get_eventtypes_mock = MagicMock()
    get_eventtypes_mock.get_eventtypes.return_value = TEST_VALUE
    with patch(
        f"{ADDON_PARSER_PATH}.AddonParser.eventtype_parser",
        new_callable=PropertyMock,
        return_value=get_eventtypes_mock,
    ):
        ap = addonparser(EXAMPLE_PATH)
        assert ap.get_eventtypes() == TEST_VALUE
