import pytest
from unittest.mock import MagicMock, patch, call
from collections import Counter
from pytest_splunk_addon.standard_lib.cim_compliance.cim_report_generator import (
    CIMReportGenerator,
)


@pytest.fixture()
def cim_report_generator():
    mdr = MagicMock()
    mdr.return_value = mdr
    return CIMReportGenerator(data=[{"data": "init"}], report_class=mdr)


@pytest.fixture()
def markdown_table_mock(monkeypatch):
    mdt = MagicMock()
    mdt.return_value = mdt
    mdt.return_table_str.return_value = "| table |"
    monkeypatch.setattr(
        "pytest_splunk_addon.standard_lib.cim_compliance.cim_report_generator.MarkdownTable",
        mdt,
    )
    return mdt


def test_add_data(cim_report_generator):
    cim_report_generator.add_data([{"data": "end"}])
    assert cim_report_generator.data == [{"data": "init"}, [{"data": "end"}]]


@pytest.mark.parametrize(
    "keys, data, expected_output",
    [
        (
            ["data_model"],
            [
                {"data_model": "Network_Traffic", "fields": "command"},
                {"data_model": "Authentication", "fields": "change_type"},
            ],
            "['Authentication']: {'data_model': 'Authentication', 'fields': 'change_type'}\n"
            "['Network_Traffic']: {'data_model': 'Network_Traffic', 'fields': 'command'}\n",
        ),
        (
            ["data_model"],
            None,
            "['Change']: {'data_model': 'Change', 'fields': 'action'}\n"
            "['Malware']: {'data_model': 'Malware', 'fields': 'dest'}\n",
        ),
    ],
)
def test_group_by(cim_report_generator, keys, data, expected_output):
    cim_report_generator.data = [
        {"data_model": "Change", "fields": "action"},
        {"data_model": "Malware", "fields": "dest"},
    ]
    out = ""
    for grouped_by, grouped_stats in cim_report_generator._group_by(keys, data):
        out += f'{grouped_by}: {"".join([str(x) for x in grouped_stats])}\n'
    assert out == expected_output


def test_get_count_by(cim_report_generator):
    with patch.object(
        CIMReportGenerator,
        "_group_by",
        return_value=[
            (["group1"], [{"status": "passed"}]),
            (["group2"], [{"status": "failed"}, {"status": "failed"}]),
            (
                ["group3"],
                [
                    {"status": "skipped"},
                    {"status": "passed"},
                    {"status": "pass"},
                    {"status": "passed"},
                ],
            ),
        ],
    ):
        out = list(cim_report_generator._get_count_by(["k1"]))
        assert out == [
            (["group1"], Counter({"passed": 1})),
            (["group2"], Counter({"failed": 2})),
            (["group3"], Counter({"skipped": 1, "passed": 2, "pass": 1})),
        ]


def test_pass_count():
    counter = {"passed": 9, "failed": 2, "skipped": 1}
    assert CIMReportGenerator.pass_count(counter) == "9/12"


def test_fail_count():
    counter = {"passed": 9, "failed": 2, "skipped": 1}
    assert CIMReportGenerator.fail_count(counter) == "2/12"


def test_generate_summary_table(cim_report_generator, markdown_table_mock):
    with patch.object(
        CIMReportGenerator,
        "_get_count_by",
        return_value=[
            (["Alerts"], {"failed": 0}),
            (["Updates"], {"failed": 1}),
        ],
    ), patch.object(CIMReportGenerator, "fail_count", side_effect=[0, 1]):
        cim_report_generator.generate_summary_table()
        markdown_table_mock.assert_has_calls(
            [
                call("", ["Data Model", "Status", "Fail/Total"]),
                call.add_row(["Alerts", "Passed", 0]),
                call.add_row(["Updates", "Failed", 1]),
                call.return_table_str(),
            ],
            any_order=True,
        )
        cim_report_generator.report_generator.assert_has_calls(
            [
                call.add_section_title(" Summary"),
                call.add_section_description(
                    "Displays test case summary of the add-on for all the supported data models."
                ),
                call.add_table("| table |"),
            ]
        )


def test_generate_tag_stanza_mapping_table(cim_report_generator, markdown_table_mock):
    with patch.object(
        CIMReportGenerator,
        "_get_count_by",
        return_value=[
            (["event_traffic", "Network_Traffic", "All_Traffic"], {"failed": 0}),
            (
                ["file_integrity_monitoring", "Malware", "Malware_Attacks"],
                {"failed": 1},
            ),
        ],
    ), patch.object(CIMReportGenerator, "fail_count", side_effect=[0, 1]):
        cim_report_generator.generate_tag_stanza_mapping_table()
        markdown_table_mock.assert_has_calls(
            [
                call("", ["Tag Stanza", "Data Model", "Data Set", "Fail/Total"]),
                call.add_row(["event_traffic", "Network_Traffic", "All_Traffic", 0]),
                call.add_row(
                    ["file_integrity_monitoring", "Malware", "Malware_Attacks", 1]
                ),
                call.return_table_str(),
            ],
        )
        cim_report_generator.report_generator.assert_has_calls(
            [
                call.add_section_title("Tag Stanza Mapping"),
                call.add_section_description(
                    "Displays test case summary for the stanzas in tags.conf and the data model mapped with it."
                ),
                call.add_table("| table |"),
            ]
        )


def test_generate_field_summary_table(cim_report_generator, markdown_table_mock):
    with patch.object(
        CIMReportGenerator,
        "_group_by",
        return_value=[
            (
                ["tag_stanza_1", "All_Changes"],
                [
                    {
                        "data_model": "Change",
                        "fields": "action",
                        "fields_type": "required",
                        "status": "passed",
                        "test_property": "test_prop",
                    }
                ],
            ),
            (
                ["file_authentication", "Default_Authentication"],
                [
                    {
                        "fields": "",
                        "fields_type": "required",
                        "status": "skipped",
                        "test_property": "-",
                    }
                ],
            ),
        ],
    ):
        cim_report_generator.generate_field_summary_table()
        markdown_table_mock.assert_has_calls(
            [
                call(
                    "tag_stanza_1 - All_Changes",
                    ["Field", "Type", "Test Status", "Failure Message"],
                ),
                call.add_row(["action", "required", "Passed", "test_prop"]),
                call.return_table_str(),
                call(
                    "file_authentication - Default_Authentication",
                    ["Field", "Type", "Test Status", "Failure Message"],
                ),
                call.add_row(["-", "-", "-", "-"]),
                call.return_table_str(),
            ],
        )
        cim_report_generator.report_generator.assert_has_calls(
            [
                call.add_section_title("Field Summary"),
                call.add_section_description(
                    "Displays test case summary for all the fields in the dataset for the tag-stanza it is mapped with."
                ),
                call.add_table("| table |"),
            ]
        )


def test_generate_skip_tests_table(cim_report_generator, markdown_table_mock):
    cim_report_generator.data = [
        {"status": "failed"},
        {"status": "skipped"},
        {"status": "skipped"},
    ]
    with patch.object(
        CIMReportGenerator,
        "_group_by",
        return_value=[
            (
                ["event_traffic", "All_Traffic", ""],
                [],
            ),
            (
                ["file_authentication", "Default_Authentication", "change_type"],
                [],
            ),
        ],
    ):
        cim_report_generator.generate_skip_tests_table()
        markdown_table_mock.assert_has_calls(
            [
                call("", ["Tag Stanza", "Data Set", "Field"]),
                call.add_row(["event_traffic", "All_Traffic", "-"]),
                call.add_row(
                    ["file_authentication", "Default_Authentication", "change_type"]
                ),
                call.return_table_str(),
            ],
        )
        cim_report_generator.report_generator.assert_has_calls(
            [
                call.add_section_title("Skipped Tests Summary"),
                call.add_table("| table |"),
            ]
        )
