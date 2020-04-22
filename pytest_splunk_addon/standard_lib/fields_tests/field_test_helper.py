# -*- coding: utf-8 -*-
"""
Provides the helper methods to test addon_parser.Field object
"""
import logging
import json
from ..addon_parser import Field

class FieldTestAdapater(Field):
    """
    Field adapter to include the testing related properties on top of Field

    Properties:
        valid_field (str): New field generated which can only have the valid values
        validity_query (str): The query which extracts the valid_field out of the field

    """
    VALID_FIELD = "{}_valid"
    INVALID_FIELD = "{}_invalid"
    FIELD_COUNT = "{}_count"
    VALID_FIELD_COUNT = "{}_valid_count"
    INVALID_FIELD_VALUES = "{}_invalid_values"

    def __init__(self, field):
        self.__dict__ = field.__dict__.copy()
        self.valid_field = self.VALID_FIELD.format(field)
        self.invalid_field = self.INVALID_FIELD.format(field)
        self.validity_query = None

    @staticmethod
    def get_query_from_values(values):
        """
        List of values into SPL list
            Example: ["a", "b"] to '\"a\", \"b\"'

        Args:
            values (list): List of str values 
        
        Returns:
            str: SPL query list
        """
        query = '\\", \\"'.join(values)
        return f'\\"{query}\\"'

    def gen_validity_query(self):
        if not self.validity_query is None:
            return self.validity_query
        else:
            self.validity_query = ""
            
            self.validity_query += ("\n"
                f"| eval {self.valid_field}={self.validity}")
            if self.expected_values:
                self.validity_query += ("\n"
                     "| eval {valid_field}=if(searchmatch(\"{valid_field} IN ({values})\"), {valid_field}, null())".format(
                         valid_field=self.valid_field,
                         values=self.get_query_from_values(self.expected_values)
                     )
                )
            if self.negative_values:
                self.validity_query += ("\n"
                     "| eval {valid_field}=if(searchmatch(\"{valid_field} IN ({values})\"), null(), {valid_field})".format(
                         valid_field=self.valid_field,
                         values=self.get_query_from_values(self.negative_values)
                     )
                )
            self.validity_query += ("\n"
                f"| eval {self.invalid_field}=if(isnull({self.valid_field}), {self.name}, null())")
            return self.validity_query

    def get_stats_query(self):
        query = f", count({self.name}) as {self.FIELD_COUNT.format(self.name)}"
        if self.gen_validity_query():
            query += f", count({self.valid_field}) as {self.VALID_FIELD_COUNT.format(self.name)}"
            query += f", values({self.invalid_field}) as {self.INVALID_FIELD_VALUES.format(self.name)}"
        return query

    @classmethod
    def get_test_fields(cls, fields):
        return [cls(each_field) for each_field in fields]
             

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

    def _make_search_query(self, base_search):
        """
        Make the search query by using the list of fields 
        """
        self.search = f"{base_search} {self._gen_condition()}"
        self.search_event = self.search
        for each_field in self.fields:
            self.search += each_field.gen_validity_query()
        
        self.search += " \n| stats count as event_count"
        for each_field in self.fields:
            self.search += each_field.get_stats_query()


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
        self.result = self.search_util.getFieldValuesDict(self.search)
        return self._parse_result(self.result)

    def get_exc_message(self):
        """
        1) There's no field in the result 

            Event Count = 100 
            Search = <search query>

        2) There's only 1 field in the result 

            Event Count = 100
            Invalid Field Values = ["-", "unknown"]

            Field Count = 100
            Valid Field Count = 50
            Search = <search query>

            Properties for the field :: One 
            . . . 

        3) There are multiple fields in the result

            Fields    Field Count     Valid Field Count 
            ---------------------------------
            one         10             10
            two         20             20
            ---------------------------------
            Event count = 20 
            Search = <search_query>
        """
        if not "fields" in self.parsed_result:
            return (
                f"Event Count = {self.parsed_result.get('event_count')}"
                f"\nSearch = {self.search}"
            )
        if len(self.parsed_result["fields"]) == 1:
            parsed_field_stats = self.parsed_result['fields'][0]
            sep = "\', \'"
            return (
                f"Field = {parsed_field_stats['field']}"
                f"\nInvalid Field Values = \'{sep.join(parsed_field_stats['invalid_values'][:10])}\'"
                f"\nInvalid Field Count = {parsed_field_stats['field_count'] - parsed_field_stats['valid_field_count']}"
                f"\n\nEvent Count = {self.result.get('event_count')}"
                f"\nField Count = {parsed_field_stats['field_count']}"
                f"\n\nSearch = {self.search}"
                f"\n\nProperties for the field :: {parsed_field_stats['field'].get_properties()}"
            )
        else:
            exc_message = self.get_table_output(
                headers=["Field", "Field Count", "Invalid Field Count", "- Values"],
                value_list=[
                    [
                        each_field["field"].name,
                        each_field["field_count"],
                        each_field["field_count"] - each_field.get(
                            "valid_field_count", each_field["field_count"]
                        ),
                        ("'{}'".format("', '".join(each_field["invalid_values"][:10])) 
                        if each_field["invalid_values"] else "-")
                    ]
                    for each_field in self.parsed_result["fields"]
                ]
            )
            exc_message += (
                f"\nEvent Count = {self.parsed_result.get('event_count')}"
                f"\n\nSearch = {self.search}"
            )
            return exc_message

    @staticmethod
    def get_table_output(headers, value_list):
        table_output = ("{:<20}"*(len(headers))).format(
                     *headers
                )
        table_output += "\n" + "-"*100
        for each_value in value_list:
            table_output += (
                ("\n" + "{:<20}"*(len(headers))).format(
                *each_value
            ))
        table_output += "\n" + "-"*100

        return table_output

    def _parse_result(self, result):
        """
        Convert the result into the following format

            {
                "event_count": int,
                "fields": {
                    "field": Field,
                    "field_count": int,
                    "valid_field_count": int
                    "invalid_values": list
                }
            }
        """
        self.parsed_result = {
            "event_count": int(result.get("event_count"))
        }
        if not self.fields:
            return self.parsed_result
        self.parsed_result["fields"] = []
        for each_field in self.fields:
            each_obj = {
                "field": each_field,
                "field_count": int(result.get(FieldTestAdapater.FIELD_COUNT.format(each_field.name))),
            }
            if each_field.gen_validity_query():
                each_obj["valid_field_count"]= int(self.result.get(FieldTestAdapater.VALID_FIELD_COUNT.format(each_field.name)))
                each_obj["invalid_values"] = json.loads(
                    self.result.get(FieldTestAdapater.INVALID_FIELD_VALUES.format(each_field.name), '[]').replace("'", "\"")
                )
            self.parsed_result["fields"].append(each_obj)
        return self.parsed_result

    def _gen_condition(self):
        return " AND ".join([each_field.condition for each_field in self.fields if each_field.condition])
