"""
Markdown generator
"""
from .base_report import CIMReport


class MarkDownReport(CIMReport):
    def __init__(self):
        self.markdown_str = ""

    def set_title(self, title_string):
        self.title_str = "#" + title_string + "\n"

    def add_section_title(self, section_title):
        self.markdown_str += "## " + section_title + "\n"

    def add_section_note(self, section_note):
        self.markdown_str += "## Note: " + section_note + "\n"

    def add_table(self, table_string):
        self.markdown_str += table_string

    def write(self, path):
        with open(path, "a") as report:
            report.write(self.title_str)
            report.write(self.markdown_str)
