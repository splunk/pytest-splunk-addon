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
    # remove leading space chars
    raw_event = raw_event.strip()
    CEF_format_match = re.search(
        r"\s(CEF:\d\|[^\|]+\|([^\|]+)\|[^\|]+\|[^\|]+\|[^\|]+\|([^\|]+)\|(.*))",
        raw_event,
    )
    if CEF_format_match:
        stripped_header = CEF_format_match.group(1)
        return stripped_header
    CEF_checkpoint_match = re.search(
        r"(time=\d+\|[^\|]+\|([^\|]+)\|[^\|]+\|[^\|]+\|[^\|]+\|([^\|]+)\|(.*))",
        raw_event,
    )
    if CEF_checkpoint_match:
        stripped_header = CEF_checkpoint_match.group(1)
        return stripped_header
    regex_rfc5424 = re.search(
        r"(?:(\d{4}[-]\d{2}[-]\d{2}[T]\d{2}[:]\d{2}[:]\d{2}(?:\.\d{1,6})?(?:[+-]\d{2}[:]\d{2}|Z)?)|-)\s(?:([\w][\w\d\.@-]*)|-)\s(.*)$",
        raw_event,
    )
    if regex_rfc5424:
        stripped_header = regex_rfc5424.group(3)
        return stripped_header
    regex_rfc3164 = re.search(
        r"([A-Z][a-z][a-z]\s{1,2}\d{1,2}(?:\s\d{4})?\s\d{2}[:]\d{2}[:]\d{2})\s+([\w][\w\d\.@-]*)\s\w*:?(.*)$",
        raw_event,
    )
    if regex_rfc3164:
        stripped_header = regex_rfc3164.group(3)
        return stripped_header
    if not (CEF_format_match and regex_rfc3164 and regex_rfc5424):
        return None
