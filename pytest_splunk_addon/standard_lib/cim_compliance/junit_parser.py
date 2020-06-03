"""
Parse the Junit XML report and convert it to required format
"""
from . import CIMReportGenerator
import argparse
import errno
import os
import sys
from html import escape, unescape
from junitparser import JUnitXml, Properties


class JunitParser(object):
    def __init__(self, junit_xml_path):
        if os.path.isfile(junit_xml_path):
            self._junitfile = junit_xml_path
        elif os.path.isdir(junit_xml_path):
            raise Exception(
                "Generating Report for multiple xml is not currently Supported."
            )
        else:
            raise FileNotFoundError(
                errno.ENOENT, os.strerror(errno.ENOENT), junit_xml_path
            )

        self._xml = JUnitXml.fromfile(self._junitfile)

    def parse_junit(self):
        """
        Function to parse the provided JUnit XML.
        It creates and adds a list of dictionaries `data` to object properties.
        """
        xml = self._xml
        self.data = []

        for suites in xml:
            for tc in suites:
                if "test_cim_required_fields" in tc.name and (
                    not tc.result or tc.result._tag in ["failure", "skipped"]
                ):
                    self.data.append(self.get_properties(tc))

    def get_properties(self, testcase):
        """
        Function to get all the properties of a testcase.

        Args:
            testcase(junitparser.TestCase): Contains all the data of a Testcase
        
        returns:
            Dictionary: dictionary with all the required properties of Testcase.
        """
        if testcase.result:
            status = (
                "failed" if testcase.result._tag == "failure" else "skipped"
            )
        else:
            status = "passed"

        test_property = (
            "-"
            if not status == "failed"
            else escape(
                unescape(testcase.result.message.splitlines()[0])[:100]
            )
        )
        row_template = {
            "status": status,
            "test_property": test_property,
        }
        for prop in self.yield_properties(testcase):
            if prop.name in [
                "data_model",
                "data_set",
                "fields",
                "tag_stanza",
                "fields_type",
            ]:
                row_template[prop.name] = prop.value

        if len(row_template) != 7:
            raise Exception(
                testcase.name + " does not have all required properties"
            )
        return row_template

    def yield_properties(self, testcase):
        """
        Function to yield properties of a Testcase

        Args:
            testcase(junitparser.TestCase): Contains all the data of a Testcase.
        
        Yields:
            junitparser.Property: Property object of a Testcase.
        """
        yield from testcase.child(Properties)

    def generate_report(
        self, report_path,
    ):
        self.parse_junit()
        report_gen = CIMReportGenerator(self.data)
        report_gen.generate_report(report_path)


def main():
    """
        Entrypoint to the script.
    """
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "junit_xml", help="Path to JUnit XML file", metavar="junit-xml"
    )
    ap.add_argument(
        "report_path",
        help="Path to Save Report",
        metavar="report-path",
        nargs="?",
        default="cim_report.md",
    )
    args = ap.parse_args()

    junit_xml_path = args.junit_xml
    report_path = args.report_path

    ju_p = JunitParser(junit_xml_path)
    ju_p.parse_junit()
    if ju_p.data:
        ju_p.generate_report(report_path)
    else:
        sys.exit("No CIM Compatibility tests found in JUnit XML")


if __name__ == "__main__":
    main()
