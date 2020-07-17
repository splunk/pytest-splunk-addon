import logging
import pytest

from ..sample_generation import SampleXdistGenerator
from ..sample_generation.rule import raise_warning

LOGGER = logging.getLogger("pytest-splunk-addon")


class IndexTimeTestGenerator(object):
    """
    Generates test cases to test the index time extraction of an Add-on.

    * Provides the pytest parameters to the test templates.
    * Supports key_fields: List of fields which should be tested 
      for the Add-on.
    """

    def generate_tests(self, app_path, config_path, test_type):
        """
        Generates the test cases based on test_type 

        Args:
            app_path (str): Path of the app package
            config_path (str): Path of package which contains pytest-splunk-addon-data.conf
            test_type (str): Type of test case

        Yields:
            pytest.params for the test templates 

        """
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
        """
        Generates test case for testing line breaker

        Args:
            tokenized_events (list): List of tokenized events

        Yields:
            pytest.params for the test templates 
        """
        unique_stanzas = set()
        sourcetype = 0
        source = 1
        expected_event_count = 2
        sample_name = 3
        sample_count = 1
        expected_count = 1

        for each_event in tokenized_events:
            try:
                sample_count = int(each_event.metadata.get("sample_count", 1))
                expected_count = int(each_event.metadata.get("expected_event_count", 1))
            except ValueError as e:
                raise_warning("Invalid value  {}".format(e)) 

            if each_event.metadata.get("input_type") not in ["modinput", "windows_input"]:
                expected_count = expected_count*sample_count    

            unique_stanzas.add(
                (
                    self.get_sourcetype(each_event),
                    self.get_source(each_event),
                    expected_count,
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
        """
        Returns value of host for event

        Args:
            tokenized_event (SampleEvent): Instance containing event info

        Returns:
            Value of host for event
        """
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
        """
        Returns value of sourcetype for event

        Args:
            sample_event (SampleEvent): Instance containing event info

        Returns:
            Value of sourcetype for event
        """
        return sample_event.metadata.get(
            "sourcetype_to_search",
            sample_event.metadata.get("sourcetype", "*"),
        )

    def get_source(self, sample_event):
        """
        Returns value of source for event

        Args:
            sample_event (SampleEvent): Instance containing event info

        Returns:
            Value of source for event
        """
        return sample_event.metadata.get(
            "source_to_search", sample_event.metadata.get("source", "*")
        )

    def generate_params(self, tokenized_event, identifier_key, hosts):
        """
        Generates test case based on parameters

        Args:
            tokenized_event (SampleEvent): Instance containing event info
            identifier_key (str): Identifier Key if mention in conf file
            hosts (list): List of host for event

        Yields:
            pytest.params for the test templates
        """
        if identifier_key:
            yield from self.generate_identifier_params(
                tokenized_event, identifier_key
            )
        else:
            yield from self.generate_hosts_params(tokenized_event, hosts)

    def generate_identifier_params(self, tokenized_event, identifier_key):
        """
        Generates test case based on Identifier key mentioned in conf file

        Args:
            tokenized_event (SampleEvent): Instance containing event info
            identifier_key (str): Identifier Key if mention in conf file

        Yields:
            pytest.params for the test templates
        """
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
        """
        Generates test case based on host value of the event

        Args:
            tokenized_event (SampleEvent): Instance containing event info
            hosts (list): List of hosts for event

        Yields:
            pytest.params for the test templates
        """
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
