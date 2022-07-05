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
    # bounded_asterisk = re.search(
    #     r"\"[\s*\w*\.\-\,\\\?\_\]\[\']*\*+[\s*\w*\.\-\,\\\?\_\[\]\']*\"", event
    # )
    bounded_asterisk = re.search(r"\".*?\*+.*?\"", event)
    if bounded_asterisk:
        event = event.replace("*", "\\*")
    else:
        event = event.replace("*", " ")
    for character in escape_splunk_chars:
        event = event.replace(character, "\\" + character)
    return event
