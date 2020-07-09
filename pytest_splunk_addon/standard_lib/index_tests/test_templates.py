import logging
import pytest
import copy
import pprint
from ..cim_tests import FieldTestHelper

MAX_TIME_DIFFERENCE = 45

LOGGER = logging.getLogger("pytest-splunk-addon")


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

        assert splunk_indextime_key_fields.get(
            "identifier") or splunk_indextime_key_fields.get("hosts"), (
                "Host or identifier fields cannot be determined from the config file.."
            )

        if splunk_indextime_key_fields.get("identifier"):
            extra_filter = splunk_indextime_key_fields.get("identifier")
        else:
            extra_filter = "host=" + " OR host=".join(
                splunk_indextime_key_fields.get("hosts"))
        fields_to_check = copy.deepcopy(
            splunk_indextime_key_fields["tokenized_event"].key_fields)

        query = "sourcetype={} {} | table {}".format(
            splunk_indextime_key_fields.get("sourcetype"),
            extra_filter,
            ",".join(fields_to_check),
        )

        search = "search {} {}".format(index_list, query)
        record_property("Query", search)

        results = splunk_search_util.getFieldValuesList(search, interval=0, retries=0)
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
        result_dict = {key: set(value) for key, value in result_fields.items()}
        dict_to_check = {key: set(value) for key, value in fields_to_check.items()}
        record_property('Dict_to_check', dict_to_check)
        record_property('Result', result_dict)

        assert (result_dict == dict_to_check)


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

        assert splunk_indextime_time.get(
            "identifier") or splunk_indextime_time.get("hosts"), (
                "Host or identifier fields cannot be determined from the config file.."
            )
        assert splunk_indextime_time["tokenized_event"].time_values, (
            "_time field cannot be determined from the config file."
        )

        if splunk_indextime_time.get("identifier"):
            extra_filter = splunk_indextime_time.get("identifier")
        else:
            extra_filter = "(host=" + " OR host=".join(
                splunk_indextime_time.get("hosts"))+")"

        if splunk_indextime_time["tokenized_event"].time_values:
            extra_filter += " | eval e_time=_time"

        query = "sourcetype={} {} | table {}".format(
            splunk_indextime_time.get("sourcetype"),
            extra_filter,
            "e_time",
        )

        search = "search {} {}".format(index_list, query)

        record_property("Query", search)

        results = splunk_search_util.getFieldValuesList(search, interval=0, retries=0)
        results = list(results)

        result_fields = {key: [float(item[key]) for item in results] for key in results[0].keys()}

        key_time = splunk_indextime_time["tokenized_event"].time_values
        result_fields["e_time"].sort()
        key_time.sort()

        record_property("time_values", key_time)
        record_property("result_time", result_fields)

        assert result_fields["e_time"] == key_time, (
            "Actual time {} :: Time in result {}".format(
                key_time, result_fields["e_time"]))

    # # Testing line breaker
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
        expected_events_count = int(
            splunk_indextime_line_breaker["expected_event_count"]
            )

        query = "search sourcetype={} (host=host_{}* OR host={}*) | stats count".format(
            splunk_indextime_line_breaker.get("sourcetype"),
            splunk_indextime_line_breaker.get('host'),
            splunk_indextime_line_breaker.get('host'),
        )
        record_property("Query", query)

        results = list(splunk_search_util.getFieldValuesList(query, interval=0, retries=0))
        count_from_results = int(results[0].get('count'))

        assert count_from_results == expected_events_count, (
            f"Expected count: {expected_events_count} Count obtained: {count_from_results}"
        )