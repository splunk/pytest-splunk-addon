import pytest
from unittest.mock import MagicMock, call, patch, PropertyMock
from collections import namedtuple
from pytest_splunk_addon.standard_lib.cim_tests.data_model_handler import (
    DataModelHandler,
)


@pytest.fixture()
def listdir_mock(monkeypatch):
    monkeypatch.setattr(
        "os.listdir",
        MagicMock(return_value=["model1.json", "model2.xml", "model3.json"]),
    )


@pytest.fixture()
def data_model_mock(monkeypatch):
    dm = MagicMock()
    dm.side_effect = ["data_model_instance_1", "data_model_instance_2"]
    monkeypatch.setattr(
        "pytest_splunk_addon.standard_lib.cim_tests.data_model_handler.DataModel", dm
    )
    return dm


@pytest.fixture()
def json_schema_mock(monkeypatch):
    js = MagicMock()
    js.parse_data_model.side_effect = ["parsed_data_model_1", "parsed_data_model_2"]
    monkeypatch.setattr(
        "pytest_splunk_addon.standard_lib.cim_tests.data_model_handler.JSONSchema", js
    )
    return js


def test_data_models():
    with patch.object(
        DataModelHandler,
        "load_data_models",
        return_value=(f"data_model_{i+1}" for i in range(3)),
    ):
        dmh = DataModelHandler("/fake_path")
        assert dmh.data_models == ["data_model_1", "data_model_2", "data_model_3"]
        assert dmh._data_models == ["data_model_1", "data_model_2", "data_model_3"]


def test_load_data_model(listdir_mock, data_model_mock, json_schema_mock):
    dmh = DataModelHandler("/fake_path")
    assert list(dmh.load_data_models("/fake_path/data_models")) == [
        "data_model_instance_1",
        "data_model_instance_2",
    ]
    data_model_mock.assert_has_calls(
        [call("parsed_data_model_1"), call("parsed_data_model_2")]
    )
    json_schema_mock.parse_data_model.assert_has_calls(
        [
            call("/fake_path/data_models/model1.json"),
            call("/fake_path/data_models/model3.json"),
        ]
    )


def test_get_all_tags_per_stanza():
    dmh = DataModelHandler("/fake_path")
    addon_parser = namedtuple("AddonParser", ["get_tags"])
    ap = addon_parser(
        lambda: [
            {
                "stanza": "test_stanza_1",
                "tag": {"tag1_key": "tag1_value", "tag2_key": "tag2_value"},
            },
            {"stanza": "test_stanza_2", "tag": {"tag3_key": "tag3_value"}},
            {"stanza": "test_stanza_1", "tag": {"tag4_key": "tag4_value"}},
        ]
    )
    assert dmh._get_all_tags_per_stanza(ap) == {
        "test_stanza_1": [
            {"tag1_key": "tag1_value", "tag2_key": "tag2_value"},
            {"tag4_key": "tag4_value"},
        ],
        "test_stanza_2": [{"tag3_key": "tag3_value"}],
    }


def test_get_mapped_data_models(caplog):
    data_model = namedtuple("DataModel", ["get_mapped_datasets"])
    data_models = [
        data_model(lambda x: x if len(x) == 1 else []),
        data_model(lambda x: []),
        data_model(lambda x: x if len(x) == 3 else []),
    ]
    with patch.object(
        DataModelHandler,
        "_get_all_tags_per_stanza",
        return_value={
            "stanza_1": [{"tag_key_1a": "tag_value_1a", "tag_key_1b": "tag_value_1b"}],
            "stanza_2": [
                {"tag_key_2a": "tag_value_2a", "tag_key_2b": "tag_value_2b"},
                None,
            ],
            "stanza_3": [
                {"tag_key_3a": "tag_value_3a"},
                {"tag_key_3b": "tag_value_3b"},
                {"tag_key_3c": "tag_value_3c"},
            ],
        },
    ), patch.object(
        DataModelHandler,
        "data_models",
        new_callable=PropertyMock,
        return_value=data_models,
    ):
        dmh = DataModelHandler("/fake_path")
        assert list(dmh.get_mapped_data_models("addon_parser")) == [
            (
                "stanza_1",
                {"tag_key_1a": "tag_value_1a", "tag_key_1b": "tag_value_1b"},
            ),
            ("stanza_3", {"tag_key_3a": "tag_value_3a"}),
            ("stanza_3", {"tag_key_3b": "tag_value_3b"}),
            ("stanza_3", {"tag_key_3c": "tag_value_3c"}),
        ]
        assert "No Data Model mapped for stanza_2" in caplog.messages
