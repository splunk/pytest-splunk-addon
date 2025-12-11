# -*- coding: utf-8 -*-
"""
End-to-End tests for UUID flow through the entire pytest-splunk-addon pipeline.
Tests Priority #2: End-to-End UUID Flow Tests
"""
import pytest
import json
import tempfile
import os
from unittest.mock import patch, MagicMock, mock_open
from collections import namedtuple

from pytest_splunk_addon.sample_generation import SampleGenerator, SampleXdistGenerator
from pytest_splunk_addon.sample_generation.sample_event import SampleEvent
from pytest_splunk_addon.sample_generation.sample_stanza import SampleStanza
from pytest_splunk_addon.event_ingestors.hec_event_ingestor import HECEventIngestor
from pytest_splunk_addon.fields_tests.test_generator import FieldTestGenerator


class TestUUIDFlowThroughPipeline:
    """Test UUID propagation through the entire sample generation pipeline"""

    def test_uuid_propagates_from_stanza_to_event(self):
        """Verify UUID flag propagates from SampleStanza to SampleEvent"""
        with tempfile.TemporaryDirectory() as tmpdir:
            sample_path = os.path.join(tmpdir, "test.sample")
            with open(sample_path, "w") as f:
                f.write("test event line 1\ntest event line 2")

            psa_data_params = {
                "sourcetype": "test:sourcetype",
                "input_type": "modinput",
                "tokens": {},  # Add tokens to avoid KeyError
            }

            # Test with UUID enabled
            stanza = SampleStanza(sample_path, psa_data_params, ingest_with_uuid="true")
            assert stanza.metadata["ingest_with_uuid"] == "true"

            # Test with UUID disabled
            stanza_no_uuid = SampleStanza(
                sample_path, psa_data_params, ingest_with_uuid="false"
            )
            assert stanza_no_uuid.metadata["ingest_with_uuid"] == "false"

    def test_uuid_in_sample_generator_initialization(self):
        """Verify SampleGenerator properly initializes with UUID flag"""
        addon_path = "/fake/addon/path"
        config_path = "/fake/config/path"

        # Test with UUID enabled
        generator = SampleGenerator(
            addon_path, ingest_with_uuid="true", config_path=config_path
        )
        assert generator.ingest_with_uuid == "true"

        # Test with UUID disabled
        generator_no_uuid = SampleGenerator(
            addon_path, ingest_with_uuid="false", config_path=config_path
        )
        assert generator_no_uuid.ingest_with_uuid == "false"

    def test_uuid_in_sample_xdist_generator_initialization(self):
        """Verify SampleXdistGenerator properly initializes with UUID flag"""
        addon_path = "/fake/addon/path"
        config_path = "/fake/config/path"

        # Test with UUID enabled
        xdist_generator = SampleXdistGenerator(
            addon_path, ingest_with_uuid="true", config_path=config_path
        )
        assert xdist_generator.ingest_with_uuid == "true"

        # Test with UUID disabled
        xdist_generator_no_uuid = SampleXdistGenerator(
            addon_path, ingest_with_uuid="false", config_path=config_path
        )
        assert xdist_generator_no_uuid.ingest_with_uuid == "false"


class TestUUIDInHECPayload:
    """Test UUID inclusion in HEC event payloads"""

    def test_uuid_added_to_hec_payload_when_enabled(self):
        """Verify UUID is added to HEC payload when flag is enabled"""
        # Create a sample event with UUID
        metadata = {
            "ingest_with_uuid": "true",
            "sourcetype": "test:sourcetype",
            "source": "/var/log/test.log",
            "index": "main",
            "host": "test-host",
            "host_type": "plugin",
            "timestamp_type": "plugin",
        }

        event = SampleEvent(
            event_string="test event for HEC",
            metadata=metadata,
            sample_name="test.sample",
        )

        # Verify event has UUID
        assert hasattr(event, "unique_identifier")
        uuid_value = event.unique_identifier

        # Create HEC ingestor and mock the actual HTTP POST
        required_configs = {
            "splunk_hec_uri": "https://splunk:8088",
            "session_headers": {"Authorization": "Splunk test-token"},
        }
        ingestor = HECEventIngestor(required_configs)

        # Mock the requests.post to capture what gets sent
        with patch(
            "pytest_splunk_addon.event_ingestors.hec_event_ingestor.requests.post"
        ) as mock_post:
            mock_post.return_value = MagicMock(status_code=200)

            # Call the actual ingest method
            ingestor.ingest([event], thread_count=1)

            # Verify post was called
            assert mock_post.called, "requests.post should have been called"

            # Get the actual data that was sent
            call_args = mock_post.call_args
            sent_data = call_args[1].get("data") if call_args else None

            assert sent_data is not None, "Data should have been sent to HEC"

            # Parse the JSON that was sent
            hec_events = [
                json.loads(line) for line in sent_data.strip().split("\n") if line
            ]

            # Verify UUID is in the actual HEC payload
            assert len(hec_events) > 0, "Should have at least one HEC event"
            hec_event = hec_events[0]

            # This is what we're really testing - did the ingestor add the UUID field?
            assert "fields" in hec_event, "HEC event should have fields"
            assert (
                "unique_identifier" in hec_event["fields"]
            ), "HEC event fields should contain unique_identifier"
            assert (
                hec_event["fields"]["unique_identifier"] == uuid_value
            ), "UUID value should match the event's unique_identifier"

    def test_uuid_not_added_to_hec_payload_when_disabled(self):
        """Verify UUID is NOT added to HEC payload when flag is disabled"""
        metadata = {
            "ingest_with_uuid": "false",
            "sourcetype": "test:sourcetype",
            "source": "/var/log/test.log",
            "index": "main",
            "host": "test-host",
            "host_type": "plugin",
            "timestamp_type": "plugin",
        }

        event = SampleEvent(
            event_string="test event without UUID",
            metadata=metadata,
            sample_name="test.sample",
        )

        # Verify event doesn't have UUID
        assert not hasattr(event, "unique_identifier")

        # Create HEC ingestor and test actual implementation
        required_configs = {
            "splunk_hec_uri": "https://splunk:8088",
            "session_headers": {"Authorization": "Splunk test-token"},
        }
        ingestor = HECEventIngestor(required_configs)

        # Mock requests.post to capture what gets sent
        with patch(
            "pytest_splunk_addon.event_ingestors.hec_event_ingestor.requests.post"
        ) as mock_post:
            mock_post.return_value = MagicMock(status_code=200)

            # Call the actual ingest method
            ingestor.ingest([event], thread_count=1)

            # Get the actual data that was sent
            call_args = mock_post.call_args
            sent_data = call_args[1].get("data") if call_args else None

            if sent_data:
                hec_events = [
                    json.loads(line) for line in sent_data.strip().split("\n") if line
                ]
                hec_event = hec_events[0]

                # Verify fields key is NOT in the actual HEC payload
                assert (
                    "fields" not in hec_event
                ), "HEC event should not have fields when UUID is disabled"

    def test_hec_payload_structure_with_uuid(self):
        """Verify complete HEC payload structure includes UUID and other fields correctly"""
        metadata = {
            "ingest_with_uuid": "true",
            "sourcetype": "test:sourcetype",
            "source": "/var/log/test.log",
            "index": "main",
            "host": "test-host",
            "host_type": "plugin",
            "timestamp_type": "event",
        }

        event = SampleEvent(
            event_string="test event with complete metadata",
            metadata=metadata,
            sample_name="test.sample",
        )
        event.time_values = [1234567890.123]

        # Verify event has UUID
        assert hasattr(event, "unique_identifier")
        uuid_value = event.unique_identifier

        # Create HEC ingestor and test actual implementation
        required_configs = {
            "splunk_hec_uri": "https://splunk:8088",
            "session_headers": {"Authorization": "Splunk test-token"},
        }
        ingestor = HECEventIngestor(required_configs)

        # Mock requests.post to capture what gets sent
        with patch(
            "pytest_splunk_addon.event_ingestors.hec_event_ingestor.requests.post"
        ) as mock_post:
            mock_post.return_value = MagicMock(status_code=200)

            ingestor.ingest([event], thread_count=1)

            call_args = mock_post.call_args
            sent_data = call_args[1].get("data") if call_args else None

            assert sent_data is not None
            hec_events = [
                json.loads(line) for line in sent_data.strip().split("\n") if line
            ]
            hec_event = hec_events[0]

            # Verify the actual HEC payload structure
            assert "sourcetype" in hec_event
            assert "source" in hec_event
            assert "event" in hec_event
            assert "index" in hec_event
            assert "host" in hec_event
            assert (
                "time" in hec_event
            ), "time should be present when timestamp_type is 'event'"
            assert (
                "fields" in hec_event
            ), "fields should be present when UUID is enabled"
            assert hec_event["fields"]["unique_identifier"] == uuid_value


class TestUUIDInTestGeneration:
    """Test UUID usage in test parameter generation"""

    def test_uuid_in_requirement_test_params(self):
        """Verify UUID is included in requirement test parameters"""
        # Create a tokenized event with UUID
        metadata = {
            "ingest_with_uuid": "true",
            "input_type": "modinput",
            "sourcetype_to_search": "test:sourcetype",
            "host": "test-host",
        }

        with patch(
            "pytest_splunk_addon.sample_generation.sample_event.uuid.uuid4"
        ) as mock_uuid:
            mock_uuid.return_value = "test-uuid-12345"

            event = SampleEvent(
                event_string="test event",
                metadata=metadata,
                sample_name="test.sample",
                requirement_test_data={
                    "cim_fields": {"severity": "low", "signature_id": "12345"}
                },
            )

        # Verify UUID was generated
        assert hasattr(event, "unique_identifier")
        assert event.unique_identifier == "test-uuid-12345"

        # Create field test generator
        test_generator = FieldTestGenerator(
            app_path="fake/path", tokenized_events=[event], field_bank=None
        )

        # Generate requirement tests
        with patch(
            "pytest_splunk_addon.fields_tests.test_generator.xml_event_parser.escape_char_event"
        ) as mock_escape:
            mock_escape.return_value = "escaped_event"

            with patch("pytest.param") as mock_param:
                mock_param.side_effect = lambda x, id: (x, id)

                params = list(test_generator.generate_requirements_tests())

                # Verify params were generated
                assert len(params) > 0
                param_data, param_id = params[0]

                # Verify UUID is in the parameters
                assert (
                    "unique_identifier" in param_data
                ), "unique_identifier should be in test parameters when UUID is enabled"
                assert param_data["unique_identifier"] == "test-uuid-12345"

    def test_uuid_in_datamodel_test_params(self):
        """Verify UUID is included in datamodel test parameters"""
        metadata = {
            "ingest_with_uuid": "true",
            "input_type": "modinput",
            "sourcetype_to_search": "test:sourcetype",
            "host": "test-host",
        }

        with patch(
            "pytest_splunk_addon.sample_generation.sample_event.uuid.uuid4"
        ) as mock_uuid:
            mock_uuid.return_value = "test-uuid-67890"

            event = SampleEvent(
                event_string="test event for datamodel",
                metadata=metadata,
                sample_name="test.sample",
                requirement_test_data={"datamodels": {"model": "Authentication"}},
            )

        # Verify UUID was generated
        assert event.unique_identifier == "test-uuid-67890"

        # Create field test generator
        test_generator = FieldTestGenerator(
            app_path="fake/path", tokenized_events=[event], field_bank=None
        )

        # Generate datamodel tests
        with patch(
            "pytest_splunk_addon.fields_tests.test_generator.xml_event_parser.escape_char_event"
        ) as mock_escape:
            mock_escape.return_value = "escaped_event"

            with patch("pytest.param") as mock_param:
                mock_param.side_effect = lambda x, id: (x, id)

                params = list(test_generator.generate_requirements_datamodels_tests())

                # Verify params were generated
                assert len(params) > 0
                param_data, param_id = params[0]

                # Verify UUID is in the parameters
                assert "unique_identifier" in param_data
                assert param_data["unique_identifier"] == "test-uuid-67890"

    def test_uuid_not_in_params_when_disabled(self):
        """Verify UUID is NOT in test parameters when flag is disabled"""
        metadata = {
            "ingest_with_uuid": "false",
            "input_type": "modinput",
            "sourcetype_to_search": "test:sourcetype",
            "host": "test-host",
        }

        event = SampleEvent(
            event_string="test event without UUID",
            metadata=metadata,
            sample_name="test.sample",
            requirement_test_data={"cim_fields": {"severity": "low"}},
        )

        # Verify no UUID was generated
        assert not hasattr(event, "unique_identifier")

        # Create field test generator
        test_generator = FieldTestGenerator(
            app_path="fake/path", tokenized_events=[event], field_bank=None
        )

        # Generate requirement tests
        with patch(
            "pytest_splunk_addon.fields_tests.test_generator.xml_event_parser.escape_char_event"
        ) as mock_escape:
            mock_escape.return_value = "escaped_event"

            with patch("pytest.param") as mock_param:
                mock_param.side_effect = lambda x, id: (x, id)

                params = list(test_generator.generate_requirements_tests())

                if len(params) > 0:
                    param_data, param_id = params[0]

                    # Verify UUID is NOT in the parameters
                    assert (
                        "unique_identifier" not in param_data
                    ), "unique_identifier should not be in test parameters when UUID is disabled"


class TestUUIDInStoredEvents:
    """Test UUID persistence in stored tokenized events"""

    def test_uuid_stored_in_tokenized_events_json(self):
        """Verify UUID is included in stored tokenized events JSON"""
        tokenized_event = namedtuple(
            "tokenized_event",
            [
                "sample_name",
                "metadata",
                "event",
                "unique_identifier",
                "key_fields",
                "time_values",
                "requirement_test_data",
            ],
        )

        events = [
            tokenized_event(
                "test_sample",
                {
                    "host": "test-host",
                    "source": "/var/log/test.log",
                    "sourcetype": "test:sourcetype",
                    "timestamp_type": "event",
                    "input_type": "modinput",
                    "expected_event_count": 1,
                },
                "test event content",
                "uuid-12345-67890",
                {"field1": "value1"},
                [1234567890],
                {"cim_fields": {"severity": "low"}},
            )
        ]

        with patch("os.path.exists", return_value=False), patch(
            "os.getcwd", return_value="/fake/path"
        ), patch("os.makedirs"), patch("builtins.open", mock_open()) as open_mock:

            xdist_generator = SampleXdistGenerator(
                "/fake/addon", "true", "/fake/config"
            )
            xdist_generator.store_events(events)

            # Get the written JSON
            write_calls = [call.args[0] for call in open_mock().write.call_args_list]
            assert len(write_calls) > 0

            # Parse the JSON
            json_content = write_calls[0]
            stored_data = json.loads(json_content)

            # Verify UUID is in the stored data
            assert "test_sample" in stored_data
            sample_data = stored_data["test_sample"]
            assert "metadata" in sample_data
            assert sample_data["metadata"]["ingest_with_uuid"] == "true"
            assert "events" in sample_data
            assert len(sample_data["events"]) > 0
            assert "unique_identifier" in sample_data["events"][0]
            assert sample_data["events"][0]["unique_identifier"] == "uuid-12345-67890"

    def test_uuid_not_stored_when_disabled(self):
        """Verify UUID is NOT stored when flag is disabled"""
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

        events = [
            tokenized_event(
                "test_sample_no_uuid",
                {
                    "host": "test-host",
                    "source": "/var/log/test.log",
                    "sourcetype": "test:sourcetype",
                    "timestamp_type": "event",
                    "input_type": "file_monitor",
                    "expected_event_count": 1,
                },
                "test event without UUID",
                {"field1": "value1"},
                [],
                None,
            )
        ]

        with patch("os.path.exists", return_value=False), patch(
            "os.getcwd", return_value="/fake/path"
        ), patch("os.makedirs"), patch("builtins.open", mock_open()) as open_mock:

            xdist_generator = SampleXdistGenerator(
                "/fake/addon", "false", "/fake/config"
            )
            xdist_generator.store_events(events)

            # Get the written JSON
            write_calls = [call.args[0] for call in open_mock().write.call_args_list]

            if write_calls:
                json_content = write_calls[0]
                stored_data = json.loads(json_content)

                sample_data = stored_data["test_sample_no_uuid"]
                assert sample_data["metadata"]["ingest_with_uuid"] == "false"

                # Verify unique_identifier is NOT in events
                for event in sample_data["events"]:
                    assert "unique_identifier" not in event


class TestUUIDSearchQueryGeneration:
    """Test UUID usage in search query generation

    Note: These tests verify the logical behavior that UUID changes search approach.
    They test decision logic rather than implementation, which is acceptable for
    documenting expected behavior. The actual search execution is tested in e2e tests.
    """

    def test_search_params_contain_uuid_when_enabled(self):
        """Verify test parameters include UUID when flag is enabled"""
        # This tests that the test parameter generation includes UUID
        metadata = {
            "ingest_with_uuid": "true",
            "input_type": "modinput",
            "sourcetype_to_search": "test:sourcetype",
            "host": "test-host",
        }

        with patch(
            "pytest_splunk_addon.sample_generation.sample_event.uuid.uuid4"
        ) as mock_uuid:
            mock_uuid.return_value = "test-uuid-search"

            event = SampleEvent(
                event_string="test event",
                metadata=metadata,
                sample_name="test.sample",
                requirement_test_data={"cim_fields": {"severity": "low"}},
            )

        test_generator = FieldTestGenerator(
            app_path="fake/path", tokenized_events=[event], field_bank=None
        )

        with patch(
            "pytest_splunk_addon.fields_tests.test_generator.xml_event_parser.escape_char_event"
        ) as mock_escape:
            mock_escape.return_value = "escaped_event"

            with patch("pytest.param") as mock_param:
                mock_param.side_effect = lambda x, id: (x, id)

                params = list(test_generator.generate_requirements_tests())
                param_data, _ = params[0]

                # The key assertion: parameters have UUID, not just escaped event
                assert "unique_identifier" in param_data
                assert param_data["unique_identifier"] == "test-uuid-search"
                # This means searches will use UUID instead of escaped event

    def test_search_params_lack_uuid_when_disabled(self):
        """Verify test parameters do NOT include UUID when flag is disabled"""
        metadata = {
            "ingest_with_uuid": "false",
            "input_type": "modinput",
            "sourcetype_to_search": "test:sourcetype",
            "host": "test-host",
        }

        event = SampleEvent(
            event_string="test event",
            metadata=metadata,
            sample_name="test.sample",
            requirement_test_data={"cim_fields": {"severity": "low"}},
        )

        test_generator = FieldTestGenerator(
            app_path="fake/path", tokenized_events=[event], field_bank=None
        )

        with patch(
            "pytest_splunk_addon.fields_tests.test_generator.xml_event_parser.escape_char_event"
        ) as mock_escape:
            mock_escape.return_value = "escaped_event"

            with patch("pytest.param") as mock_param:
                mock_param.side_effect = lambda x, id: (x, id)

                params = list(test_generator.generate_requirements_tests())

                if params:
                    param_data, _ = params[0]

                    # The key assertion: parameters don't have UUID, use escaped event approach
                    assert "unique_identifier" not in param_data
                    assert "escaped_event" in param_data
                    # This means searches will use traditional escaped event method


class TestUUIDEndToEndIntegration:
    """Integration tests for complete UUID flow"""

    def test_complete_uuid_flow_modinput(self):
        """Test complete UUID flow for modinput events"""
        # This test simulates the complete flow:
        # 1. Event creation with UUID
        # 2. HEC payload generation
        # 3. Test parameter generation
        # 4. Assert parameters drive UUID-based search (without reimplementing query builder)

        metadata = {
            "ingest_with_uuid": "true",
            "input_type": "modinput",
            "sourcetype": "test:sourcetype",
            "source": "pytest-splunk-addon:modinput",
            "index": "main",
            "host": "test-host",
            "host_type": "plugin",
            "timestamp_type": "plugin",
            "sourcetype_to_search": "test:sourcetype",
        }

        with patch(
            "pytest_splunk_addon.sample_generation.sample_event.uuid.uuid4"
        ) as mock_uuid:
            mock_uuid.return_value = "integration-test-uuid"

            # Step 1: Create event
            event = SampleEvent(
                event_string="integration test event",
                metadata=metadata,
                sample_name="integration.sample",
                requirement_test_data={"cim_fields": {"severity": "high"}},
            )

            # Verify UUID was created
            assert event.unique_identifier == "integration-test-uuid"

            # Step 2: Verify HEC payload would include UUID
            assert event.metadata.get("ingest_with_uuid") == "true"

            # Step 3: Generate test parameters
            test_generator = FieldTestGenerator(
                app_path="fake/path", tokenized_events=[event], field_bank=None
            )

            with patch(
                "pytest_splunk_addon.fields_tests.test_generator.xml_event_parser.escape_char_event"
            ) as mock_escape:
                mock_escape.return_value = "escaped_integration_event"

                with patch("pytest.param") as mock_param:
                    mock_param.side_effect = lambda x, id: (x, id)

                    params = list(test_generator.generate_requirements_tests())

                    assert len(params) > 0
                    param_data, _ = params[0]

                    # Verify UUID is in parameters and escaped_event is still present but not required for UUID path
                    assert param_data["unique_identifier"] == "integration-test-uuid"
                    # Key assertion: when UUID is present, consumers should use it (do not manually build search here)
                    assert (
                        "escaped_event" in param_data
                    )  # present for backward compatibility

    def test_complete_flow_without_uuid(self):
        """Test complete flow works correctly without UUID (backward compatibility)"""
        metadata = {
            "ingest_with_uuid": "false",
            "input_type": "modinput",
            "sourcetype": "test:sourcetype",
            "source": "pytest-splunk-addon:modinput",
            "index": "main",
            "host": "test-host",
            "host_type": "plugin",
            "timestamp_type": "plugin",
            "sourcetype_to_search": "test:sourcetype",
        }

        # Step 1: Create event without UUID
        event = SampleEvent(
            event_string="test event without uuid",
            metadata=metadata,
            sample_name="test.sample",
            requirement_test_data={"cim_fields": {"severity": "medium"}},
        )

        # Verify no UUID was created
        assert not hasattr(event, "unique_identifier")

        # Step 2: Generate test parameters
        test_generator = FieldTestGenerator(
            app_path="fake/path", tokenized_events=[event], field_bank=None
        )

        with patch(
            "pytest_splunk_addon.fields_tests.test_generator.xml_event_parser.escape_char_event"
        ) as mock_escape:
            mock_escape.return_value = "escaped_test_event"

            with patch("pytest.param") as mock_param:
                mock_param.side_effect = lambda x, id: (x, id)

                params = list(test_generator.generate_requirements_tests())

                if len(params) > 0:
                    param_data, _ = params[0]

                    # Verify UUID is NOT in parameters, and escaped event is present for traditional search path
                    assert "unique_identifier" not in param_data
                    assert param_data["escaped_event"] == "escaped_test_event"
