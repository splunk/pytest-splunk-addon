import logging
import pytest

from ..sample_generation import SampleXdistGenerator
from ..sample_generation.rule import raise_warning

LOGGER = logging.getLogger("pytest-splunk-addon")


class IndexTimeTestGenerator(object):
    def generate_tests(self, app_path, config_path, test_type):
        sample_generator = SampleXdistGenerator(app_path, config_path)
        store_sample = sample_generator.get_samples()
        tokenized_events = store_sample.get("tokenized_events")

        if not store_sample.get("conf_name") == "psa-data-gen":
            return " Index Time tests cannot be executed using eventgen.conf,\
                 pytest-splunk-addon-data.conf is required."

        if test_type == "line_breaker":
            yield from self.generate_line_breaker_tests(tokenized_events)

        else:

            for tokenized_event in tokenized_events:

                identifier_key = tokenized_event.metadata.get("identifier")

                hosts = self.get_hosts(tokenized_event)

                # Generate test params only if key_fields
                if test_type == "key_fields" and tokenized_event.key_fields:

                    yield from self.generate_params(
                        tokenized_event, identifier_key, hosts
                    )

                # Generate test only if time_values
                elif test_type == "_time" and tokenized_event.metadata.get('timestamp_type') == 'event':
                    yield from self.generate_params(
                        tokenized_event, identifier_key, hosts
                    )

    def generate_line_breaker_tests(self, tokenized_events):
        unique_stanzas = set()
        sourcetype = 0
        source = 1
        expected_event_count = 2
        sample_name = 3

        for each_event in tokenized_events:
            unique_stanzas.add(
                (
                    self.get_sourcetype(each_event),
                    self.get_source(each_event),
                    each_event.metadata.get("expected_event_count", 1),
                    each_event.sample_name,
                )
            )

        for each_stanza in unique_stanzas:
            yield pytest.param(
                {
                    "host": each_stanza[sample_name],
                    "sourcetype": each_stanza[sourcetype],
                    "source": each_stanza[source],
                    "expected_event_count": each_stanza[expected_event_count],
                },
                id="{}::{}".format(
                    each_stanza[sourcetype], each_stanza[sample_name]
                ),
            )

    def get_hosts(self, tokenized_event):
        if tokenized_event.metadata.get("host_type") in ("plugin", None):
            hosts = tokenized_event.metadata.get("host")
        elif tokenized_event.metadata.get("host_type") == "event":
            hosts = tokenized_event.key_fields.get("host")
        else:
            hosts = None
            LOGGER.error(
                "Invalid 'host_type' for stanza {}".format(
                    tokenized_event.sample_name
                )
            )
        if isinstance(hosts, str):
            hosts = [hosts]

        return hosts

    def get_sourcetype(self, sample_event):
        return sample_event.metadata.get(
            "sourcetype_to_search",
            sample_event.metadata.get("sourcetype", "*"),
        )

    def get_source(self, sample_event):
        return sample_event.metadata.get(
            "source_to_search", sample_event.metadata.get("source", "*")
        )

    def generate_params(self, tokenized_event, identifier_key, hosts):
        if identifier_key:
            yield from self.generate_identifier_params(
                tokenized_event, identifier_key
            )
        else:
            yield from self.generate_hosts_params(tokenized_event, hosts)

    def generate_identifier_params(self, tokenized_event, identifier_key):
        identifier_val = tokenized_event.key_fields.get(identifier_key)
        for identifier in identifier_val:
            yield pytest.param(
                {
                    "identifier": identifier_key + "=" + identifier,
                    "sourcetype": self.get_sourcetype(tokenized_event),
                    "source": self.get_source(tokenized_event),
                    "tokenized_event": tokenized_event,
                },
                id="{}::{}:{}".format(
                    self.get_sourcetype(tokenized_event),
                    identifier_key,
                    identifier,
                ),
            )

    def generate_hosts_params(self, tokenized_event, hosts):
        id_host = hosts[0]+"_to_"+hosts[-1] if hosts else tokenized_event.sample_name
        yield pytest.param(
            {
                "hosts": hosts,
                "sourcetype": self.get_sourcetype(tokenized_event),
                "source": self.get_source(tokenized_event),
                "tokenized_event": tokenized_event,
            },
            id="{}::{}".format(
                self.get_sourcetype(tokenized_event),
                id_host
            ),
        )
