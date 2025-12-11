# -*- coding: utf-8 -*-
"""
Test for UUID timing fix - ensures UUIDs are assigned per finalized event after tokenization.
"""
import pytest
import tempfile
import os
from pytest_splunk_addon.sample_generation.sample_stanza import SampleStanza


class TestUUIDTokenizationTiming:
    """Test UUID assignment timing during tokenization"""

    def test_uuid_assigned_post_tokenization(self):
        """Test that UUIDs are assigned after tokenization, ensuring uniqueness per event"""

        with tempfile.TemporaryDirectory() as tmpdir:
            sample_path = os.path.join(tmpdir, "test.sample")
            with open(sample_path, "w") as f:
                # Multiple events to ensure we get multiple UUIDs
                f.write("Event 1\nEvent 2\nEvent 3\n")

            psa_data_params = {
                "sourcetype": "test:sourcetype",
                "input_type": "modinput",  # This will create one event per line
                "tokens": {},  # No tokens needed for this test
            }

            stanza = SampleStanza(sample_path, psa_data_params, ingest_with_uuid=True)

            # Tokenize to generate events with UUIDs
            stanza.tokenize("psa-data-gen")

            events = stanza.tokenized_events

            # Verify events were created
            assert (
                len(events) >= 3
            ), f"Should create events for each line, got {len(events)}"

            # Collect UUIDs
            uuids = []
            for event in events:
                assert hasattr(
                    event, "unique_identifier"
                ), f"Event should have unique_identifier: {event.event}"
                assert event.unique_identifier is not None, "UUID should not be None"
                assert (
                    len(event.unique_identifier) == 36
                ), "UUID should be 36 characters (standard UUID format)"
                uuids.append(event.unique_identifier)

            # Verify all UUIDs are unique (this was the core bug we fixed)
            unique_uuids = set(uuids)
            assert len(unique_uuids) == len(
                uuids
            ), f"All UUIDs should be unique! Got {len(unique_uuids)} unique out of {len(uuids)} total"

            print(
                f"✓ Generated {len(events)} events with {len(unique_uuids)} unique UUIDs"
            )
            print(f"✓ UUID timing fix successful - no duplication across events")

    def test_uuid_not_assigned_when_disabled(self):
        """Test that UUIDs are not assigned when flag is disabled"""

        with tempfile.TemporaryDirectory() as tmpdir:
            sample_path = os.path.join(tmpdir, "test.sample")
            with open(sample_path, "w") as f:
                f.write("Test event without UUID\n")

            psa_data_params = {
                "sourcetype": "test:sourcetype",
                "input_type": "modinput",
                "tokens": {},
            }

            stanza = SampleStanza(
                sample_path, psa_data_params, ingest_with_uuid=False  # UUID disabled
            )

            stanza.tokenize("psa-data-gen")
            events = stanza.tokenized_events

            for event in events:
                assert not hasattr(
                    event, "unique_identifier"
                ), "Event should not have unique_identifier when UUID is disabled"
