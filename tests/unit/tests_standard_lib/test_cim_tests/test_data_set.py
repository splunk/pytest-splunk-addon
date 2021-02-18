import pytest
from unittest.mock import patch, call
from collections import namedtuple
from pytest_splunk_addon.standard_lib.cim_tests.data_set import DataSet

field = namedtuple("Field", ["name"])


@pytest.fixture()
def mocked_dataset_constructor():
    from pytest_splunk_addon.standard_lib.cim_tests.data_set import DataSet, Field

    with patch.object(
        DataSet, "load_dataset", return_value=("child_dataset1", "child_dataset2")
    ), patch.object(
        Field, "parse_fields", return_value=("field1", "field2")
    ), patch.object(
        DataSet,
        "_parse_fields_cluster",
        return_value="parse_field_cluster_return_value",
    ), patch.object(
        DataSet, "_parse_constraint", return_value="prase_constraints_return_value"
    ):
        return DataSet(
            {
                "name": "dataset1",
                "tags": ["test_tag1", "test_tag2"],
                "child_dataset": [],
                "fields": [{"name": "app"}],
                "fields_cluster": [],
                "search_constraints": "tag=alert",
            },
            "test_data_model",
        )


@pytest.fixture()
def dataset_mock():
    with patch.object(DataSet, "__init__", return_value=None):
        dataset = DataSet({}, "test_data_model")
    dataset.name = "dataset2"
    dataset.fields = [
        field("bytes"),
        field("bytes_in"),
        field("bytes_out"),
        field("dest"),
        field("dest_ip"),
        field("dest_mac"),
    ]
    dataset.tags = [["tag1", "tag1b"], ["tag2", "tag3"]]
    return dataset


def test_dataset_can_be_loaded():
    with patch.object(DataSet, "__init__", return_value=None) as data_set_mock:
        list(
            DataSet.load_dataset(
                [
                    {"name": "dataset1", "tags": ["tag1"]},
                    {"name": "dataset2", "tags": ["tag2"]},
                ],
                "test",
            )
        )
    data_set_mock.assert_has_calls(
        [
            call({"name": "dataset1", "tags": ["tag1"]}, "test"),
            call({"name": "dataset2", "tags": ["tag2"]}, "test"),
        ]
    )


def test_dataset_instantiation(mocked_dataset_constructor):
    assert mocked_dataset_constructor.name == "dataset1"
    assert mocked_dataset_constructor.tags == ["test_tag1", "test_tag2"]
    assert mocked_dataset_constructor.data_model == "test_data_model"
    assert mocked_dataset_constructor.child_dataset == [
        "child_dataset1",
        "child_dataset2",
    ]
    assert mocked_dataset_constructor.fields == ["field1", "field2"]
    assert (
        mocked_dataset_constructor.fields_cluster == "parse_field_cluster_return_value"
    )
    assert (
        mocked_dataset_constructor.search_constraints
        == "prase_constraints_return_value"
    )


def test_dataset_string(mocked_dataset_constructor):
    assert (
        mocked_dataset_constructor.name == str(mocked_dataset_constructor) == "dataset1"
    )


def test_parse_constraints():
    assert DataSet._parse_constraint("constraints") == "constraints"


def test_parse_fields_cluster(dataset_mock):
    assert dataset_mock._parse_fields_cluster(
        [["bytes", "bytes_in", "bytes_out"], ["dest", "dest_ip", "dest_mac"]]
    ) == [
        [field("bytes"), field("bytes_in"), field("bytes_out")],
        [field("dest"), field("dest_ip"), field("dest_mac")],
    ]


def test_parse_fields_raises_error_when_cluster_field_not_in_fields_list(dataset_mock):
    with pytest.raises(
        AssertionError,
        match="Dataset=dataset2, Each cluster field should be included in fields list",
    ):
        dataset_mock._parse_fields_cluster(
            [["bytes", "bytes_in", "bytes_out", "bytes_all"]]
        )


def test_tags_match(dataset_mock):
    assert dataset_mock.match_tags(["tag1", "tag1a", "tag2", "tag3"]) is True


def test_tags_not_match(dataset_mock):
    assert dataset_mock.match_tags(["tag1", "tag1a", "tag2"]) is None
