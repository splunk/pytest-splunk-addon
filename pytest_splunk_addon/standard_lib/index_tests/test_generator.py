import logging
import pytest

LOGGER = logging.getLogger("pytest-splunk-addon")


class IndexTimeTestGenerator(object):
    def generate_tests(self, sample_events):
        for sample in sample_events:
            sourcetype = sample.metadata.get(
                "sourcetype_after_transforms",
                sample.metadata.get("sourcetype", "*"),
            )
            source = sample.metadata.get(
                "source_after_transforms", sample.metadata.get("source", "*")
            )

            identifier_key = sample.metadata.get("identifier")
            if identifier_key:
                identifier_val = sample.key_fields.get(identifier_key)
                for identifier in identifier_val:
                    t = {
                        "identifier": identifier_key+"="+identifier,
                        "sourcetype": sourcetype,
                        "source": source,
                        "sample": sample,
                    }
                    yield pytest.param(
                        t,
                        id="{}_{}_{}:{}".format(
                            sourcetype, source, identifier_key, identifier
                        ),
                    )
            else:
                hosts = sample.metadata.get(
                    "host", sample.key_fields.get("host")
                )
                if isinstance(hosts, str):
                    hosts = [hosts]

                for host in hosts:
                    t = {
                        "host": host,
                        "sourcetype": sourcetype,
                        "source": source,
                        "sample": sample,
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
                #                 ",".join(sample.key_fields),
                #             ),
                #             "sample": sample,
                #         },
                #         id="{}_{}_{}".format(sourcetype, source, hosts),
                #     )
