# -*- coding: utf-8 -*-
"""
To enhance the test cases while verifying the field extractions.
"""
import json

from ..addon_parser import Field
from ..addon_parser import PropsParser

class FieldBank(object):
    """
    Supports field_bank: List of fields with patterns and expected
        values which should be tested for the Add-on.

    Steps to use:

    1. Create a json file with the list of fields. 
    
        Example::

            {
                "stanza_name": [    # Key should be stanza_name
                    {
                        "name": "action",
                        "condition": "| regex _raw=\\"success\\""
                        "validity": "action=if(action=\\"unknown\\", null(), action)"
                        "expected_values": ["success", "failure"]
                        "negative_values": ["", "-", "unknown"]
                    }
                ]
            }


        .. csv-table::
            :header: Parameter, Description

            condition, A filtering SPL command.
            validity, An EVAL statement. Filter out invalid value of a field 
            expected_fields, List of expected_fields 
            negative_fields, The list of values the field should not have

        supported stanza_type:

            1. source
            2. sourcetype

    2. Provide path of the json file with --field-bank=path parameter 
    """

    @classmethod
    def init_field_bank_tests(cls, field_bank_path):
        """
        Parse the field JSON file and return the list of fields

        Args:
            field_bank_path (str): Path of the field JSON file

        Yields:
            dict: details of the fields including stanza and stanza_type
        """
        if field_bank_path:
            with open(field_bank_path) as field_file:
                stanza_list = json.load(field_file)
            for each_stanza in stanza_list:
                if each_stanza.startswith("host::"):
                    continue
                field_list = Field.parse_fields(stanza_list[each_stanza]) 
                if each_stanza.startswith("source::"):
                    for each_source in PropsParser.get_list_of_sources(each_stanza):
                        yield {
                            "stanza": each_source,
                            "stanza_type": "source",
                            "classname": "field_bank",
                            "fields": field_list
                        }
                else:
                    yield { 
                        "stanza": each_stanza,
                        "stanza_type": "sourcetype",
                        "classname": "field_bank",
                        "fields": field_list
                    }
