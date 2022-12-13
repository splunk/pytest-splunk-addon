#
# Copyright 2021 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import re
from collections import OrderedDict


supported_headers = OrderedDict(
    [
        (
            "CEF",
            {
                "regex": r"\s(CEF:\d\|[^\|]+\|([^\|]+)\|[^\|]+\|[^\|]+\|[^\|]+\|([^\|]+)\|(.*))",
                "match_element": 1,
            },
        ),
        (
            "CEF_checkpoint",
            {
                "regex": r"(time=\d+\|[^\|]+\|([^\|]+)\|[^\|]+\|[^\|]+\|[^\|]+\|([^\|]+)\|(.*))",
                "match_element": 1,
            },
        ),
        (
            "rfc5424",
            {
                "regex": r"(?:(\d{4}[-]\d{2}[-]\d{2}[T]\d{2}[:]\d{2}[:]\d{2}(?:\.\d{1,6})?(?:[+-]\d{2}[:]\d{2}|Z)?))\s(?:([\w][\w\d\.@-]*)|-)\s(.*)$",
                "match_element": 3,
            },
        ),
        (
            "rfc3164",
            {
                "regex": r"([A-Z][a-z][a-z]\s{1,2}\d{1,2}(?:\s\d{4})?\s\d{2}[:]\d{2}[:]\d{2})\s+([\w][\w\d\.@-]*)\s\w*:?(.*)$",
                "match_element": 3,
            },
        ),
        (
            "httpd",
            {
                "regex": r"((?:\d+(?:(?:\.|:)[0-9a-fA-F]{0,4}){3,8}))(?:\s(?:-|\w+))*\s\[(\d{1,2}\/\w+\/\d{4}(?:[:]\d{2}){3}(?:\.\d{1,6})?(?:\s[+-]\d{2}[:]?\d{2})?(?:Z)?)]\s(.*)$",
                "match_element": 3,
            },
        ),
    ]
)


def escape_char_event(event):
    """
    Input: Event getting parsed
    Function to escape special characters in Splunk
    https://docs.splunk.com/Documentation/StyleGuide/current/StyleGuide/Specialcharacters
    """
    escape_splunk_chars = [
        "`",
        "~",
        "!",
        "@",
        "#",
        "$",
        "%",
        "^",
        "&",
        "(",
        ")",
        "-",
        "=",
        "+",
        "[",
        "]",
        "}",
        "{",
        "|",
        ";",
        ":",
        "'",
        r"\,",
        "<",
        ">",
        r"\/",
        "?",
        "IN",
        "AS",
        "BY",
        "OVER",
        "WHERE",
        "LIKE",
        "NOT",
        '"',
    ]
    event = event.replace("\\", "\\\\")
    bounded_asterisk = re.search(r"\".*?\*+.*?\"", event)
    if bounded_asterisk:
        event = event.replace("*", "\\*")
    else:
        event = event.replace("*", " ")
    for character in escape_splunk_chars:
        event = event.replace(character, "\\" + character)
    return event


def strip_syslog_header(raw_event):
    """
    removes syslog header and returns event without it, make sure header type is added to supported_headers
    Input: raw event
    """
    # remove leading space chars
    raw_event = raw_event.strip()
    for header_format in supported_headers.values():
        header_match = re.search(header_format.get("regex"), raw_event)
        if header_match:
            return header_match.group(header_format.get("match_element"))
