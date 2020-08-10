"""
Includes the test scenarios to check the index time properties of an Add-on.
"""
import logging
import pytest
import copy

from math import ceil
from ..cim_tests import FieldTestHelper

MAX_TIME_DIFFERENCE = 45
LOGGER = logging.getLogger("pytest-splunk-addon")


class IndexTimeTestTemplate(object):
    """
    Test templates to test the index time fields of an App
    """

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
        """
        This test case checks that a key_field has the expected values.
        The key fields are as follows:

            * src
            * src_port
            * dest
            * dest_port
            * dvc
            * host
            * user
            * url

        Args:
            splunk_search_util (SearchUtil): Object that helps to search on Splunk.
            splunk_ingest_data (fixture): To ingest data into splunk.
            splunk_indextime_key_fields (fixture): Test for key fields
            record_property (fixture): Document facts of test cases.
            caplog (fixture): fixture to capture logs.
        """

        index_list = (
            "(index="
            + " OR index=".join(splunk_search_util.search_index.split(","))
            + ")"
        )

        assert splunk_indextime_key_fields.get(
            "identifier"
        ) or splunk_indextime_key_fields.get(
            "hosts"
        ), "Host or identifier fields cannot be determined from the config file.."

        if splunk_indextime_key_fields.get("identifier"):
            extra_filter = splunk_indextime_key_fields.get("identifier")
        else:
            extra_filter = "host IN (\""+"\",\"".join(set(splunk_indextime_key_fields.get("hosts")))+"\")"
        fields_to_check = copy.deepcopy(
            splunk_indextime_key_fields["tokenized_event"].key_fields
        )

        query = "sourcetype={} {} | table {}".format(
            splunk_indextime_key_fields.get("sourcetype"),
            extra_filter,
            ",".join(fields_to_check),
        )

        search = "search {} {}".format(index_list, query)
        record_property("Query", search)

        results = splunk_search_util.getFieldValuesList(
            search,
            interval=splunk_search_util.search_interval,
            retries=splunk_search_util.search_retry,
        )
        results = list(results)

        if not results:
            assert False, "No Events found for query " + search
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
        result_fields = {key: set(value) for key, value in result_fields.items()}
        fields_to_check = {key: set(value) for key, value in fields_to_check.items()}
        if not result_fields == fields_to_check:
            value_list, missing_keys = [], []
            for each_field in fields_to_check.keys():
                if each_field in result_fields.keys():
                    if not fields_to_check.get(each_field) == result_fields.get(each_field):
                        value_list.append([each_field, fields_to_check[each_field], result_fields.get(each_field)])
                else:
                    missing_keys.append([each_field, fields_to_check[each_field]])
            final_str = ''
            if value_list:
                result_str = FieldTestHelper.get_table_output(
                    headers=["Key_field", "Expected_values", "Actual_values"],
                    value_list=[
                        [
                            each_value[0],
                            str(each_value[1]),
                            str(each_value[2]),
                        ]
                        for each_value in value_list
                    ],
                )
                final_str += f"Some values for the following key fields are missing\n\n{result_str}"

            if missing_keys:    
                missing_keys_result_str = FieldTestHelper.get_table_output(
                    headers=["Key_field", "Expected_values"],
                    value_list=[
                        [
                            each_key[0],
                            str(each_key[1]),
                        ]
                        for each_key in missing_keys
                    ],     
                )
                final_str += f"\n\nSome key fields are not found in search results\n\n{missing_keys_result_str}"
            LOGGER.info(final_str)

            assert int(len(value_list)) == 0 and int(len(missing_keys)) == 0, (
                f"For this search query: '{search}'\n{final_str}"
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
        """
        This test case checks that _time value in the events has the expected values.

        Args:
            splunk_search_util (SearchUtil): Object that helps to search on Splunk.
            splunk_ingest_data (fixture): To ingest data into splunk.
            splunk_indextime_time (fixture): Test for _time field
            record_property (fixture): Document facts of test cases.
            caplog (fixture): fixture to capture logs.
        """
        index_list = (
            "(index="
            + " OR index=".join(splunk_search_util.search_index.split(","))
            + ")"
        )

        assert splunk_indextime_time.get(
            "identifier"
        ) or splunk_indextime_time.get(
            "hosts"
        ), "Host or identifier fields cannot be determined from the config file.."
        assert splunk_indextime_time[
            "tokenized_event"
        ].time_values, (
            "_time field cannot be determined from the config file."
        )

        if splunk_indextime_time.get("identifier"):
            extra_filter = splunk_indextime_time.get("identifier")
        else:
            extra_filter = "host IN (\""+"\",\"".join(set(splunk_indextime_time.get("hosts")))+"\")"

        if splunk_indextime_time["tokenized_event"].time_values:
            extra_filter += " | eval e_time=_time"

        query = "sourcetype={} {} | table {}".format(
            splunk_indextime_time.get("sourcetype"), extra_filter, "e_time",
        )

        search = "search {} {}".format(index_list, query)

        record_property("Query", search)

        results = splunk_search_util.getFieldValuesList(
            search,
            interval=splunk_search_util.search_interval,
            retries=splunk_search_util.search_retry,
        )
        results = list(results)
        if not results:
            assert False, "No Events found for query: " + search
        result_fields = {
            key: [ceil(float(item[key])) for item in results]
            for key in results[0].keys()
        }

        key_time = [ceil(t) for t in splunk_indextime_time[
            "tokenized_event"].time_values]
        result_fields["e_time"].sort()
        key_time.sort()

        record_property("time_values", key_time)
        record_property("result_time", result_fields)

        assert (
            result_fields["e_time"] == key_time
        ), "Actual time {} :: Time in result {}".format(
            key_time, result_fields["e_time"]
        )


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
        """
        This test case checks that number of events is as expected.

        Args:
            splunk_search_util (SearchUtil): Object that helps to search on Splunk.
            splunk_ingest_data (fixture): To ingest data into splunk.
            splunk_indextime_line_breaker (fixture): Test for event count
            record_property (fixture): Document facts of test cases.
            caplog (fixture): fixture to capture logs.
        """
        expected_events_count = int(
            splunk_indextime_line_breaker["expected_event_count"]
        )
        index_list = (
            "(index="
            + " OR index=".join(splunk_search_util.search_index.split(","))
            + ")"
        )
        host = "(\""+"\",\"".join(splunk_indextime_line_breaker.get("host"))+"\")"
        query = "search {} sourcetype={} host IN {} | stats count".format(
            index_list,
            splunk_indextime_line_breaker.get("sourcetype"),
            host
        )
        record_property("Query", query)

        results = list(
            splunk_search_util.getFieldValuesList(
                query,
                interval=splunk_search_util.search_interval,
                retries=splunk_search_util.search_retry,
            )
        )
        count_from_results = int(results[0].get("count"))

        assert (
            count_from_results == expected_events_count
        ), f"Query: {query} \nExpected count: {expected_events_count} Actual Count: {count_from_results}"
