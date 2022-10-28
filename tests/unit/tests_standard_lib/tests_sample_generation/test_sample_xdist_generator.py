from collections import namedtuple
from unittest.mock import MagicMock, patch, mock_open, call

import pytest

from pytest_splunk_addon.standard_lib.sample_generation.sample_xdist_generator import (
    SampleXdistGenerator,
)

SAMPLES = {"conf_name": "x-name", "tokenized_events": "pickle Rick"}

tokenized_event = namedtuple(
    "tokenized_event",
    [
        "sample_name",
        "metadata",
        "event",
        "key_fields",
        "time_values",
        "requirement_test_data",
    ],
)

tokenized_events = [
    tokenized_event(
        "sample_name_1",
        {
            "expected_event_count": 1,
            "host": "host_1",
            "source": "source_1",
            "sourcetype": "sourcetype_1",
            "timestamp_type": "timestamp_type_1",
            "input_type": "modinput",
        },
        "event_field",
        "key_fields_field",
        "time_values_field",
        "requirement_test_data",
    ),
    tokenized_event(
        "sample_name_2",
        {
            "expected_event_count": 2,
            "host": "host_2",
            "source": "source_2",
            "sourcetype": "sourcetype_2",
            "timestamp_type": "timestamp_type_2",
            "input_type": "input_else",
            "sample_count": 4,
        },
        "event_field",
        "key_fields_field",
        "time_values_field",
        "requirement_test_data",
    ),
    tokenized_event(
        "sample_name_1",
        {
            "expected_event_count": 2,
            "host": "host_2",
            "source": "source_2",
            "sourcetype": "sourcetype_2",
            "timestamp_type": "timestamp_type_2",
            "input_type": "input_else",
            "sample_count": 4,
        },
        "event_field",
        "key_fields_field_3",
        "time_values_field_3",
        "requirement_test_data",
    ),
]


class TestSampleXdistGenerator:
    def test_init(self):
        sample_xdist_generator = SampleXdistGenerator("path", "config_path", 5)
        assert sample_xdist_generator.addon_path == "path"
        assert sample_xdist_generator.config_path == "config_path"
        assert sample_xdist_generator.process_count == 5

    @patch(
        "pytest_splunk_addon.standard_lib.sample_generation.sample_xdist_generator.FileLock",
        MagicMock(),
    )
    @patch("builtins.open", mock_open())
    @patch(
        "pytest_splunk_addon.standard_lib.sample_generation.sample_xdist_generator.pickle"
    )
    @pytest.mark.parametrize(
        "exists_value, environ, expected",
        [
            (
                True,
                {"PYTEST_XDIST_WORKER": "", "PYTEST_XDIST_TESTRUNUID": "fake_id"},
                "pickle_loaded",
            ),
        ],
    )
    def test_get_samples_from_pickle(self, pickle_mock, exists_value, environ, expected):
        pickle_mock.load.return_value = "pickle_loaded"
        sample_xdist_generator = SampleXdistGenerator("path")
        sample_xdist_generator.store_events = MagicMock()
        with patch("os.path.exists", MagicMock(return_value=exists_value)), patch(
            "os.environ",
            environ,
        ), patch(
            "pytest_splunk_addon.standard_lib.sample_generation.sample_xdist_generator.SampleGenerator",
            MagicMock(),
        ) as sample_generator_mock:
            assert sample_xdist_generator.get_samples(True) == expected
            sample_generator_mock.assert_not_called()


    @patch(
        "pytest_splunk_addon.standard_lib.sample_generation.sample_xdist_generator.FileLock",
        MagicMock(),
    )
    @patch("builtins.open", mock_open())
    @patch(
        "pytest_splunk_addon.standard_lib.sample_generation.sample_xdist_generator.pickle"
    )
    @pytest.mark.parametrize(
        "exists_value, environ, expected",
        [
            (
                False,
                {"PYTEST_XDIST_WORKER": "", "PYTEST_XDIST_TESTRUNUID": "fake_id"},
                {"conf_name": "conf_name", "tokenized_events": []},
            ),
            (
                False,
                {"PYTEST_XDIST_TESTRUNUID": "fake_id"},
                {"conf_name": "conf_name", "tokenized_events": []},
            ),
        ],
    )
    def test_get_samples_from_generator(self, pickle_mock, exists_value, environ, expected):
        pickle_mock.load.return_value = "pickle_loaded"
        sample_xdist_generator = SampleXdistGenerator("path")
        sample_xdist_generator.store_events = MagicMock()
        with patch("os.path.exists", MagicMock(return_value=exists_value)), patch(
            "os.environ",
            environ,
        ), patch(
            "pytest_splunk_addon.standard_lib.sample_generation.sample_xdist_generator.SampleGenerator",
            MagicMock(),
        ) as sample_generator_mock:
            sample_xdist_generator.get_samples(True)
            sample_generator_mock.return_value.get_samples_store.assert_called_once()

    @pytest.mark.parametrize(
        "store_events",
        [
            (False),
            (True),
        ],
    )
    def test_get_pregenerated_events(self, store_events):
        with patch(
                "builtins.open", mock_open()), patch(
                "os.path.exists", MagicMock(return_value=True)), patch(
                "pickle.load", MagicMock(return_value=SAMPLES)) as pickle_mock:
            SampleXdistGenerator.tokenized_event_source = "pregenerated"
            sample_xdist_generator = SampleXdistGenerator("path")
            sample_xdist_generator.store_events = MagicMock(name="store_events")
            # Execution
            returnedValue = sample_xdist_generator.get_samples(store_events)
            # Validation
            if store_events:
                sample_xdist_generator.store_events.assert_called_once_with(SAMPLES["tokenized_events"])
            else:
                sample_xdist_generator.store_events.assert_not_called()

            assert returnedValue == SAMPLES

    def test_get_pregenerated_events_store_throws_exception(self):
        with patch(
                "builtins.open", mock_open()), patch(
                "os.path.exists", MagicMock(return_value=True)), patch(
                "pickle.load", MagicMock(return_value=SAMPLES)), patch(
                "pytest.exit", MagicMock()) as exit_mock:
            SampleXdistGenerator.tokenized_event_source = "pregenerated"
            sample_xdist_generator = SampleXdistGenerator("path")
            sample_xdist_generator.store_events = MagicMock(side_effect=Exception("HA!"))
            # Execution
            sample_xdist_generator.get_samples(True)
            # Validation
            exit_mock.assert_called_once_with("HA!")

    @pytest.mark.parametrize(
        "exists_value, makedirs_calls",
        [(True, []), (False, [call("/path/to/cwd/.tokenized_events")])],
    )
    def test_store_events(self, exists_value, makedirs_calls):
        with patch("os.path.exists", MagicMock(return_value=exists_value)), patch(
            "os.getcwd", MagicMock(return_value="/path/to/cwd")
        ), patch("os.makedirs", MagicMock()) as mock_makedirs, patch(
            "builtins.open", mock_open()
        ) as open_mock:
            sample_xdist_generator = SampleXdistGenerator("path")
            sample_xdist_generator.store_events(tokenized_events)
            mock_makedirs.assert_has_calls(makedirs_calls)
            open_mock.assert_has_calls(
                [
                    call("/path/to/cwd/.tokenized_events/sample_name_1.json", "w"),
                    call("/path/to/cwd/.tokenized_events/sample_name_2.json", "w"),
                ],
                any_order=True,
            )
            open_mock().write.assert_has_calls(
                [
                    call(
                        '{\n\t"sample_name_1": {\n\t\t"metadata": {\n\t\t\t"host": "host_1",\n\t\t\t"source": "source_1",\n\t\t\t"sourcetype": "sourcetype_1",\n\t\t\t"timestamp_type": "timestamp_type_1",\n\t\t\t"input_type": "modinput",\n\t\t\t"expected_event_count": 1,\n\t\t\t"index": "main"\n\t\t},\n\t\t"events": [\n\t\t\t{\n\t\t\t\t"event": "event_field",\n\t\t\t\t"key_fields": "key_fields_field",\n\t\t\t\t"time_values": "time_values_field",\n\t\t\t\t"requirement_test_data": "requirement_test_data"\n\t\t\t},\n\t\t\t{\n\t\t\t\t"event": "event_field",\n\t\t\t\t"key_fields": "key_fields_field_3",\n\t\t\t\t"time_values": "time_values_field_3",\n\t\t\t\t"requirement_test_data": "requirement_test_data"\n\t\t\t}\n\t\t]\n\t}\n}'
                    ),
                    call(
                        '{\n\t"sample_name_2": {\n\t\t"metadata": {\n\t\t\t"host": "host_2",\n\t\t\t"source": "source_2",\n\t\t\t"sourcetype": "sourcetype_2",\n\t\t\t"timestamp_type": "timestamp_type_2",\n\t\t\t"input_type": "input_else",\n\t\t\t"expected_event_count": 8,\n\t\t\t"index": "main"\n\t\t},\n\t\t"events": [\n\t\t\t{\n\t\t\t\t"event": "event_field",\n\t\t\t\t"key_fields": "key_fields_field",\n\t\t\t\t"time_values": "time_values_field",\n\t\t\t\t"requirement_test_data": "requirement_test_data"\n\t\t\t}\n\t\t]\n\t}\n}'
                    ),
                ]
            )
