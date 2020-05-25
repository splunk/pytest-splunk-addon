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
        self.data = []

    def generate_report(self):
        report_gen = CIMReportGenerator(self.data)
        report_gen.generate_report(self.report_path)


def main():
    # Parse Args using arg parse 
    # Parse Junit path : input
    # parse report path : output
