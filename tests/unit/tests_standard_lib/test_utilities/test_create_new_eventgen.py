import pytest
from unittest.mock import MagicMock, patch, PropertyMock, mock_open
from pytest_splunk_addon.standard_lib.utilities.create_new_eventgen import (
    UpdateEventgen,
)

output_to_build = {
    "fiction_is_splunkd": {
        "search": "index=_internal sourcetype=splunkd",
        "token.101.search": "index=main source=localhost",
        "token.101.find": "index=main source=remotehost",
        "token.102.search": "index=main sourcetype=splunkd",
    },
    "fiction_for_tags_positive": {"search": "sourcetype=splunkd"},
    "fiction_for_tags_negative": {"search": "index=_internal sourcetype=splunkd"},
}


@pytest.fixture()
def app_mock(monkeypatch):
    app = MagicMock()
    monkeypatch.setattr(
        "pytest_splunk_addon.standard_lib.utilities.create_new_eventgen.App", app
    )
    return app


@pytest.fixture()
def update_eventgen_instance(monkeypatch):
    with patch.object(UpdateEventgen, "__init__", return_value=None):
        eventgen = UpdateEventgen()
        eventgen._app = MagicMock()
        eventgen._eventgen = None
        eventgen.path_to_samples = "fake_path"
        return eventgen


@pytest.fixture()
def eventgen_mock():
    with patch.object(
        UpdateEventgen, "eventgen", new_callable=PropertyMock
    ) as eventgen_mock:
        yield eventgen_mock


@pytest.fixture()
def parsed_output(build_parsed_output):
    return build_parsed_output(output_to_build)


@pytest.fixture()
def os_listdir_mock(monkeypatch):
    listdir = MagicMock()
    monkeypatch.setattr("os.listdir", listdir)
    return listdir


def test_update_eventgen_instantiation(app_mock):
    app_mock.return_value = "APP_RETURN_VALUE"
    event = UpdateEventgen("fake_path")
    assert event._app == "APP_RETURN_VALUE"
    assert event._eventgen is None
    assert (event.path_to_samples == "fake_path/samples") or (
        event.path_to_samples == "fake_path\\samples"
    )


def test_eventgen(update_eventgen_instance):
    update_eventgen_instance._app.get_config.return_value = "eventgen config"
    assert (
        update_eventgen_instance.eventgen
        == update_eventgen_instance._eventgen
        == "eventgen config"
    )
    update_eventgen_instance._app.get_config.assert_called_once_with("eventgen.conf")


def test_eventgen_raises_exception(update_eventgen_instance):
    update_eventgen_instance._app.get_config.side_effect = OSError
    with pytest.raises(Exception, match="Eventgen.conf not found"):
        _ = update_eventgen_instance.eventgen


def test_get_eventgen_stanzas(
    open_mock,
    os_listdir_mock,
    build_parsed_output,
    eventgen_mock,
    update_eventgen_instance,
    configuration_file,
):
    eventgen_mock.return_value = configuration_file(
        [], build_parsed_output(output_to_build), []
    )
    open_mock().readlines.side_effect = [
        1 * ".",
        2 * ".",
        3 * ".",
        4 * ".",
        Exception,
        6 * ".",
    ]
    os_listdir_mock.return_value = [
        "fiction_for_tags_positive",
        "preffix_fiction_for_tags_positive_suffix",
        "fiction_for_tags_negative",
    ]
    out = update_eventgen_instance.get_eventgen_stanzas()
    assert out == {
        "fiction_is_splunkd": {
            "tokens": {
                "101": {
                    "search": "index=main source=localhost",
                    "find": "index=main source=remotehost",
                },
                "102": {"search": "index=main sourcetype=splunkd"},
            },
            "sample_count": 1,
            "search": "index=_internal sourcetype=splunkd",
        },
        "fiction_for_tags_positive": {
            "tokens": {},
            "sample_count": 2,
            "search": "sourcetype=splunkd",
        },
        "preffix_fiction_for_tags_positive_suffix": {
            "tokens": {},
            "sample_count": 4,
            "add_comment": True,
        },
        "fiction_for_tags_negative": {"tokens": {}, "search": "index=_internal sourcetype=splunkd"},
    }
