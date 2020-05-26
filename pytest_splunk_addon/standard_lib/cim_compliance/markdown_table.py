"""
Markdown table generator
"""
from .base_table import BaseTable


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
        return "\n" + title + "\n" + "-" * len(title) + "\n" if title else ""

    def __set_headers(self, header_list):
        """
        Sets the header column for the table.

        Args:
            header_list(list): Contains list of column headers.
        """
        header_str = "\n"
        helper_str = ""
        for each_column in header_list:
            header_str += "| {} ".format(each_column)
            helper_str += "|:{}".format("-" * len(each_column))
        return header_str + "|\n" + helper_str + "|\n"

    def set_description(self, description):
        """
        Adds description string to the table

        Args: 
            description(str): Description string.
        """
        self.table_description += "\n**Description:** " + description + "\n"

    def add_row(self, value_list):
        """
        Expects a list of row values to be added in the table

        Args:
            value_list(list): Contains list of row values
        """
        row_element = ""
        for each_value in value_list:
            row_element += "| {} ".format(each_value)
        self.row_str += row_element + "|\n"

    def set_note(self, note_str):
        """
        It adds the note at the end of the table

        Args: 
            note_str(str): Note string to be added.
        """
        self.table_note = "\n*NOTE: " + note_str + "*\n"

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
