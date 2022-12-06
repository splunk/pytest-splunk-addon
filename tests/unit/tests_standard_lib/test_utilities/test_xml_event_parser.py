import pytest

from pytest_splunk_addon.standard_lib.utilities.xml_event_parser import (
    strip_syslog_header,
    escape_char_event,
)


@pytest.mark.parametrize(
    "escape_char, expected_output",
    [
        ("\\", "SESSION \\\\ CREATED"),
        ("`", "SESSION \\` CREATED"),
        ("~", "SESSION \\~ CREATED"),
        ("!", "SESSION \\! CREATED"),
        ("@", "SESSION \\@ CREATED"),
        ("#", "SESSION \\# CREATED"),
        ("$", "SESSION \\$ CREATED"),
        ("%", "SESSION \\% CREATED"),
        ("^", "SESSION \\^ CREATED"),
        ("&", "SESSION \\& CREATED"),
        ("(", "SESSION \\( CREATED"),
        (")", "SESSION \\) CREATED"),
        ("-", "SESSION \\- CREATED"),
        ("=", "SESSION \\= CREATED"),
        ("+", "SESSION \\+ CREATED"),
        ("[", "SESSION \\[ CREATED"),
        ("]", "SESSION \\] CREATED"),
        ("}", "SESSION \\} CREATED"),
        ("{", "SESSION \\{ CREATED"),
        ("|", "SESSION \\| CREATED"),
        (";", "SESSION \\; CREATED"),
        (":", "SESSION \\: CREATED"),
        ("'", "SESSION \\' CREATED"),
        ("\,", "SESSION \\\\\, CREATED"),
        ("<", "SESSION \\< CREATED"),
        (">", "SESSION \\> CREATED"),
        ("\/", "SESSION \\\\\/ CREATED"),
        ("?", "SESSION \\? CREATED"),
        ("IN", "SESSION \\IN CREATED"),
        ("AS", "SESSION \\AS CREATED"),
        ("BY", "SESSION \\BY CREATED"),
        ("OVER", "SESSION \\OVER CREATED"),
        ("WHERE", "SESSION \\WHERE CREATED"),
        ("LIKE", "SESSION \\LIKE CREATED"),
        ("NOT", "SESSION \\NOT CREATED"),
    ],
)
def test_escape_char_event(escape_char, expected_output):
    assert escape_char_event(f"SESSION {escape_char} CREATED") == expected_output


@pytest.mark.parametrize(
    "raw_event, expected_output",
    [
        ("Oct 06 2021 14:44:59 10.10.10.10 : Received ARP", " Received ARP"),
        (
            "<34>1 2003-10-11T22:14:15.003Z mymachine.example.com Received ARP",
            "Received ARP",
        ),
        ("<34>Oct 11 22:14:15 mymachine su: su root /dev/pts/8", " su root /dev/pts/8"),
        (
            "time=1611840576|hostname=test_name|severity=Critical|confidence_level=High|product=test_product|action=Detect|ifdir=inbound|loguid=test",
            "time=1611840576|hostname=test_name|severity=Critical|confidence_level=High|product=test_product|action=Detect|ifdir=inbound|loguid=test",
        ),
        (
            "Jan 11 10:25:39 host CEF:Version|Device Vendor|Device Product|Device Version|Device Event Class ID|Name|Severity|[Extension]",
            "Version|Device Vendor|Device Product|Device Version|Device Event Class ID|Name|Severity|[Extension]",
        ),
        (
            '10.0.1.1 - - [04/Jan/2021:18:37:21 +0530] "GET /tomcat.svg HTTP/1.1" 200 67795',
            '"GET /tomcat.svg HTTP/1.1" 200 67795',
        ),
        ("- cisco dummy", None),
    ],
    ids=[
        "rfc5424-format",
        "rfc3164-format",
        "rfc3164-format-longer",
        "CEF-checkpoint-foramt",
        "CEF-format",
        "httpd-format",
        "wrong-format",
    ],
)
def test_strip_syslog_header(raw_event, expected_output):
    assert strip_syslog_header(raw_event) == expected_output
