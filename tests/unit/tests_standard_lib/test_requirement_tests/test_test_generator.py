import pytest
import traceback
from unittest.mock import MagicMock, call, patch
from collections import namedtuple
from pytest_splunk_addon.standard_lib.requirement_tests.test_generator import (
    ReqsTestGenerator,
)

root_content = namedtuple("Element", ["text"])


@pytest.fixture()
def reqs_test_generator(os_path_join_file_mock):
    return ReqsTestGenerator("fake_path")


@pytest.fixture()
def root_mock():
    root_mock = MagicMock()
    root_mock.tags = {
        "model": ["Network Traffic", "Authentication"],
        "raw": ["RT_FLOW_SESSION_CREATE"],
    }
    root_mock.iter.side_effect = lambda x: (
        root_content(text=item) for item in root_mock.tags[x]
    )
    return root_mock


@pytest.fixture()
def et_parse_mock(monkeypatch):
    tree_mock = MagicMock()
    monkeypatch.setattr(
        "pytest_splunk_addon.standard_lib.requirement_tests.test_generator.ET.parse",
        tree_mock,
    )
    return tree_mock


def test_generate_tests():
    with patch.object(
        ReqsTestGenerator,
        "generate_cim_req_params",
        side_effect=lambda: (tc for tc in ["test_1", "test_2", "test_3"]),
    ):
        rtg = ReqsTestGenerator("fake_path")
        out = list(rtg.generate_tests("splunk_searchtime_requirement_param"))
        assert out == ["test_1", "test_2", "test_3"]


def test_extract_key_value_xml():
    event = MagicMock()
    with patch.object(
        ReqsTestGenerator,
        "extract_key_value_xml",
        side_effect=[
            {"field1": "value1", "field2": "value2"},
        ],
    ):
        rtg = ReqsTestGenerator("fake_path")
        out = rtg.extract_key_value_xml(event, "cim_fields")
        assert out == {"field1": "value1", "field2": "value2"}


def test_extract_transport_tag():
    event = MagicMock()
    event.iter.side_effect = lambda x: (
        d
        for d in [
            {"type": "syslog"},
        ]
    )
    rtg = ReqsTestGenerator("fake_path")
    out = rtg.extract_transport_tag(event)
    assert out == "syslog"
    event.iter.assert_called_once_with("transport")


def test_extract_params():
    event = MagicMock()
    event.iter.side_effect = lambda x: (
        d
        for d in [
            {"type": "modinput"},
            {"host": "sample_host"},
            {"source": "sample_source"},
            {"sourcetype": "sample_sourcetype"},
        ]
    )
    rtg = ReqsTestGenerator("fake_path")
    out = rtg.extract_params(event)
    assert out == ("sample_host", "sample_source", "sample_sourcetype")
    event.iter.assert_called_once_with("transport")


@pytest.mark.parametrize(
    "listdir_return_value, "
    "check_xml_format_return_value, "
    "extract_transport_tag_return_value, "
    "root_events, "
    "get_models_return_value, "
    "get_event_name_return_value, "
    "extract_key_value_xml_return_value, "
    "expected_output",
    [
        (
            ["requirement.log"],
            [True],
            ["syslog"],
            {"event": ["<34>Oct 11 22:14:15 machine1 pr1:event_1"]},
            [["model_1:dataset_1", "model_2:dataset_2"]],
            ["event_name_1"],
            [{"field1": "value1", "field2": "value2"}, {"field3": "value3"}],
            [
                (
                    {
                        "model_list": [
                            ("model_1", "dataset_1", ""),
                            ("model_2", "dataset_2", ""),
                        ],
                        "escaped_event": "event_1",
                        "exceptions_dict": {"field3": "value3"},
                        "Key_value_dict": {"field1": "value1", "field2": "value2"},
                        "modinput_params": None,
                        "transport_type": "syslog",
                    },
                    "model_1:dataset_1 "
                    "model_2:dataset_2::fake_path/requirement.log::event_no::1::event_name::event_name_1",
                ),
            ],
        ),
        (
            ["requirement.xml"],
            [True],
            ["syslog"],
            {"event": ["<34>Oct 11 22:14:15 machine1 pr1:event_1"]},
            [["model_1:dataset_1", "model_2:dataset_2"]],
            ["event_name_1"],
            [{"field1": "value1", "field2": "value2"}, {"field3": "value3"}],
            [
                (
                    {
                        "model_list": [
                            ("model_1", "dataset_1", ""),
                            ("model_2", "dataset_2", ""),
                        ],
                        "escaped_event": "event_1",
                        "exceptions_dict": {"field3": "value3"},
                        "Key_value_dict": {"field1": "value1", "field2": "value2"},
                        "modinput_params": None,
                        "transport_type": "syslog",
                    },
                    "model_1:dataset_1 "
                    "model_2:dataset_2::fake_path/requirement.log::event_no::1::event_name::event_name_1",
                ),
            ],
        ),
        (
            ["req.log"],
            [True],
            ["syslog"],
            {"event": ["event_1"]},
            [[]],
            ["event_name_3"],
            [{"field1": "value1", "field2": "value2"}, {"field3": "value3"}],
            [],
        ),
    ],
)
def test_generate_cim_req_params(
    mock_object,
    root_mock,
    listdir_return_value,
    check_xml_format_return_value,
    extract_transport_tag_return_value,
    root_events,
    get_models_return_value,
    get_event_name_return_value,
    extract_key_value_xml_return_value,
    expected_output,
):
    os_path_is_dir_mock = mock_object("os.path.isdir")
    os_path_is_dir_mock.return_value = True
    os_listdir_mock = mock_object("os.listdir")
    os_listdir_mock.return_value = listdir_return_value
    root_mock.tags.update(root_events)
    with patch.object(
        ReqsTestGenerator, "check_xml_format", side_effect=check_xml_format_return_value
    ), patch.object(
        ReqsTestGenerator,
        "extract_transport_tag",
        side_effect=extract_transport_tag_return_value,
    ), patch.object(
        ReqsTestGenerator, "get_root", side_effect=[root_mock]
    ), patch.object(
        ReqsTestGenerator, "get_event", side_effect=lambda x: x.text
    ), patch.object(
        ReqsTestGenerator, "escape_char_event", side_effect=lambda x: x
    ), patch.object(
        ReqsTestGenerator, "get_models", side_effect=get_models_return_value
    ), patch.object(
        ReqsTestGenerator, "get_event_name", side_effect=get_event_name_return_value
    ), patch.object(
        ReqsTestGenerator,
        "extract_key_value_xml",
        side_effect=extract_key_value_xml_return_value,
    ), patch.object(
        ReqsTestGenerator,
        "split_model",
        side_effect=lambda x: (x.split(":")[0], x.split(":")[1], ""),
    ), patch.object(
        pytest, "param", side_effect=lambda x, id: (x, id)
    ) as param_mock:
        rtg = ReqsTestGenerator("fake_path")
        out = list(rtg.generate_cim_req_params())
        assert out == expected_output
        param_mock.assert_has_calls(
            [call(param[0], id=param[1]) for param in expected_output]
        )


def test_get_models(root_mock):
    rtg = ReqsTestGenerator("fake_path")
    assert rtg.get_models(root_mock) == ["Network Traffic", "Authentication"]
    root_mock.iter.assert_called_once_with("model")


def test_get_event(root_mock):
    rtg = ReqsTestGenerator("fake_path")
    assert rtg.get_event(root_mock) == "RT_FLOW_SESSION_CREATE"
    root_mock.iter.assert_called_once_with("raw")


def test_get_root(et_parse_mock):
    et_parse_mock.return_value = et_parse_mock
    et_parse_mock.getroot.return_value = "root"
    rtg = ReqsTestGenerator("fake_path")
    assert rtg.get_root("requirement.log") == "root"
    et_parse_mock.assert_has_calls([call("requirement.log"), call.getroot()])


@pytest.mark.parametrize(
    "is_xml_valid, expected_output",
    [
        (True, True),
        (False, False),
    ],
)
def test_check_xml_format(et_parse_mock, is_xml_valid, expected_output):
    et_parse_mock.return_value = is_xml_valid
    rtg = ReqsTestGenerator("fake_path")
    assert rtg.check_xml_format("requirement.log") is expected_output


@pytest.mark.parametrize(
    "escape_char, expected_output",
    [
        ("\\", "SESSION \\\\ CREATED"),
        ("`", "SESSION \\` CREATED"),
        ("~", "SESSION \\~ CREATED"),
        ("!", "SESSION \\! CREATED"),
        ("@", "SESSION \\@ CREATED"),
        ("#", "SESSION \\# CREATED"),
        ("$", "SESSION \\$ CREATED"),
        ("%", "SESSION \\% CREATED"),
        ("^", "SESSION \\^ CREATED"),
        ("&", "SESSION \\& CREATED"),
        ("(", "SESSION \\( CREATED"),
        (")", "SESSION \\) CREATED"),
        ("-", "SESSION \\- CREATED"),
        ("=", "SESSION \\= CREATED"),
        ("+", "SESSION \\+ CREATED"),
        ("[", "SESSION \\[ CREATED"),
        ("]", "SESSION \\] CREATED"),
        ("}", "SESSION \\} CREATED"),
        ("{", "SESSION \\{ CREATED"),
        ("|", "SESSION \\| CREATED"),
        (";", "SESSION \\; CREATED"),
        (":", "SESSION \\: CREATED"),
        ("'", "SESSION \\' CREATED"),
        ("\,", "SESSION \\\\\, CREATED"),
        ("<", "SESSION \\< CREATED"),
        (">", "SESSION \\> CREATED"),
        ("\/", "SESSION \\\\\/ CREATED"),
        ("?", "SESSION \\? CREATED"),
        ("IN", "SESSION \\IN CREATED"),
        ("AS", "SESSION \\AS CREATED"),
        ("BY", "SESSION \\BY CREATED"),
        ("OVER", "SESSION \\OVER CREATED"),
        ("WHERE", "SESSION \\WHERE CREATED"),
        ("LIKE", "SESSION \\LIKE CREATED"),
        ("NOT", "SESSION \\NOT CREATED"),
    ],
)
def test_escape_char_event(escape_char, expected_output):
    rtg = ReqsTestGenerator("fake_path")
    assert rtg.escape_char_event(f"SESSION {escape_char} CREATED") == expected_output
