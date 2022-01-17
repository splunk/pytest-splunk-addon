import pytest
import os

from pytest_splunk_addon.standard_lib.cim_compliance import CIMReportGenerator


# class TestCIMReport(object):
#     @pytest.mark.kubernetes
#     def test_report(self):
#         data = [
#             {
#                 "data_model": "Change",
#                 "fields": "action",
#                 "fields_type": "required",
#                 "data_set": "All_Changes",
#                 "tag_stanza": "tag_stanza_1",
#                 "status": "passed",
#                 "test_property": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
#             },
#             {
#                 "data_model": "Authentication",
#                 "fields": "change_type",
#                 "fields_type": "required",
#                 "data_set": "Default_Authentication",
#                 "tag_stanza": "file_authentication",
#                 "status": "skipped",
#                 "test_property": "-",
#             },
#             {
#                 "data_model": "Network_Traffic",
#                 "fields": "command",
#                 "fields_type": "conditional",
#                 "data_set": "All_Traffic",
#                 "tag_stanza": "event_traffic",
#                 "status": "failed",
#                 "test_property": "AssertionError: Field command is not extracted in any events.",
#             },
#             {
#                 "data_model": "Malware",
#                 "fields": "dest",
#                 "fields_type": "required",
#                 "data_set": "Malware_Attacks",
#                 "tag_stanza": "file_integrity_monitoring",
#                 "status": "passed",
#                 "test_property": "-",
#             },
#         ]
#         cim_report_gen = CIMReportGenerator(data)
#         cim_report_gen.generate_report("test_report.md")

#         with open("test_report.md", "r") as inputfile:
#             test_data = inputfile.read()
#         with open(
#             os.path.join(
#                 os.path.dirname(__file__), "test_data", "sample_cim_report.md"
#             ),
#             "r",
#         ) as input_file:
#             actual_data = input_file.read()
#         assert test_data == actual_data
