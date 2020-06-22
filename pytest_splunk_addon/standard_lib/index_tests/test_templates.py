import logging
import pytest


class IndexTimeTestTemplate(object):

    logger = logging.getLogger("pytest-splunk-addon-tests")

    @pytest.mark.splunk_indextime
    def test_index_time_extractions(
        self, splunk_search_util, splunk_ingest_data, splunk_indextime_fields, record_property, caplog
    ):
        record_property("what_we_ingestd", splunk_indextime_fields["sample"].event)
        record_property(
            "Key_fields_we_are_looking_for",
            str(splunk_indextime_fields["sample"].key_fields),
        )
        index_list = (
            "(index="
            + " OR index=".join(splunk_search_util.search_index.split(","))
            + ")"
        )

        if splunk_indextime_fields.get("identifier"):
            extra_filter = splunk_indextime_fields.get("identifier")
        else:
            extra_filter = "host=" + splunk_indextime_fields.get("host")

        if splunk_indextime_fields["sample"].key_fields.get("_time"):
            # splunk_indextime_fields["query"] += ",_time"
            extra_filter += " | eval e_time=_time"
            splunk_indextime_fields["sample"].key_fields[
                "e_time"
            ] = splunk_indextime_fields["sample"].key_fields.pop("_time")

        query = "sourcetype={} source={} {} | table {}".format(
            splunk_indextime_fields.get("sourcetype"),
            splunk_indextime_fields.get("source"),
            extra_filter,
            ",".join(splunk_indextime_fields["sample"].key_fields),
        )

        search = "search {} {}".format(index_list, query)

        record_property("search", search)

        results = splunk_search_util.getFieldValuesList(search)
        results = list(results)

        record_property("we_got_this_many_results", str(len(results)))

        for result in results:
            for key in result:

                record_property("what_we_got_for_" + key, result[key])

                msg = "looking for {}={} Found {}={}".format(
                    key,
                    splunk_indextime_fields["sample"].key_fields[key],
                    key,
                    result[key],
                )

                assert (
                    result[key]
                    in splunk_indextime_fields["sample"].key_fields[key]
                ), msg

        # # Testing line breaker
        # expected_events_count = splunk_indextime_fields["sample"].metadata.get(
        #     "expected_event_count", 1
        # )

        # query1 = "search sourcetype={} source={} host={}".format(
        #     splunk_indextime_fields.get("sourcetype"),
        #     splunk_indextime_fields.get("source"),
        #     splunk_indextime_fields["sample"].sample_name + "_*",
        # )
        # assert splunk_search_util.checkQueryCount(
        #     query1, expected_events_count
        # ), ("We should get exactly " + str(expected_events_count) + " result")
        # # implementation here
        # assert True
