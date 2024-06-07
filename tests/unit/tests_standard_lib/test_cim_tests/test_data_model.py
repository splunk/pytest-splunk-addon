import pytest
from unittest.mock import patch, MagicMock, call
from collections import namedtuple
from pytest_splunk_addon.cim_tests.data_model import DataModel


@pytest.fixture()
def data_set_mock(monkeypatch):
    data_set_mock = MagicMock()
    data_set_mock.return_value = data_set_mock
    data_set_mock.load_dataset.return_value = ["dataset1", "dataset2"]
    monkeypatch.setattr(
        "pytest_splunk_addon.cim_tests.data_model.DataSet", data_set_mock
    )
    return data_set_mock


def test_data_model_instantiation(data_set_mock):
    data_model = DataModel({"model_name": "test_model_name", "objects": []})
    assert data_model.name == "test_model_name"
    assert data_model.root_data_set == ["dataset1", "dataset2"]


def test_data_model_string(data_set_mock):
    data_model = DataModel({"model_name": "test_model_name", "objects": []})
    assert str(data_model) == data_model.name == "test_model_name"


def test_get_mapped_datasets_calls_internal_function():
    m1 = MagicMock()
    m1.side_effect = lambda x, y: (i for i in range(3))
    with patch.object(DataModel, "__init__", return_value=None), patch.object(
        DataModel, "_get_mapped_datasets", m1
    ):
        data_model = DataModel({})
        data_model.root_data_set = ["root_data_set"]
        assert list(data_model.get_mapped_datasets(["addons_tags"])) == [0, 1, 2]
        m1.assert_has_calls([call(["addons_tags"], ["root_data_set"])])


def test__get_mapped_datasets():
    data_set = namedtuple("DataSet", ["name", "match_tags", "child_dataset"])
    dataset1 = data_set(
        "dataset1",
        lambda x: True,
        [
            data_set("dataset1a", lambda x: True, []),
            data_set(
                "dataset1b",
                lambda x: False,
                [data_set("dataset1c", lambda x: True, [])],
            ),
        ],
    )
    dataset2 = data_set("dataset2", lambda x: True, [])
    with patch.object(DataModel, "__init__", return_value=None):
        data_model = DataModel({})
    assert list(data_model._get_mapped_datasets([], [dataset1, dataset2])) == [
        [dataset1],
        [dataset1, dataset1.child_dataset[0]],
        [dataset2],
    ]
