"""
Parse the Junit XML report and convert it to required format
"""
from .ca_report_generator import CIMReportGenerator
import argparse
class JunitParser(object):
    def __init__(self, junit_path, report_path):
        self.junit_path = junit_path
        self.report_path = report_path

    def parse_junit(self):
        # Parsing Logic
        # assign to self.data
        self.data = [
            {
                "data_model": "A",
                "field": "aaa",
                "data_set": "AAA",
                "eventtype": "p",
                "status": True
            },
            {
                "data_model": "B",
                "field": "bbb",
                "data_set": "BBB",
                "eventtype": "p",
                "status": False
            },{
                "data_model": "A",
                "field": "ccc",
                "data_set": "AAA",
                "eventtype": "q",
                "status": False
            },{
                "data_model": "B",
                "field": "bbb",
                "data_set": "CCC",
                "eventtype": "q",
                "status": False
            },{
                "data_model": "C",
                "field": "ddd",
                "data_set": "CCC",
                "eventtype": "q",
                "status": True
            },
        ]

    def generate_report(self):
        self.parse_junit()
        report_gen = CIMReportGenerator(self.data)
        report_gen.generate_report(self.report_path)


def main():
    jp = JunitParser("a", "b")
    jp.generate_report()

if __name__=="__main__":
    main()
