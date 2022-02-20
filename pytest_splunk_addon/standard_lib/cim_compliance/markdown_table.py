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
"""
Markdown table generator
"""
from pytest_splunk_addon.standard_lib.cim_compliance.base_table import BaseTable


class MarkdownTable(BaseTable):
    def __init__(self, table_title, header_list):
        self.table_title = self.__set_title(table_title)
        self.table_headers = self.__set_headers(header_list)
        self.row_str = ""
        self.table_description = ""
        self.table_note = ""

    def __set_title(self, title):
        """
        Adds Title string to the table

        Args:
            title(str): Title string.
        """
        return f"### {title}" if title else ""

    def __set_headers(self, header_list):
        """
        Sets the header column for the table.

        Args:
            header_list(list): Contains list of column headers.
        """
        header_str = "\n"
        helper_str = ""
        for each_column in header_list:
            header_str += f"| {each_column} "
            helper_str += "|:{}".format("-" * len(each_column))
        return f"{header_str} |\n {helper_str} |\n"

    def set_description(self, description):
        """
        Adds description string to the table

        Args:
            description(str): Description string.
        """
        self.table_description = f"\n {description} \n"

    def add_row(self, value_list):
        """
        Expects a list of row values to be added in the table

        Args:
            value_list(list): Contains list of row values
        """
        row_element = ""
        for each_value in value_list:
            row_element += f"| {each_value} "
        self.row_str += f"{row_element} |\n"

    def set_note(self, note_str):
        """
        It adds the note at the end of the table

        Args:
            note_str(str): Note string to be added.
        """
        self.table_note = f"\n*NOTE: {note_str} *\n "

    def return_table_str(self):
        """
        Generates the final table str
        """
        self.table_str = self.table_title
        self.table_str += self.table_description
        self.table_str += self.table_headers
        self.table_str += self.row_str
        self.table_str += self.table_note
        return self.table_str + "\n"
