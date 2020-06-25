import logging
import pytest

LOGGER = logging.getLogger("pytest-splunk-addon")


class IndexTimeTestGenerator(object):
    def generate_tests(self, tokenized_events):
        for tokenized_event in tokenized_events:
            sourcetype = tokenized_event.metadata.get(
                "sourcetype_to_search",
                tokenized_event.metadata.get("sourcetype", "*"),
            )
            source = tokenized_event.metadata.get(
                "source_after_transforms", tokenized_event.metadata.get("source", "*")
            )

            identifier_key = tokenized_event.metadata.get("identifier")
            if identifier_key:
                identifier_val = tokenized_event.key_fields.get(identifier_key)
                for identifier in identifier_val:
                    t = {
                        "identifier": identifier_key+"="+identifier,
                        "sourcetype": sourcetype,
                        "source": source,
                        "tokenized_event": tokenized_event,
                    }
                    yield pytest.param(
                        t,
                        id="{}_{}_{}:{}".format(
                            sourcetype, source, identifier_key, identifier
                        ),
                    )
            else:
                hosts = tokenized_event.metadata.get(
                    "host", tokenized_event.key_fields.get("host")
                )
                if isinstance(hosts, str):
                    hosts = [hosts]

                for host in hosts:
                    t = {
                        "host": host,
                        "sourcetype": sourcetype,
                        "source": source,
                        "tokenized_event": tokenized_event,
                    }
                    yield pytest.param(
                        t, id="{}_{}_{}".format(sourcetype, source, host),
                    )
                # else:
                #     yield pytest.param(
                #         {
                #             "query": "sourcetype={} source={} host={} | table {}".format(
                #                 sourcetype,
                #                 source,
                #                 hosts,
                #                 ",".join(tokenized_event.key_fields),
                #             ),
                #             "tokenized_event": tokenized_event,
                #         },
                #         id="{}_{}_{}".format(sourcetype, source, hosts),
                #     )
