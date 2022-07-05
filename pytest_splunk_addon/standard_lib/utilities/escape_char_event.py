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