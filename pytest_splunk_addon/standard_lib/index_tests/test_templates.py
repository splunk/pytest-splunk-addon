import logging
import pytest


class IndexTimeTestTemplate(object):

    logger = logging.getLogger("pytest-splunk-addon-tests")

    @pytest.mark.splunk_indextime
    def test_index_time_extractions(
        self, splunk_search_util, splunk_ingest_data, record_property, caplog
    ):
        record_property("what_we_ingestd", splunk_ingest_data["sample"].event)

        index_list = (
            "(index="
            + " OR index=".join(splunk_search_util.search_index.split(","))
            + ")"
        )

        if splunk_ingest_data.get("identifier"):
            extra_filter = splunk_ingest_data.get("identifier")
        else:
            extra_filter = splunk_ingest_data.get("host")

        if splunk_ingest_data["sample"].key_fields.get("_time"):
            # splunk_ingest_data["query"] += ",_time"
            extra_filter += " | eval e_time=_time"
            splunk_ingest_data["sample"].key_fields[
                "e_time"
            ] = splunk_ingest_data["sample"].key_fields.pop("_time")

        query = "sourcetype={} source={} {} | table {}".format(
            splunk_ingest_data.get("sourcetype"),
            splunk_ingest_data.get("source"),
            extra_filter,
            ",".join(splunk_ingest_data["sample"].key_fields),
        )

        search = "search {} {}".format(index_list, query)

        record_property("search", search)

        results = splunk_search_util.getFieldValuesList(search)
        results = list(results)

        record_property("we_got_this_many_results", str(len(results)))

        # n = splunk_ingest_data['sample'].metadata.get('expected_event_count', 1)

        # assert len(results) == n, "We should get exactly "+str(n)+" result"

        for result in results:
            for key in result:

                record_property("what_we_got_for_" + key, result[key])

                msg = "looking for {}={} Found {}={}".format(
                    key,
                    splunk_ingest_data["sample"].key_fields[key],
                    key,
                    result[key],
                )

                assert (
                    result[key] in splunk_ingest_data["sample"].key_fields[key]
                ), msg
                
        # Testing line breaker

        # implementation here
        assert True
