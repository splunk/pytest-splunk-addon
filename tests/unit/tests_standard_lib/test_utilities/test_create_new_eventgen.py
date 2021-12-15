import pytest
from unittest.mock import MagicMock, patch, PropertyMock, call
from pytest_splunk_addon.standard_lib.utilities.create_new_eventgen import (
    UpdateEventgen,
)

output_to_build = {
    "fiction_is_splunkd": {
        "search": "index=_internal sourcetype=splunkd",
        "token.101.token": "##replacement_token##",
        "token.101.replacementType": "timestamp",
        "token.102.token": "##Dest_Port##",
        "token.102.replacement": "dest_port",
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
                    "token": "##replacement_token##",
                    "replacementType": "timestamp",
                },
                "102": {
                    "token": "##Dest_Port##",
                    "replacement": "dest_port",
                },
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
        "fiction_for_tags_negative": {
            "tokens": {},
            "search": "index=_internal sourcetype=splunkd",
        },
    }


@pytest.mark.parametrize(
    "eventgen_dict, expected_output",
    [
        (
            {
                "sample_file.samples": {
                    "tokens": {
                        "101": {
                            "token": "##replacement_token##",
                            "replacementType": "timestamp",
                            "replacement": 'list["a", "b"]',
                        },
                    },
                    "index": "main",
                    "sample_count": 1,
                    "search": "index=_internal sourcetype=splunkd",
                },
            },
            {
                "sample_file.samples": {
                    "input_type": "<<input_type>> #REVIEW : Update metadata as per addon's requirement",
                    "host_type": "<<host_type>> #REVIEW : Update metadata as per addon's requirement",
                    "sourcetype_to_search": "<<sourcetype_to_search>> "
                    "#REVIEW : Update metadata as per addon's requirement",
                    "timestamp_type": "<<timestamp_type>> "
                    "#REVIEW : Update metadata as per addon's requirement",
                    "sample_count": "1  # REVIEW : Please check for the events per stanza "
                    "and update sample_count accordingly",
                    "index": "main #REVIEW : Update metadata as per addon's requirement",
                    "search": "index=_internal sourcetype=splunkd",
                    "source": "pytest-splunk-addon:<<input_type>> #REVIEW : Update metadata as per addon's requirement",
                    "tokens": {
                        "101": {
                            "field": "_time # REVIEW : Check if the field is extracted from the events, "
                            "else remove this field parameter",
                            "token": "##replacement_token##",
                            "replacementType": "timestamp",
                            "replacement": 'list["a", "b"]',
                        },
                    },
                },
            },
        ),
        (
            {
                "sample_file.samples": {
                    "tokens": {
                        "102": {
                            "token": "##Dest##",
                            "replacementType": "static",
                            "replacement": "src",
                        },
                    },
                    "source": "utility.log",
                },
            },
            {
                "sample_file.samples": {
                    "input_type": "<<input_type>> #REVIEW : Update metadata as per addon's requirement",
                    "host_type": "<<host_type>> #REVIEW : Update metadata as per addon's requirement",
                    "sourcetype_to_search": "<<sourcetype_to_search>> "
                    "#REVIEW : Update metadata as per addon's requirement",
                    "timestamp_type": "<<timestamp_type>> #REVIEW : Update metadata as per addon's requirement",
                    "source": "utility.log",
                    "tokens": {
                        "102": {
                            "field": "dest # REVIEW : Check if the field is extracted from the events, "
                            "else remove this field parameter",
                            "token": "##Dest##",
                            "replacementType": "random",
                            "replacement": "dest[] "
                            "# REVIEW : Possible value in list :  ['ipv4', 'ipv6', 'host', 'fqdn']",
                        },
                    },
                },
            },
        ),
        (
            {
                "sample_file.samples": {
                    "tokens": {
                        "103": {
                            "token": "##token_user_file##",
                            "replacementType": "file",
                            "replacement": "$SPLUNK_HOME/fake_path/samples/user_name.sample:1",
                        },
                    },
                    "source": "user.log",
                },
            },
            {
                "sample_file.samples": {
                    "input_type": "<<input_type>> #REVIEW : Update metadata as per addon's requirement",
                    "host_type": "<<host_type>> "
                    "#REVIEW : Update metadata as per addon's requirement",
                    "sourcetype_to_search": "<<sourcetype_to_search>> "
                    "#REVIEW : Update metadata as per addon's requirement",
                    "timestamp_type": "<<timestamp_type>> "
                    "#REVIEW : Update metadata as per addon's requirement",
                    "source": "user.log",
                    "tokens": {
                        "103": {
                            "field": "user # REVIEW : Please check if it can be replace with user rule",
                            "token": "##token_user_file##",
                            "replacementType": "random",
                            "replacement": "file[$SPLUNK_HOME/fake_path/samples/user_name.sample:1] "
                            "# REVIEW : Possible value in list :  "
                            "['name', 'email', 'domain_user', 'distinquised_name']",
                        },
                    },
                },
            },
        ),
        (
            {
                "sample_file.samples": {
                    "tokens": {
                        "104": {
                            "token": "##token_email_log##",
                            "replacementType": "file",
                            "replacement": "SA-Eventgen/email_address.sample:2",
                        },
                    },
                    "source": "email.log",
                },
            },
            {
                "sample_file.samples": {
                    "input_type": "<<input_type>> #REVIEW : Update metadata as per addon's requirement",
                    "host_type": "<<host_type>> #REVIEW : Update metadata as per addon's requirement",
                    "sourcetype_to_search": "<<sourcetype_to_search>> "
                    "#REVIEW : Update metadata as per addon's requirement",
                    "timestamp_type": "<<timestamp_type>> #REVIEW : Update metadata as per addon's requirement",
                    "source": "email.log",
                    "tokens": {
                        "104": {
                            "token": "##token_email_log##",
                            "replacementType": "random # REVIEW : Please check if it can be replace with email rule",
                            "replacement": "email # REVIEW : Please check if it can be replace with email rule",
                        },
                    },
                },
            },
        ),
    ],
)
def test_update_eventgen_stanzas(
    update_eventgen_instance, eventgen_dict, expected_output
):
    out = update_eventgen_instance.update_eventgen_stanzas(eventgen_dict)
    assert out == expected_output


def test_create_new_eventgen(
    open_mock,
    eventgen_mock,
    build_parsed_output,
    update_eventgen_instance,
    configuration_file,
):
    eventgen_mock.return_value = configuration_file(["## Splunk", "## Data"], [], [])
    updated_d = {
        "sample_file.samples": {
            "add_comment": True,
            "source": "utility.log",
            "tokens": {
                "102": {
                    "field": "dest",
                    "token": "##Dest##",
                    "replacementType": "random",
                    "replacement": "dest[]",
                },
            },
        },
    }
    update_eventgen_instance.create_new_eventgen(updated_d, "fake_path")
    open_mock.assert_called_once_with("fake_path", "w")
    open_mock().assert_has_calls(
        [
            call.__enter__(),
            call.write("## Splunk\n"),
            call.write("## Data\n"),
            call.write("\n[sample_file.samples]\n"),
            call.write("## Stanza gets metadata from main stanza\n"),
            call.write("source = utility.log\n"),
            call.write("\n"),
            call.write("token.102.token = ##Dest##\n"),
            call.write("token.102.replacementType = random\n"),
            call.write("token.102.replacement = dest[]\n"),
            call.write("token.102.field = dest\n"),
            call.write("\n"),
            call.__exit__(None, None, None),
        ]
    )
