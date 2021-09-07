from unittest.mock import call

import pytest

from pytest_splunk_addon.standard_lib.cim_compliance.markdown_report import (
    MarkDownReport,
)

MARKDOWN_STR = "init string"
NOTE_STR = "init note"


@pytest.fixture()
def mark_down_report():
    report = MarkDownReport()
    report.markdown_str = MARKDOWN_STR
    report.note_str = NOTE_STR
    return report


def test_set_title(mark_down_report):
    mark_down_report.set_title("test_title")
    assert mark_down_report.title_str == "# test_title \n"


def test_add_section_title(mark_down_report):
    mark_down_report.add_section_title("test section title")
    assert mark_down_report.markdown_str == f"{MARKDOWN_STR}\n## test section title\n"


def test_add_section_description(mark_down_report):
    mark_down_report.add_section_description("test section descr")
    assert (
        mark_down_report.markdown_str
        == f"{MARKDOWN_STR}\n**Description:** test section descr\n"
    )


def test_add_section_note(mark_down_report):
    mark_down_report.add_section_note("test section note")
    assert mark_down_report.note_str == f"## Note: test section note \n"


def test_add_table(mark_down_report):
    mark_down_report.add_table("test table")
    assert mark_down_report.markdown_str == f"{MARKDOWN_STR}test table"


def test_write(mark_down_report, open_mock):
    mark_down_report.title_str = "new title"
    mark_down_report.write("fake_path")
    open_mock.assert_has_calls(
        [
            call("fake_path", "w"),
            call().__enter__(),
            call().write("new title"),
            call().write(MARKDOWN_STR),
            call().write(NOTE_STR),
            call().__exit__(None, None, None),
        ]
    )
