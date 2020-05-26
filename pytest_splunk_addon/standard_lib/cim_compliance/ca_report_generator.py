"""
Calculates the statistics of test cases and Creates a MarkDown Report
"""
from .markdown_report import MarkDownReport
from itertools import groupby
from collections import Counter


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
                    "status": True
                }
        ]
    """

    def __init__(self, data=[], report_class=MarkDownReport):
        self.data = data
        self.report_generator = report_class()

    def add_data(self, data):
        self.data.append(data)

    def get_count_by(self, keys):
        for data_model, grouped_stats in groupby(
            self.data, lambda testcase: [testcase[key] for key in keys]
        ):
            print(
                data_model, Counter(each["status"] for each in grouped_stats)
            )

    def generate_report(self, report_path):
        self.data.sort(
            key=lambda tc: (
                tc["data_model"],
                tc["data_set"],
                tc["tag_stanza"],
                tc["field"],
            )
        )
        self.get_count_by(["data_model"])
        self.get_count_by(["data_set", "tag_stanza"])

        # Save
