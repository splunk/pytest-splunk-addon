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
        search_util (SearchUtil): the util class to search on the Splunk instance
        fields (list addon_parser.Field): The field to be tested 
        interval (int): at what interval each retry should be made
        retries (int): number of retries to make if no results found
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
            | eval <invalid_fields>
            | stats count as event_count, count(field) as field_count,
                count(valid_field) as valid_field_count,
                values(invalid_field) by sourcetype 

        Args:
            base_search (str): Base search. Must be a search command.

        Yields:
            dict: with sourcetype, field, event_count, field_count,
             valid_field_count, invalid_values keys
        """
        self._make_search_query(base_search)
        self.logger.info(f"Executing the search query: {self.search}")
        self.results = list(self.search_util.getFieldValuesList(
                self.search, self.interval, self.retries
            ))
        return self._parse_result(self.results)


    def _make_search_query(self, base_search):
        """
        Make the search query by using the list of fields 

            <base_search> <condition> 
            | eval valid_field=<validity> 
            | eval valid_field = if(field in <expected_values>)
            | eval valid_field = if(field not in <not negative_values>)
            | eval invalid_field = field if isnull(valid_field)
            | stats count as event_count, count(field) as field_count,
                count(valid_field) as valid_field_count,
                values(invalid_field) by sourcetype 

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


    def _parse_result(self, results):
        """
        Flatten the result into the following format

            [{
                "sourcetype": str
                "event_count": int,
                "field": Field,
                "field_count": int,
                "valid_field_count": int
                "invalid_values": list
            }]
        """
        self.parsed_result = list()
        for each_sourcetype_result in results:
            sourcetype = each_sourcetype_result["sourcetype"]
            event_count = int(each_sourcetype_result.get("event_count"))
            for each_field in self.fields:
                field_dict = {
                    "field": each_field,
                    "field_count": int(each_sourcetype_result.get(
                        FieldTestAdapater.FIELD_COUNT.format(each_field.name))),
                }
                if each_field.gen_validity_query():
                    field_dict["valid_field_count"]= int(each_sourcetype_result.get(
                        FieldTestAdapater.VALID_FIELD_COUNT.format(each_field.name)))
                    field_dict["invalid_values"] = each_sourcetype_result.get(
                            FieldTestAdapater.INVALID_FIELD_VALUES.format(each_field.name), '[]').replace("'", "\"")
                field_dict.update({
                    "sourcetype": sourcetype,
                    "event_count": event_count
                })
                self.parsed_result.append(field_dict)
            if not self.fields:
                self.parsed_result.append({
                        "sourcetype": sourcetype,
                        "event_count": event_count
                })
        return self.parsed_result


    def _gen_condition(self):
        return " AND ".join([
            each_field.condition for each_field in self.fields if each_field.condition
        ])


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
            splunkd     One    10           10           5                   'unknown'
            scheduler   Two    20           20           7                   '-', 'invalid'
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
                    [each_result["sourcetype"], each_result["event_count"]]
                    for each_result in self.parsed_result
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
                        each_result["sourcetype"],
                        each_result["field"].name,
                        each_result["event_count"],
                        each_result["field_count"],
                        each_result["field_count"] - each_result.get(
                            "valid_field_count", each_result["field_count"]
                        ),
                        (each_result["invalid_values"]
                        if each_result["invalid_values"] else "-")
                    ]
                    for each_result in self.parsed_result
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
        """
        Generate a table output of the following format 

            Header1 Header2
            ---------------
            One     Value1
            Two     Value2
            --------------
        """
        table_output = ("{:<20}"*(len(headers))).format(
                     *headers
                )
        table_output += "\n" + "-"*20*len(headers)
        for each_value in value_list:
            table_output += (
                ("\n" + "{:<20}"*(len(headers)-1) + "{}").format(
                *each_value
            ))
        table_output += "\n" + "-"*20*len(headers)

        return table_output

