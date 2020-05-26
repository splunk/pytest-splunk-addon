"""
Calculates the statistics of test cases and Creates a MarkDown Report
"""
# from .markdown_report import MarkDownReport
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

    # def __init__(self, data=[], report_class=MarkDownReport):
    def __init__(self, data=[]):
        self.data = data
        # self.report_generator = report_class()

    def add_data(self, data):
        self.data.append(data)

    def _group_by(self, keys, data=None):
        if not data:
            data = self.data
        return groupby(data, lambda testcase: [testcase[key] for key in keys])

    def _get_count_by(self, keys, data=None):
        for grouped_by, grouped_stats in self._group_by(keys, data):
            yield (
                grouped_by,
                Counter(each["status"] for each in grouped_stats),
            )

    @staticmethod
    def fail_count(counter):
        return "{}/{}".format(counter[True], (counter[False] + counter[True]))

    def generate_report(self, report_path):
        self.data.sort(
            key=lambda tc: (
                tc["data_model"],
                tc["data_set"],
                tc["tag_stanza"],
                tc["field"],
            )
        )
        print("data model\tFail/Total")
        for data_model, stats in self._get_count_by(["data_model"]):
            print("\t".join([data_model[0], self.fail_count(stats)]))

        print("\ntag_stanza\tdata_set\tFail/Total")
        for group, stats in self._get_count_by(["data_set", "tag_stanza"]):
            data_set, tag_stanza = group
            print("\t".join([tag_stanza, data_set, self.fail_count(stats)]))

        for group_name, grouped_data in self._group_by(
            ["tag_stanza", "data_set"]
        ):
            print("\n\n")
            print(" - ".join(group_name))
            print("==========")
            for each_data in grouped_data:
                print(each_data["field"], each_data["status"])
