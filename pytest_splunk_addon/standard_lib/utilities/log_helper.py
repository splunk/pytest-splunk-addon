#
# Copyright 2021 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


def get_table_output(headers, value_list):
    """
    Generate a table output of the following format::

        Header1 | Header2
        ---------------
        One     | Value1
        Two     | Value2
        --------------

    Args:
        headers (list): list of headers
        value_list (list of list): list of rows for the table
    """
    table_output = ""
    table_list = [headers] + value_list
    col_length = [
        max(map(lambda cell: len(str(cell)), col)) for col in zip(*table_list)
    ]
    format_str = " | ".join(["{{:<{}}}".format(i) for i in col_length])
    # Separating line
    table_list.insert(1, ["-" * i for i in col_length])
    for each_value in table_list:
        table_output += format_str.format(*each_value) + "\n"
    return table_output


def format_search_query_log(search_query):
    search_query_to_copy = search_query.replace("\n", "")
    search_query = search_query_to_copy.replace("|", "\n|")
    return f"\nSearch query:\n{search_query}\n\nSearch query to copy:\n{search_query_to_copy}\n"
