"""
Calculates the statistics of test cases and Creates a MarkDown Report
"""
from .markdown_report import MarkDownReport
from .markdown_table import MarkdownTable
from itertools import groupby
from collections import Counter

SUPPORTED_DATAMODELS = [
    "Alerts",
    "Authentication",
    "Certificates",
    "Change",
    "DLP",
    "Email",
    "Endpoint",
    "Intrusion_Detection",
    "Malware",
    "Network_Resolution",
    "Network_Sessions",
    "Network_Traffic",
    "Updates",
    "Vulnerabilities",
    "Web",
]
NOT_SUPPORTED_DATAMODELS = [
    "Application_State",
    "Change_Analysis",
    "Compute_Inventory",
    "Databases",
    "Event_Signatures",
    "Interprocess_Messaging",
    "JVM",
    "Performance",
    "Splunk_Audit",
    "Splunk_CIM_Validation",
    "Ticket_Management",
]


class CIMReportGenerator(object):
    """
    Generate the Report
    data format::

        [
                {
                    "data_model": "A",
                    "field": "aaa",
                    "data_set": "AAA",
                    "tag_stanza": "p",
                    "status": "pass"/"fail"
                }
        ]
    """

    def __init__(self, data=[], report_class=MarkDownReport):
        self.data = data
        self.report_generator = report_class()

    def add_data(self, data):
        """
        adds data to object property.

        Args:
            data(list): List of dictionaries with specified format.
        """
        self.data.append(data)

    def _group_by(self, keys, data=None):
        """
        Function to generate group of data using Keys provided

        Args:
            keys(list): Contains keys to group data by.
            data(list): list of dictionaries with specified format.
        
        Yields:
            data_set.DataSet: data set object mapped with the tags
        """
        if not data:
            data = self.data
        return groupby(
            sorted(data, key=lambda data: data["data_model"]),
            lambda testcase: [testcase[key] for key in keys],
        )

    def _get_count_by(self, keys, data=None):
        """
        Function to generate count of data using Keys provided

        Args:
            keys(list): Contains keys to generate count by.
            data(list): list of dictionaries with specified format.
        
        Yields:
            data_set.DataSet: data set object mapped with the tags
        """
        for grouped_by, grouped_stats in self._group_by(keys, data):
            yield (
                grouped_by,
                Counter(each["status"] for each in grouped_stats),
            )

    @staticmethod
    def pass_count(counter):
        """
        Function to Get count in Pass/Total format.

        Args:
            counter(collections.Counter): Contains counts of passing/failing Testcases.
        
        Yields:
            String: string with pass/total format.
        """
        return "{}/{}".format(
            counter["passed"],
            (counter["failed"] + counter["passed"] + counter["skipped"]),
        )

    @staticmethod
    def fail_count(counter):
        """
        Function to Get count in Fail/Total format.

        Args:
            counter(collections.Counter): Contains counts of passing/failing Testcases.
        
        Yields:
            String: string with fail/total format.
        """
        return "{}/{}".format(
            counter["failed"],
            (counter["failed"] + counter["passed"] + counter["skipped"]),
        )

    def generate_summary_table(self):
        """
        Displays test case summary of the add-on for all the supported data models.
        """
        self.report_generator.add_section_title(" Summary")
        self.report_generator.add_section_description("Displays test case summary of the add-on for all the supported data models.")
        summary_table = MarkdownTable("", ["Data Model", "Status", "Fail/Total"])

        data_models = iter(SUPPORTED_DATAMODELS)

        for data_model, stats in self._get_count_by(["data_model"]):
            for each_model in data_models:
                if each_model == data_model[0]:
                    status = "Passed" if stats["failed"] == 0 else "Failed"
                    summary_table.add_row(
                        [data_model[0], status, self.fail_count(stats)]
                    )
                    break
                else:
                    summary_table.add_row([each_model, "N/A", "-"])

        for each in data_models:
            summary_table.add_row([each, "N/A", "-"])

        self.report_generator.add_table(summary_table.return_table_str())

    def generate_tag_stanza_mapping_table(self):
        """
        Displays test case summary for the stanzas in tags.conf and the dataset mapped with it.
        """
        self.report_generator.add_section_title("Tag Stanza Mapping")
        self.report_generator.add_section_description("Displays test case summary for the stanzas in tags.conf and the data model mapped with it.")
        tag_stanza_map = MarkdownTable(
            "", ["Tag Stanza", "Data Model", "Data Set", "Fail/Total"]
        )
        for group, stats in self._get_count_by(
            ["tag_stanza", "data_model", "data_set"]
        ):
            tag_stanza, data_model, data_set = group
            tag_stanza_map.add_row(
                [tag_stanza, data_model, data_set, self.fail_count(stats)]
            )

        self.report_generator.add_table(tag_stanza_map.return_table_str())

    def generate_field_summary_table(self):
        """
        Displays test case summary for all the fields in the dataset for the tag-stanza it is mapped with.
        """
        self.report_generator.add_section_title("Field Summary")
        self.report_generator.add_section_description("Displays test case summary for all the fields in the dataset for the tag-stanza it is mapped with.")

        for group_name, grouped_data in self._group_by(["tag_stanza", "data_set"]):
            field_summary_table = MarkdownTable(
                " - ".join(group_name),
                ["Field", "Type", "Test Status", "Failure Message"],
            )

            for each_data in grouped_data:
                fields = False
                if each_data["fields"] and not "," in each_data["fields"]:
                    fields = True
                    field_summary_table.add_row(
                        [
                            each_data["fields"],
                            each_data["fields_type"],
                            each_data["status"].title(),
                            each_data["test_property"],
                        ]
                    )
            if not fields:
                field_summary_table.add_row(["-", "-", "-", "-"])
            self.report_generator.add_table(field_summary_table.return_table_str())
            del field_summary_table

    def generate_skip_tests_table(self):
        """
        """
        skipped_tests = list(filter(lambda d: d["status"] == "skipped", self.data))
        if skipped_tests:
            skipped_tests_table = MarkdownTable(
                "", ["Tag Stanza", "Data Set", "Field"],
            )
            self.report_generator.add_section_title("Skipped Tests Summary")
            for group, stats in self._get_count_by(
                ["tag_stanza", "data_set", "fields"], skipped_tests,
            ):
                tag_stanza, data_set, field = group
                if not field:
                    field = "-"
                skipped_tests_table.add_row([tag_stanza, data_set, field])

            self.report_generator.add_table(skipped_tests_table.return_table_str())

    def generate_report(self, report_path):
        """
        Function to generate report from the stored data.

        Args:
            report_path(string): Path to create the report.
        """
        self.report_generator.set_title("CIM AUDIT REPORT")
        self.data.sort(
            key=lambda tc: (
                tc["tag_stanza"],
                tc["data_model"],
                tc["data_set"],
                tc["fields"],
                tc["fields_type"],
            )
        )

        # Generating Summary table.
        self.generate_summary_table()

        # Generating Tag Stanza Mapping table.
        self.generate_tag_stanza_mapping_table()

        # Generating Field Summary tables.
        self.generate_field_summary_table()

        # Generating Skipped tests Table
        self.generate_skip_tests_table()

        # Table for not supported datamodels
        nsd_table = MarkdownTable("Not Supported Datamodels", ["Name"])
        for each_model in NOT_SUPPORTED_DATAMODELS:
            nsd_table.add_row([each_model])
        self.report_generator.add_table(nsd_table.return_table_str())

        # Writing into markdown file
        if self.data:
            self.report_generator.write(report_path)
