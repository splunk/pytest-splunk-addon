import logging
import pytest
import copy

MAX_TIME_DIFFERENCE = 45


class IndexTimeTestTemplate(object):

    logger = logging.getLogger("pytest-splunk-addon-tests")
    

    @pytest.mark.first
    @pytest.mark.splunk_indextime
    def test_indextime_key_fields(
        self,
        splunk_search_util,
        splunk_ingest_data,
        splunk_indextime_key_fields,
        record_property,
        caplog,
    ):

        index_list = (
            "(index="
            + " OR index=".join(splunk_search_util.search_index.split(","))
            + ")"
        )

        if splunk_indextime_key_fields.get("identifier"):
            extra_filter = splunk_indextime_key_fields.get("identifier")
        else:
            extra_filter = "host=" + splunk_indextime_key_fields.get(
                "host", "*")
        fields_to_check = copy.deepcopy(
            splunk_indextime_key_fields["tokenized_event"].key_fields)

        query = "sourcetype={} {} | table {}".format(
            splunk_indextime_key_fields.get("sourcetype"),
            extra_filter,
            ",".join(fields_to_check),
        )

        search = "search {} {}".format(index_list, query)
        record_property("Query", search)

        results = splunk_search_util.getFieldValuesList(search)
        results = list(results)

        if not results:
            assert False, "No Events found for query "+search
        result_fields = dict()
        for result in results:
            for key, val in result.items():
                try:
                    result_fields[key].append(val)
                except KeyError:
                    result_fields[key] = [val]

        # This logic helps in comparing Results when the token is
        # only replaced once but the value is assigned to n events
        # Example syslog: all the headers are only tokenized once hence
        #   key_fields = {'host': ['dummy_host']}
        #   result_dict = {'host': ['dummy_host']*n}

        assert (
            {i: list(
                set(result_fields)) for i in result_fields} == {i: list(
                    set(fields_to_check)) for i in fields_to_check}
        )

    @pytest.mark.first
    @pytest.mark.splunk_indextime
    def test_indextime_time(
        self,
        splunk_search_util,
        splunk_ingest_data,
        splunk_indextime_time,
        record_property,
        caplog,
    ):
        index_list = (
            "(index="
            + " OR index=".join(splunk_search_util.search_index.split(","))
            + ")"
        )

        if splunk_indextime_time.get("identifier"):
            extra_filter = splunk_indextime_time.get("identifier")
        else:
            extra_filter = "host=" + splunk_indextime_time.get("host", "*")

        if splunk_indextime_time["tokenized_event"].time_values:
            extra_filter += " | eval e_time=_time"

        query = "sourcetype={} {} | table {}".format(
            splunk_indextime_time.get("sourcetype"),
            extra_filter,
            "e_time",
        )

        search = "search {} {}".format(index_list, query)

        record_property("Query", search)

        results = splunk_search_util.getFieldValuesList(search)
        results = list(results)
        result_fields = {key: [item[key] for item in results] for key in results[0].keys()}

        key_time = splunk_indextime_time["tokenized_event"].time_values
        record_property("time_values", key_time)
        for index, event_time in enumerate(result_fields["e_time"]):
            if splunk_indextime_time["tokenized_event"].metadata.get("timestamp_type") in ('event'):
                index_to_check = index
            else:
                index_to_check = 0
            assert (
                (
                    float(event_time) - float(key_time[index_to_check])
                    ) < MAX_TIME_DIFFERENCE
            ), "Actual time {} :: Time in result {}".format(
                key_time[index_to_check], event_time
                )

    # Testing line breaker
    @pytest.mark.first
    @pytest.mark.splunk_indextime
    def test_indextime_line_breaker(
        self,
        splunk_search_util,
        splunk_ingest_data,
        splunk_indextime_line_breaker,
        record_property,
        caplog,
    ):
        expected_events_count = int(splunk_indextime_line_breaker[
            "tokenized_event"
        ].metadata.get("expected_event_count", 1))

        query = "search sourcetype={} (host=host_{}* OR host={}*)".format(
            splunk_indextime_line_breaker.get("sourcetype"),
            splunk_indextime_line_breaker.get('host'),
            splunk_indextime_line_breaker.get('host'),
        )
        record_property("Query", query)

        assert splunk_search_util.checkQueryCount(
            query, expected_events_count, retries=0, interval=0
        ), ("We should get exactly " + str(expected_events_count) + " result")
