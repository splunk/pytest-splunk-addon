"""
Parse the Junit XML report and convert it to required format
"""
from .ca_report_generator import CIMReportGenerator
import argparse
import errno
import os
import sys
from junitparser import JUnitXml, Properties


class JunitParser(object):
    def __init__(self, junit_xml_path, report_path):
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

        self.report_path = report_path
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
                    not tc.result or tc.result._tag == "failure"
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
        row_template = {
            "data_model": None,
            "data_set": None,
            "fields": None,
            "status": "fail" if testcase.result else "pass",
            "tag_stanza": None,
        }
        props = self.yield_properties(testcase)
        for prop in props:
            if prop.name in row_template:
                row_template[prop.name] = prop.value
        return row_template

    def yield_properties(self, testcase):
        """
        Function to yield properties of a Testcase

        Args:
            testcase(junitparser.TestCase): Contains all the data of a Testcase.
        
        Yields:
            junitparser.Property: Property object of a Testcase.
        """
        props = testcase.child(Properties)
        for prop in props:
            yield prop

    def generate_report(self):
        self.parse_junit()
        report_gen = CIMReportGenerator(self.data)
        report_gen.generate_report(self.report_path)


def main():
    """
        Entrypoint to the script.
    """
    ap = argparse.ArgumentParser()
    group = ap.add_mutually_exclusive_group()
    ap.add_argument("--junit-xml-path", help="Path to JUnit file", required=True)
    ap.add_argument(
        "--report-path", help="Path to Save Report", required=True
    )
    group.add_argument(
        "--overwrite", action="store_true", help="Overwrites report if exists"
    )
    group.add_argument(
        "--append", action="store_true", help="Append report if exists"
    )
    args = ap.parse_args()

    junit_xml_path = args.junit_xml_path
    report_path = args.report_path

    if args.overwrite:
        open(report_path, "w").close()
    elif not args.append and os.path.isfile(report_path):
        sys.exit(
            "File already Exists. Provide --append or --overwrite to continue."
        )

    ju_p = JunitParser(junit_xml_path, report_path,)
    ju_p.parse_junit()
    ju_p.generate_report()


if __name__ == "__main__":
    main()
