# -*- coding: utf-8 -*-
"""
Provides the helper methods to test addon_parser.Field object
"""
import logging
import json
from .field_test_adapter import FieldTestAdapater

class FieldTestHelper(object):
    """
    Provides the helper methods to test addon_parser.Field object

    Args:
        fields (list addon_parser.Field): The field to be tested 
    """
    logger = logging.getLogger("pytest-splunk-addon-tests")
    def __init__(self, search_util, fields, interval=10, retries=4):
        self.search_util = search_util
        self.fields = FieldTestAdapater.get_test_fields(fields)
        self.interval = interval
        self.retries = retries


    def test_field(self, base_search):
        """
        Generate a query for the list of fields and return the result 
        Format of the query is

            <condition> 
            | eval <validity> 
            | eval <expected_values>
            | eval <not negative_values>
            | stats count as event_count, count(field) as field_count,
                count(valid_field) as valid_field_count

        Args:
            base_search (str): Base search. Must be a search command.

        Yields:
            dict: with field, event_count, field_count, valid_field_count keys
        """
        self._make_search_query(base_search)
        self.logger.info(f"Executing the search query: {self.search}")
        self.result = self.search_util.getFieldValuesList(
                self.search, self.interval, self.retries
            )
        return self._parse_result(self.result)


    def _make_search_query(self, base_search):
        """
        Make the search query by using the list of fields 

        Args:
            base_search (str): The base search 
        """
        self.search = f"{base_search} {self._gen_condition()}"
        self.search_event = self.search
        for each_field in self.fields:
            self.search += each_field.gen_validity_query()
        
        self.search += " \n| stats count as event_count"
        for each_field in self.fields:
            self.search += each_field.get_stats_query()
        self.search += " by sourcetype"


    def _parse_result(self, result):
        """
        Convert the result into the following format

            {
                "str": {    // sourcetype
                    "event_count": int,
                    "fields": [{
                        "field": Field,
                        "field_count": int,
                        "valid_field_count": int
                        "invalid_values": list
                    }]
                }
            }
        """
        self.parsed_result = dict()
        for each_sourcetype_result in result:
            sourcetype = each_sourcetype_result["sourcetype"]
            self.parsed_result[sourcetype] = {
                "event_count": int(each_sourcetype_result.get("event_count"))
            }
            self.parsed_result[sourcetype]["fields"] = []
            for each_field in self.fields:
                each_obj = {
                    "field": each_field,
                    "field_count": int(each_sourcetype_result.get(
                        FieldTestAdapater.FIELD_COUNT.format(each_field.name))),
                }
                if each_field.gen_validity_query():
                    each_obj["valid_field_count"]= int(each_sourcetype_result.get(
                        FieldTestAdapater.VALID_FIELD_COUNT.format(each_field.name)))
                    each_obj["invalid_values"] = each_sourcetype_result.get(
                            FieldTestAdapater.INVALID_FIELD_VALUES.format(each_field.name), '[]').replace("'", "\"")
                self.parsed_result[sourcetype]["fields"].append(each_obj)
        return self.parsed_result


    def _gen_condition(self):
        return " AND ".join([each_field.condition for each_field in self.fields if each_field.condition])


    def format_exc_message(self):
        """
        Format the exception message to display 
        1) There's no field in the result 

            Sourcetype      Event Count
            ---------------------------
            splunkd         10
            scheduler       0
            ---------------------------
            Search = <search query>

        2) There are multiple fields in the result

            Sourcetype  Field  Total Count  Field Count  Invalid Field Count  Invalid Values
            --------------------------------------------------------------------------------
            splunkd     one    10           10           5                   'unknown'
            scheduler   two    20           20           7                   '-', 'invalid'
            --------------------------------------------------------------------------------
            Event count = 20
            Search = <search_query>

            Properties for the field :: One
            . . .
        """
        if not self.fields:
            exc_message = self.get_table_output(
                headers=["Sourcetype", "Event Count"],
                value_list=[
                    [sourcetype, value["event_count"]]
                    for sourcetype, value in self.parsed_result.items()
                ]
            )
        elif len(self.fields) >= 1:
            exc_message = self.get_table_output(
                headers=[
                    "Sourcetype", "Field", "Total Count", 
                    "Field Count", "Invalid Field Count", "Invalid Values"
                ],
                value_list=[
                    [
                        sourcetype,
                        each_field["field"].name,
                        value["event_count"],
                        each_field["field_count"],
                        each_field["field_count"] - each_field.get(
                            "valid_field_count", each_field["field_count"]
                        ),
                        (each_field["invalid_values"]
                        if each_field["invalid_values"] else "-")
                    ]
                    for sourcetype, value in self.parsed_result.items()
                    for each_field in value["fields"]
                ]
            )
        exc_message += (
            f"\n\nSearch = {self.search}"
        )
        for each_field in self.fields:
            exc_message += f"\n\nProperties for the field :: {each_field.get_properties()}"
        return exc_message


    @staticmethod
    def get_table_output(headers, value_list):
        table_output = ("{:<20}"*(len(headers))).format(
                     *headers
                )
        table_output += "\n" + "-"*20*len(headers)
        for each_value in value_list:
            table_output += (
                ("\n" + "{:<20}"*(len(headers))).format(
                *each_value
            ))
        table_output += "\n" + "-"*20*len(headers)

        return table_output

