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
            "identifier") or splunk_indextime_key_fields.get("host"), (
                "Host or identifier fields cannot be determined from the config file.."
            )

        if splunk_indextime_key_fields.get("identifier"):
            extra_filter = splunk_indextime_key_fields.get("identifier")
        else:
            extra_filter = "host=" + splunk_indextime_key_fields.get(
                "host")
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
        value_list = []
        for each in fields_to_check.keys():
            List = []
            if not (all(x in fields_to_check.get(each) for x in list(set(result_fields.get(each))))):
                List.append(each)
                List.append(fields_to_check[each])
                List.append(list(set(result_fields.get(each))))
                value_list.append(List)
        result_str = FieldTestHelper.get_table_output(
            headers=["Key_field", "Expected_values", "Actual_values"],
            value_list=[
                [
                    each_result[0],
                    str(each_result[1]),
                    str(each_result[2]),
                ]
                for each_result in value_list
            ],     
        )       
        LOGGER.info(result_str)
        assert int(len(value_list)) == 0, (
            f"For this search query: '{search}'\n"
            f"some key fields have values which are not expected\n{result_str}"
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

        assert splunk_indextime_time.get(
            "identifier") or splunk_indextime_time.get("host"), (
                "Host or identifier fields cannot be determined from the config file.."
            )
        assert splunk_indextime_time["tokenized_event"].time_values, (
            "_time field cannot be determined from the config file."
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

            assert (
                (
                    float(event_time) - float(key_time[index])
                    ) < MAX_TIME_DIFFERENCE
            ), "Actual time {} :: Time in result {}".format(
                key_time[index], event_time
                )

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

        query = "search sourcetype={} (host=host_{}* OR host={}*)".format(
            splunk_indextime_line_breaker.get("sourcetype"),
            splunk_indextime_line_breaker.get('host'),
            splunk_indextime_line_breaker.get('host'),
        )
        record_property("Query", query)

        results = list(splunk_search_util.getFieldValuesList(query))
        count_of_results = len(results)

        if not count_of_results == expected_events_count:
            record_property("results", results)
            pp = pprint.PrettyPrinter(indent=4)
            result_str = pp.pformat(results)

        assert count_of_results == expected_events_count,  (
            f"Query result not as per expected event count.\n"
            f"Expected: {str(expected_events_count)} Found: {count_of_results}.\n"
            f"search={query}\n"
            f"found result={result_str}"
        )
