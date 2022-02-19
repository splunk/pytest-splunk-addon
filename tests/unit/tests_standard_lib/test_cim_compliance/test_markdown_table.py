from unittest.mock import patch

import pytest

from pytest_splunk_addon.standard_lib.cim_compliance.markdown_table import MarkdownTable


@pytest.fixture()
def markdown_table():
    with patch.object(MarkdownTable, "__init__", return_value=None):
        return MarkdownTable()


def test_markdown_table_instantiation():
    with patch.object(
        MarkdownTable,
        "_MarkdownTable__set_title",
        return_value="set_title_return_value",
    ), patch.object(
        MarkdownTable,
        "_MarkdownTable__set_headers",
        return_value="set_headers_return_value",
    ):
        markdown_table = MarkdownTable("test title", ["header1", "header2"])
        assert markdown_table.table_title == "set_title_return_value"
        assert markdown_table.table_headers == "set_headers_return_value"


@pytest.mark.parametrize(
    "title, expected_output",
    [
        ("new title", "### new title"),
        ("", ""),
    ],
)
def test_set_title(markdown_table, title, expected_output):
    assert markdown_table._MarkdownTable__set_title(title) == expected_output


def test_set_headers(markdown_table):
    assert (
        markdown_table._MarkdownTable__set_headers(["head", "h", "header"])
        == "\n| head | h | header  |\n |:----|:-|:------ |\n"
    )


def test_set_description(markdown_table):
    markdown_table.set_description("test descr")
    assert markdown_table.table_description == "\n test descr \n"


def test_add_row(markdown_table):
    markdown_table.row_str = "previous row |"
    markdown_table.add_row(["value_1", "v2", "val3"])
    assert markdown_table.row_str == "previous row || value_1 | v2 | val3  |\n"


def test_set_note(markdown_table):
    markdown_table.set_note("test note")
    assert markdown_table.table_note == "\n*NOTE: test note *\n "


def test_return_table_str(markdown_table):
    markdown_table.table_title = "table title\n"
    markdown_table.table_description = "table description\n"
    markdown_table.table_headers = "table headers\n"
    markdown_table.row_str = "row str\n"
    markdown_table.table_note = "table note\n"
    assert (
        markdown_table.return_table_str()
        == "table title\ntable description\ntable headers\nrow str\ntable note\n\n"
    )
