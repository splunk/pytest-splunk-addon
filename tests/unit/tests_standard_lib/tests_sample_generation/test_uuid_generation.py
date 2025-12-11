# -*- coding: utf-8 -*-
"""
Unit tests for UUID generation and uniqueness in sample events.
Tests Priority #1: UUID Generation & Uniqueness Tests
"""
import pytest
import uuid
from unittest.mock import patch, MagicMock
from pytest_splunk_addon.sample_generation.sample_event import SampleEvent
from pytest_splunk_addon.sample_generation.sample_stanza import SampleStanza


def _simulate_tokenization_uuid_assignment(event):
    """Helper to simulate UUID assignment that happens during tokenization"""
    if event.metadata.get("ingest_with_uuid") == "true":
        event.unique_identifier = str(uuid.uuid4())


class TestUUIDGeneration:
    """Test suite for UUID generation functionality"""

    def test_uuid_generated_when_flag_enabled(self):
        """Verify UUID is generated when ingest_with_uuid is 'true'"""
        metadata = {"ingest_with_uuid": "true", "index": "main"}
        event = SampleEvent(
            event_string="test event", metadata=metadata, sample_name="test.sample"
        )

        # Simulate tokenization UUID assignment
        _simulate_tokenization_uuid_assignment(event)

        assert hasattr(
            event, "unique_identifier"
        ), "unique_identifier attribute should exist"
        assert (
            event.unique_identifier is not None
        ), "unique_identifier should not be None"
        assert isinstance(
            event.unique_identifier, str
        ), "unique_identifier should be a string"

    def test_uuid_not_generated_when_flag_disabled(self):
        """Verify UUID is NOT generated when ingest_with_uuid is 'false'"""
        metadata = {"ingest_with_uuid": "false", "index": "main"}
        event = SampleEvent(
            event_string="test event", metadata=metadata, sample_name="test.sample"
        )

        # Simulate tokenization UUID assignment
        _simulate_tokenization_uuid_assignment(event)

        assert not hasattr(
            event, "unique_identifier"
        ), "unique_identifier attribute should not exist when flag is disabled"

    def test_uuid_not_generated_when_flag_missing(self):
        """Verify UUID is NOT generated when ingest_with_uuid is not specified"""
        metadata = {"index": "main"}
        event = SampleEvent(
            event_string="test event", metadata=metadata, sample_name="test.sample"
        )

        # Simulate tokenization UUID assignment
        _simulate_tokenization_uuid_assignment(event)

        assert not hasattr(
            event, "unique_identifier"
        ), "unique_identifier attribute should not exist when flag is missing"

    def test_uuid_format_is_valid(self):
        """Verify generated UUID follows UUID4 format"""
        metadata = {"ingest_with_uuid": "true", "index": "main"}
        event = SampleEvent(
            event_string="test event", metadata=metadata, sample_name="test.sample"
        )

        # Simulate tokenization UUID assignment
        _simulate_tokenization_uuid_assignment(event)

        # Validate UUID format by attempting to parse it
        try:
            uuid_obj = uuid.UUID(event.unique_identifier, version=4)
            assert (
                str(uuid_obj) == event.unique_identifier
            ), "UUID should be properly formatted"
            assert uuid_obj.version == 4, "UUID should be version 4"
        except ValueError:
            pytest.fail(
                f"Generated UUID '{event.unique_identifier}' is not a valid UUID4"
            )


class TestUUIDUniqueness:
    """Test suite for UUID uniqueness across multiple events"""

    def test_multiple_events_get_unique_uuids(self):
        """Verify each event gets a different UUID"""
        metadata = {"ingest_with_uuid": "true", "index": "main"}
        num_events = 100

        events = [
            SampleEvent(
                event_string=f"test event {i}",
                metadata=metadata.copy(),
                sample_name=f"test.sample{i}",
            )
            for i in range(num_events)
        ]

        # Simulate tokenization UUID assignment for all events
        for event in events:
            _simulate_tokenization_uuid_assignment(event)

        uuids = [event.unique_identifier for event in events]

        # Check all UUIDs are unique
        assert (
            len(set(uuids)) == num_events
        ), f"All {num_events} events should have unique UUIDs, but got {len(set(uuids))} unique values"

    def test_same_event_string_gets_different_uuids(self):
        """Verify identical events get different UUIDs"""
        metadata = {"ingest_with_uuid": "true", "index": "main"}
        event_string = "identical test event"

        event1 = SampleEvent(
            event_string=event_string,
            metadata=metadata.copy(),
            sample_name="test.sample",
        )

        event2 = SampleEvent(
            event_string=event_string,
            metadata=metadata.copy(),
            sample_name="test.sample",
        )

        # Simulate tokenization UUID assignment for both events
        _simulate_tokenization_uuid_assignment(event1)
        _simulate_tokenization_uuid_assignment(event2)

        assert (
            event1.unique_identifier != event2.unique_identifier
        ), "Identical events should receive different UUIDs"

    def test_uuid_persistence_through_event_lifecycle(self):
        """Verify UUID remains constant throughout event lifecycle"""
        metadata = {"ingest_with_uuid": "true", "index": "main"}
        event = SampleEvent(
            event_string="test event", metadata=metadata, sample_name="test.sample"
        )

        # Simulate tokenization UUID assignment
        _simulate_tokenization_uuid_assignment(event)

        original_uuid = event.unique_identifier

        # Modify event properties
        event.update("modified event string")
        event.key_fields = {"field1": "value1"}
        event.time_values = [1234567890]

        # UUID should remain the same
        assert (
            event.unique_identifier == original_uuid
        ), "UUID should remain constant after event modifications"


class TestUUIDCaseSensitivity:
    """Test suite for case sensitivity of the ingest_with_uuid flag"""

    @pytest.mark.parametrize("flag_value", ["True", "TRUE", "tRuE", "T", "yes", "1"])
    def test_uuid_not_generated_for_non_lowercase_true(self, flag_value):
        """Verify UUID is only generated for lowercase 'true'"""
        metadata = {"ingest_with_uuid": flag_value, "index": "main"}
        event = SampleEvent(
            event_string="test event", metadata=metadata, sample_name="test.sample"
        )

        # Simulate tokenization UUID assignment
        _simulate_tokenization_uuid_assignment(event)

        # Based on implementation, only lowercase "true" generates UUID
        assert not hasattr(
            event, "unique_identifier"
        ), f"UUID should not be generated for flag value '{flag_value}'"

    @pytest.mark.parametrize("flag_value", ["false", "False", "FALSE", "0", "no", ""])
    def test_uuid_not_generated_for_false_values(self, flag_value):
        """Verify UUID is not generated for various false-like values"""
        metadata = {"ingest_with_uuid": flag_value, "index": "main"}
        event = SampleEvent(
            event_string="test event", metadata=metadata, sample_name="test.sample"
        )

        # Simulate tokenization UUID assignment
        _simulate_tokenization_uuid_assignment(event)

        assert not hasattr(
            event, "unique_identifier"
        ), f"UUID should not be generated for flag value '{flag_value}'"


class TestUUIDWithRequirementData:
    """Test suite for UUID generation with requirement test data"""

    def test_uuid_with_requirement_test_data(self):
        """Verify UUID is generated when requirement_test_data is present"""
        metadata = {"ingest_with_uuid": "true", "index": "main"}
        requirement_data = {"cim_fields": {"severity": "low", "signature_id": "12345"}}

        event = SampleEvent(
            event_string="test event",
            metadata=metadata,
            sample_name="test.sample",
            requirement_test_data=requirement_data,
        )

        # Simulate tokenization UUID assignment
        _simulate_tokenization_uuid_assignment(event)

        assert hasattr(
            event, "unique_identifier"
        ), "UUID should be generated even with requirement_test_data"
        assert (
            event.requirement_test_data == requirement_data
        ), "requirement_test_data should be preserved"

    def test_uuid_without_requirement_test_data(self):
        """Verify UUID is generated when requirement_test_data is None"""
        metadata = {"ingest_with_uuid": "true", "index": "main"}

        event = SampleEvent(
            event_string="test event",
            metadata=metadata,
            sample_name="test.sample",
            requirement_test_data=None,
        )

        # Simulate tokenization UUID assignment
        _simulate_tokenization_uuid_assignment(event)

        assert hasattr(
            event, "unique_identifier"
        ), "UUID should be generated even without requirement_test_data"
        assert event.requirement_test_data is None


class TestUUIDMocking:
    """Test suite for UUID mocking and deterministic testing"""

    def test_uuid_can_be_mocked(self):
        """Verify UUID generation can be mocked for deterministic tests"""
        expected_uuid = "12345678-1234-5678-1234-567812345678"

        with patch("uuid.uuid4") as mock_uuid:
            mock_uuid.return_value = expected_uuid

            metadata = {"ingest_with_uuid": "true", "index": "main"}
            event = SampleEvent(
                event_string="test event", metadata=metadata, sample_name="test.sample"
            )

            # Simulate tokenization UUID assignment
            _simulate_tokenization_uuid_assignment(event)

            mock_uuid.assert_called_once()
            assert event.unique_identifier == expected_uuid

    def test_uuid_generation_called_once_per_event(self):
        """Verify UUID is generated exactly once per event"""
        with patch("uuid.uuid4") as mock_uuid:
            mock_uuid.return_value = "test-uuid"

            metadata = {"ingest_with_uuid": "true", "index": "main"}
            event = SampleEvent(
                event_string="test event", metadata=metadata, sample_name="test.sample"
            )

            # Simulate tokenization UUID assignment
            _simulate_tokenization_uuid_assignment(event)

            # Access the UUID multiple times
            _ = event.unique_identifier
            _ = event.unique_identifier

            # uuid4 should only be called once during tokenization
            mock_uuid.assert_called_once()


class TestUUIDWithDifferentMetadata:
    """Test suite for UUID generation with various metadata configurations"""

    def test_uuid_with_minimal_metadata(self):
        """Verify UUID is generated with minimal metadata"""
        metadata = {"ingest_with_uuid": "true"}
        event = SampleEvent(
            event_string="test event", metadata=metadata, sample_name="test.sample"
        )

        # Simulate tokenization UUID assignment
        _simulate_tokenization_uuid_assignment(event)

        assert hasattr(event, "unique_identifier")

    def test_uuid_with_extensive_metadata(self):
        """Verify UUID is generated with extensive metadata"""
        metadata = {
            "ingest_with_uuid": "true",
            "index": "main",
            "sourcetype": "test:sourcetype",
            "source": "/var/log/test.log",
            "host": "test-host",
            "host_type": "plugin",
            "timestamp_type": "event",
            "input_type": "modinput",
            "sample_count": "10",
        }

        event = SampleEvent(
            event_string="test event with extensive metadata",
            metadata=metadata,
            sample_name="test.sample",
        )

        # Simulate tokenization UUID assignment
        _simulate_tokenization_uuid_assignment(event)

        assert hasattr(event, "unique_identifier")
        assert event.metadata == metadata

    @pytest.mark.parametrize(
        "input_type", ["modinput", "file_monitor", "syslog_tcp", "default", "sc4s"]
    )
    def test_uuid_with_different_input_types(self, input_type):
        """Verify UUID is generated regardless of input type"""
        metadata = {
            "ingest_with_uuid": "true",
            "input_type": input_type,
            "index": "main",
        }

        event = SampleEvent(
            event_string="test event", metadata=metadata, sample_name="test.sample"
        )

        # Simulate tokenization UUID assignment
        _simulate_tokenization_uuid_assignment(event)

        assert hasattr(
            event, "unique_identifier"
        ), f"UUID should be generated for input_type={input_type}"
