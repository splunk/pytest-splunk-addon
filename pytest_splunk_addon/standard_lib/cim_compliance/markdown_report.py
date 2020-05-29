"""
Markdown generator
"""
from .base_report import CIMReport


class MarkDownReport(CIMReport):
    def __init__(self):
        self.markdown_str = ""
        self.note_str = ""

    def set_title(self, title_string):
        """
        Function to set title of a report

        Args:
            title_string(string): String containing title for report.
        """
        self.title_str = "# {} \n".format(title_string)

    def add_section_title(self, section_title):
        """
        Function to add new section to report

        Args:
            section_title(string): String containing title for new Section.
        """
        self.markdown_str += "\n## {}\n".format(section_title)

    def add_section_description(self, description):
        """
        Adds description string to the section

        Args:
            description(str): Description string.
        """
        self.markdown_str += "\n**Description:** " + description + "\n"

    def add_section_note(self, section_note):
        """
        Function to set Note in a report

        Args:
            section_note(string): String containing note for report.
        """
        self.note_str = "## Note: {} \n".format(section_note)

    def add_table(self, table_string):
        """
        Function to add a table to the Report.

        Args:
            table_string(string): Stringified table.
        """
        self.markdown_str += table_string

    def write(self, path):
        """
        Function to add a table to the Report.

        Args:
            path(string) : path to store report file.
        """
        with open(path, "w") as report:
            report.write(self.title_str)
            report.write(self.markdown_str)
            report.write(self.note_str)
