import importlib
from collections import namedtuple
from unittest.mock import MagicMock, patch

import pytest

import pytest_splunk_addon.standard_lib.sample_generation.sample_event

EVENT_STRING = "Event_string dad ad dfd ddas Value_5."
UPDATED_STRING = "Updated_string"
SAMPLE_NAME = "Sample_name"
METADATA = {"Metadata": "metadata"}
RULE = "Rule"
SAMPLE_HOST = "sample_host"
FAKE_IPV4 = "222.222.222.222"
FAKE_IPV6 = "2222:2222:2222:2222:2222:2222"
VALUE_1 = "Value_1."
VALUE_2 = "Value_2"
HOST = "host"


@pytest.fixture
def samp_eve():
    ip_mock = MagicMock()
    ip_mock.ipv4.return_value = FAKE_IPV4
    ip_mock.ipv6.return_value = FAKE_IPV6
    with patch("faker.Faker") as faker_mock:
        faker_mock.return_value = ip_mock
        importlib.reload(
            pytest_splunk_addon.standard_lib.sample_generation.sample_event
        )
    return pytest_splunk_addon.standard_lib.sample_generation.sample_event.SampleEvent(
        event_string=EVENT_STRING,
        metadata=METADATA,
        sample_name=SAMPLE_NAME,
    )


def check_host_count(value):
    assert (
        pytest_splunk_addon.standard_lib.sample_generation.sample_event.host_count
        == value
    )


def check_fqdn_count(value):
    assert (
        pytest_splunk_addon.standard_lib.sample_generation.sample_event.fqdn_count
        == value
    )


def test_update(samp_eve):
    assert samp_eve.event == EVENT_STRING
    samp_eve.update(UPDATED_STRING)
    assert samp_eve.event == UPDATED_STRING


def test_get_host(samp_eve):
    assert samp_eve.get_host() == f"host-{SAMPLE_NAME}-1"
    check_host_count(1)
    assert samp_eve.host_count == 0
    assert samp_eve.get_host() == f"host-{SAMPLE_NAME}-2"
    check_host_count(2)
    assert samp_eve.host_count == 0


def test_get_field_host(samp_eve):
    check_host_count(0)
    assert samp_eve.get_field_host(RULE) == f"{RULE}-{SAMPLE_HOST}1"
    check_host_count(1)


def test_get_field_fqdn(samp_eve):
    check_fqdn_count(0)
    assert samp_eve.get_field_fqdn(RULE) == f"{RULE}_{SAMPLE_HOST}.sample_domain1.com"
    check_fqdn_count(1)


def test_get_ipv4(samp_eve):
    # that test might be divided into many smaller tests,
    # but feels natural to write it this way
    module = pytest_splunk_addon.standard_lib.sample_generation.sample_event
    rule = "src"
    assert samp_eve.get_ipv4(rule) == "10.1.0.1"
    assert module.src_ipv4 == 1
    module.src_ipv4 = 270
    assert samp_eve.get_ipv4(rule) == "10.1.1.15"
    assert module.src_ipv4 == 271
    rule = "host"
    assert samp_eve.get_ipv4(rule) == "172.16.51.0"
    assert module.host_ipv4_octet_count == 0
    assert module.host_ipv4 == 51
    module.host_ipv4_octet_count = 260
    assert samp_eve.get_ipv4(rule) == "172.16.52.5"
    assert module.host_ipv4_octet_count == 5
    assert module.host_ipv4 == 52
    module.host_ipv4 = 101
    assert samp_eve.get_ipv4(rule) == "172.16.51.6"
    assert module.host_ipv4_octet_count == 6
    assert module.host_ipv4 == 51
    rule = "dvc"
    assert samp_eve.get_ipv4(rule) == "172.16.1.1"
    assert module.dvc_ipv4 == 1
    assert module.dvc_ipv4_octet_count == 1
    module.dvc_ipv4 = 80
    module.dvc_ipv4_octet_count = 300
    assert samp_eve.get_ipv4(rule) == "172.16.30.45"
    assert module.dvc_ipv4 == 81
    assert module.dvc_ipv4_octet_count == 301
    rule = "dest"
    assert samp_eve.get_ipv4(rule) == "10.100.0.1"
    assert module.dest_ipv4 == 1
    rule = "url"
    assert samp_eve.get_ipv4(rule) == "192.168.0.1"
    assert module.url_ip_count == 1
    rule = "else"
    assert samp_eve.get_ipv4(rule) == FAKE_IPV4


def test_get_ipv6(samp_eve):
    # that test might be divided into many smaller tests,
    # but feels natural to write it this way
    module = pytest_splunk_addon.standard_lib.sample_generation.sample_event
    rule = "src"
    assert samp_eve.get_ipv6(rule) == "fdee:1fe4:2b8c:3261:0000:0000:0000:0000"
    assert module.src_ipv6 == 1
    rule = "host"
    assert samp_eve.get_ipv6(rule) == "fdee:1fe4:2b8c:3264:0000:0000:0000:0000"
    assert module.host_ipv6 == 1
    rule = "dvc"
    assert samp_eve.get_ipv6(rule) == "fdee:1fe4:2b8c:3263:0000:0000:0000:0000"
    assert module.dvc_ipv6 == 1
    rule = "dest"
    assert samp_eve.get_ipv6(rule) == "fdee:1fe4:2b8c:3262:0000:0000:0000:0000"
    assert module.dest_ipv6 == 1
    rule = "else"
    assert samp_eve.get_ipv6(rule) == FAKE_IPV6


def test_get_token_count(samp_eve):
    assert samp_eve.get_token_count("d?ad") == 2


def test_replace_token(samp_eve):
    value_3 = "end_value"
    TokenValue = namedtuple("TokenValue", ["value"])
    token_values = [TokenValue(VALUE_1), TokenValue(VALUE_2)]
    samp_eve.replace_token("d?ad", token_values)
    assert samp_eve.event == f"Event_string {VALUE_1} {VALUE_2} dfd ddas Value_5."
    token_values = [TokenValue(value_3), TokenValue(value_3)]
    samp_eve.replace_token(r"Value_[1-9]?\.", token_values)
    assert samp_eve.event == f"Event_string {value_3} {VALUE_2} dfd ddas {value_3}"
    samp_eve.replace_token(value_3, VALUE_1)
    assert samp_eve.event == f"Event_string {VALUE_1} {VALUE_2} dfd ddas {VALUE_1}"


def test_register_field_value(samp_eve, monkeypatch):
    field_1 = "field1"
    field_2 = "field2"
    TokenValue = namedtuple("TokenValue", ["key"])
    assert samp_eve.time_values == []
    samp_eve.register_field_value("_time", [TokenValue(VALUE_1), TokenValue(VALUE_2)])
    assert samp_eve.time_values == [VALUE_1, VALUE_2]
    key_fields_mock = MagicMock()
    key_fields_mock.KEY_FIELDS = [field_1, field_2]
    monkeypatch.setattr(
        "pytest_splunk_addon.standard_lib.sample_generation.sample_event.key_fields",
        key_fields_mock,
    )
    samp_eve.register_field_value(field_1, TokenValue(VALUE_1))
    assert samp_eve.key_fields == {field_1: [VALUE_1]}
    samp_eve.register_field_value(field_2, [TokenValue(VALUE_1), TokenValue(VALUE_2)])
    assert samp_eve.key_fields == {field_1: [VALUE_1], field_2: [VALUE_1, VALUE_2]}


def test_get_key_fields(samp_eve):
    value = {"A": 1}
    assert samp_eve.get_key_fields() == {}
    samp_eve.key_fields = value
    assert samp_eve.get_key_fields() == value


def test_copy(samp_eve):
    key_fields_value = {1: 2}
    time_values = ["12", "13"]
    samp_eve.key_fields = key_fields_value
    samp_eve.time_values = time_values
    new_eve = pytest_splunk_addon.standard_lib.sample_generation.sample_event.SampleEvent.copy(
        samp_eve
    )
    assert new_eve.metadata == METADATA
    assert new_eve.key_fields == key_fields_value
    assert new_eve.time_values == time_values
    assert new_eve.event == EVENT_STRING
    assert new_eve.sample_name == SAMPLE_NAME
    assert new_eve.host_count == 0


def test_update_metadata(samp_eve):
    value = "value"
    header_without_prefix = f"{HOST}={value}_1 header={value}_2"
    event_body = "event body"
    event, metadata, key_fields = samp_eve.update_metadata(
        f"***SPLUNK*** {header_without_prefix}\n{event_body}",
        {HOST: f"{HOST}_{value}"},
        {},
    )
    assert event == event_body
    assert metadata == {HOST: f"{HOST}_{HOST}_{value}", "header": f"{value}_2"}
    assert key_fields == {HOST: [f"{HOST}_{HOST}_{value}"]}


def test_update_metadata_index_error(samp_eve):
    with pytest.raises(KeyError):
        samp_eve.update_metadata(f"***SPLUNK*** host=value_1\nsmth", {}, {})
