import os
import tempfile

import pytest

from pytest_splunk_addon.sample_generation import (
    PytestSplunkAddonDataParser,
)


def test_psa_data_when_no_config():
    with tempfile.TemporaryDirectory() as tempdir:
        with pytest.raises(FileNotFoundError):
            psa_data_parser = PytestSplunkAddonDataParser(tempdir, tempdir)
            _ = psa_data_parser.psa_data


def test_path_to_samples():
    path = os.path.join(os.path.dirname(__file__), "test_data")
    psa_data_parser = PytestSplunkAddonDataParser(
        path,
        path,
    )
    assert os.path.join(path, "samples") == psa_data_parser._path_to_samples


def test_get_psa_data_stanzas_with_samples():
    path = os.path.join(os.path.dirname(__file__), "test_data", "with_samples")
    psa_data_parser = PytestSplunkAddonDataParser(
        path,
        path,
    )
    expected_result = {
        "test1.samples": {
            "sourcetype": "test:sourcetype",
            "source": "source://test",
            "input_type": "modinput",
            "host_type": "plugin",
            "sourcetype_to_search": "test:sourcetype",
            "timestamp_type": "event",
            "sample_count": "1",
            "tokens": {
                "test1.samples_0": {
                    "token": "##Timestamp##",
                    "replacementType": "timestamp",
                    "replacement": "%Y-%m-%dT%H:%M:%S",
                    "field": "_time",
                },
                "test1.samples_1": {
                    "token": "##user##",
                    "replacementType": "random",
                    "replacement": 'list["user1@email.com","user2@email.com"]',
                },
                "test1.samples_2": {
                    "token": "##ip##",
                    "replacementType": "random",
                    "replacement": 'src["ipv4"]',
                    "field": "src",
                },
                "test1.samples_3": {
                    "token": "##number##",
                    "replacementType": "random",
                    "replacement": "integer[100000000000000000000:999999999999999999999]",
                },
            },
        },
        "test2.samples": {
            "sourcetype": "test:sourcetype",
            "source": "source://test:text",
            "input_type": "modinput",
            "host_type": "plugin",
            "sourcetype_to_search": "test:sourcetype",
            "timestamp_type": "event",
            "sample_count": "1",
            "tokens": {
                "test2.samples_1": {
                    "token": "##user##",
                    "replacementType": "random",
                    "replacement": 'list["user1@email.com","user2@email.com"]',
                },
                "test2.samples_2": {
                    "token": "##ip##",
                    "replacementType": "random",
                    "replacement": 'src["ipv4"]',
                    "field": "src",
                },
            },
        },
    }
    result = psa_data_parser._get_psa_data_stanzas()
    assert expected_result == result


def test_get_sample_stanzas_without_samples(caplog):
    with tempfile.TemporaryDirectory() as tempdir:
        samples_path = os.path.join(tempdir, "samples")
        os.mkdir(samples_path)
        config_path = os.path.join(
            os.path.dirname(__file__), "test_data", "without_samples"
        )
        parser = PytestSplunkAddonDataParser(
            tempdir,
            config_path,
        )
        parser.get_sample_stanzas()
        assert "No sample file found for stanza : test1.samples" in caplog.messages
        assert "No sample file found for stanza : test2.samples" in caplog.messages
