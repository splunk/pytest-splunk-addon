import pytest
from unittest.mock import MagicMock, patch, PropertyMock, call
from collections import namedtuple
from splunk_appinspect import App

from pytest_splunk_addon.standard_lib.sample_generation.eventgen_parser import (
    EventgenParser,
)

ADDON_PATH = "/add/on/path"
CONFIG_PATH = "/config/path"
PARENT_DIR = "pardir"
DATA_CONFIG = "data_config"
FILE_1 = "file_1"
FILE_2 = "file_2"
VALUE_1 = "value_1"
VALUE_2 = "value_2"
OPTION_1 = "option_1"
SAMPLE_STANZA = "sample_stanza"
PTS = "pts"

sects = namedtuple("Sects", ["sects"])


def get_exists_mock_func(path):
    def func(input):
        if input == path:
            return True
        return False

    return func


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self


class TestEventgenParser:
    @pytest.fixture(scope="session")
    def eventgen_parser(self):
        def func(*args):
            if not args:
                return EventgenParser("path")
            return EventgenParser(*args)

        return func

    def test_init(self, eventgen_parser):
        ep = eventgen_parser(ADDON_PATH, CONFIG_PATH)
        assert ep.config_path == CONFIG_PATH
        assert ep.addon_path == ADDON_PATH
        assert ep.match_stanzas == set()

    @pytest.mark.parametrize(
        "exist_path",
        [
            (f"{CONFIG_PATH}/samples"),
            (f"{CONFIG_PATH}/{PARENT_DIR}/samples"),
            (f"{ADDON_PATH}/samples"),
        ],
    )
    def test_path_to_samples(self, eventgen_parser, exist_path):
        ep = eventgen_parser(ADDON_PATH, CONFIG_PATH)
        path = exist_path
        with patch("os.path.exists", get_exists_mock_func(path)), patch(
            "os.pardir", PARENT_DIR
        ), patch("os.path.abspath", lambda x: x), patch("os.sep", "/"):
            assert ep.path_to_samples == path

    @pytest.mark.parametrize(
        "exist_path, expected, args, kwargs",
        [
            (
                f"{CONFIG_PATH}/pytest-splunk-addon-data.conf",
                DATA_CONFIG,
                ("pytest-splunk-addon-data.conf",),
                {"dir": "relpath_/config/path"},
            ),
            (
                f"{CONFIG_PATH}/eventgen.conf",
                DATA_CONFIG,
                ("eventgen.conf",),
                {"dir": "relpath_/config/path"},
            ),
            (f"{CONFIG_PATH}/other", DATA_CONFIG, ("eventgen.conf",), {}),
        ],
    )
    def test_eventgen(self, eventgen_parser, exist_path, expected, args, kwargs):
        ep = eventgen_parser(ADDON_PATH, CONFIG_PATH)
        path = exist_path
        app_mock = MagicMock(spec=App)
        app_mock.get_config.return_value = DATA_CONFIG
        app_mock.get_filename.return_value = "filename"
        with patch("os.path.exists", get_exists_mock_func(path)), patch(
            "os.path.relpath", lambda x, _: f"relpath_{x}"
        ), patch("os.sep", "/"), patch.object(ep, "_app", app_mock):
            assert ep.eventgen == expected
            app_mock.get_config.assert_called_with(*args, **kwargs)

    def test_eventgen_os_error(self, eventgen_parser):
        ep = eventgen_parser(ADDON_PATH, CONFIG_PATH)
        with patch("os.path.exists", MagicMock(side_effect=OSError)):
            with pytest.raises(
                FileNotFoundError,
                match="pytest-splunk-addon-data.conf/eventgen.conf not Found",
            ):
                ep.eventgen

    def test_get_sample_stanzas(self):
        with patch.object(
            EventgenParser,
            "get_eventgen_stanzas",
            MagicMock(return_value=AttrDict(file_1=VALUE_1, file_2=VALUE_2)),
        ), patch("os.sep", "/"), patch.object(
            EventgenParser,
            "path_to_samples",
            new_callable=PropertyMock(return_value=PTS),
        ), patch(
            "pytest_splunk_addon.standard_lib.sample_generation.eventgen_parser.SampleStanza",
            MagicMock(return_value=SAMPLE_STANZA),
        ) as sample_stanza_mock:
            assert list(
                EventgenParser(ADDON_PATH, CONFIG_PATH).get_sample_stanzas()
            ) == [SAMPLE_STANZA, SAMPLE_STANZA]
            sample_stanza_mock.assert_has_calls(
                [call("pts/file_1", "value_1"), call("pts/file_2", "value_2")]
            )

    def test_get_eventgen_stanzas(self):
        with patch.object(
            EventgenParser,
            "path_to_samples",
            new_callable=PropertyMock(return_value=""),
        ), patch.object(
            EventgenParser,
            "eventgen",
            new_callable=PropertyMock(
                return_value=sects(
                    {
                        FILE_1: AttrDict(
                            options=AttrDict(
                                option1=AttrDict(name="token.option.1", value=VALUE_1)
                            )
                        ),
                        FILE_2: AttrDict(
                            options=AttrDict(
                                option2=AttrDict(name=OPTION_1, value=VALUE_2)
                            )
                        ),
                    }
                )
            ),
        ), patch(
            "os.path.exists", MagicMock(return_value=True)
        ), patch(
            "os.listdir", MagicMock(return_value=[FILE_1, FILE_2, "file_3"])
        ):
            assert EventgenParser(ADDON_PATH, CONFIG_PATH).get_eventgen_stanzas() == {
                FILE_1: {"tokens": {"file_1_option": {"1": VALUE_1}}},
                FILE_2: {OPTION_1: VALUE_2, "tokens": {}},
            }

    def test_check_samples(self, caplog):
        with patch.object(
            EventgenParser,
            "path_to_samples",
            new_callable=PropertyMock(return_value=""),
        ), patch("os.path.exists", MagicMock(return_value=True)), patch.object(
            EventgenParser,
            "eventgen",
            new_callable=PropertyMock(return_value=sects([FILE_1, FILE_2])),
        ):
            assert EventgenParser(ADDON_PATH, CONFIG_PATH).check_samples() is None
            assert all(
                message in caplog.messages
                for message in [
                    "No sample file found for stanza : file_1",
                    "Sample file found for stanza : file_1",
                    "No sample file found for stanza : file_2",
                    "Sample file found for stanza : file_2",
                ]
            )
