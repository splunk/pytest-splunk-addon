import logging
import pytest

from ..sample_generation import SampleGenerator

LOGGER = logging.getLogger("pytest-splunk-addon")


class IndexTimeTestGenerator(object):
    def generate_tests(self, app_path, config_path, test_type):
        sample_generator = SampleGenerator(
            app_path, config_path, bulk_event_ingestion=False)
        tokenized_events = list(sample_generator.get_samples())

        if not SampleGenerator.splunk_test_type == "splunk_indextime":
            return " Index Time tests cannot be executed using eventgen.conf,\
                 pytest-splunk-addon-data-generator.conf is required."

        for tokenized_event in tokenized_events:
            self.sourcetype = tokenized_event.metadata.get(
                "sourcetype_to_search",
                tokenized_event.metadata.get("sourcetype", "*"),
            )
            self.source = tokenized_event.metadata.get(
                "source_to_search", tokenized_event.metadata.get("source", "*")
            )

            identifier_key = tokenized_event.metadata.get("identifier")

            if tokenized_event.metadata.get("host_type") in ('plugin', None):
                hosts = tokenized_event.metadata.get("host")
            elif tokenized_event.metadata.get("host_type") == "event":
                hosts = tokenized_event.key_fields.get("host")
            else:
                LOGGER.error("Invalid 'host_type' for stanza {}".format(
                    tokenized_event.sample_name)
                             )
            if isinstance(hosts, str):
                hosts = [hosts]

            # Generate test params only if key_fields
            if test_type == "key_fields" and tokenized_event.key_fields:

                yield from self.generate_params(
                    tokenized_event, identifier_key, hosts
                    )

            # Generate test only if time_values
            elif test_type == "_time" and tokenized_event.time_values:
                yield from self.generate_params(
                    tokenized_event, identifier_key, hosts
                    )

            # Line Breaker test param
            elif test_type == "line_breaker":
                yield pytest.param(
                            {
                                "host": tokenized_event.sample_name,
                                "sourcetype": self.sourcetype,
                                "source": self.source,
                                "tokenized_event": tokenized_event,
                            },
                            id="{}::{}".format(
                                self.sourcetype, tokenized_event.sample_name
                                ),
                        )

    def generate_params(self, tokenized_event, identifier_key, hosts):
        if identifier_key:
            yield from self.generate_identifier_params(
                tokenized_event,
                identifier_key
                )
        else:
            yield from self.generate_hosts_params(
                tokenized_event,
                hosts
            )

    def generate_identifier_params(self, tokenized_event, identifier_key):
        identifier_val = tokenized_event.key_fields.get(
                        identifier_key
                        )
        for identifier in identifier_val:
            yield pytest.param(
                {
                    "identifier": identifier_key+"="+identifier,
                    "sourcetype": self.sourcetype,
                    "source": self.source,
                    "tokenized_event": tokenized_event,
                },
                id="{}::{}:{}".format(
                    self.sourcetype, identifier_key, identifier
                ),
            )

    def generate_hosts_params(self, tokenized_event, hosts):
        for host in hosts:
            yield pytest.param(
                {
                    "host": host,
                    "sourcetype": self.sourcetype,
                    "source": self.source,
                    "tokenized_event": tokenized_event,
                },
                id="{}::{}".format(self.sourcetype, host),
            )
