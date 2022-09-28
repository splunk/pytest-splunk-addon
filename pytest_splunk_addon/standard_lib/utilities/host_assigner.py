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
import os
import argparse
from lxml import etree


def assign_host(sample_path, pattern, output_dir=None):
    """
    Assigns host value to transport stanza in xml format file based on provided pattern.

    Args:
        sample_path:  path to file with samples
        output_dir:   path to directory where separated files will be stored. Default the same dir as input file
        pattern:      regex pattern with capture group for host value in samples
    """

    parser = etree.XMLParser(strip_cdata=False)
    if output_dir is None:
        output_dir = os.path.dirname(sample_path)
    tree = etree.parse(sample_path, parser)
    root = tree.getroot()
    events = root.findall("event")
    filename, ext = os.path.splitext(sample_path)
    output_filename = f"{filename}_assigned_host{ext}"
    for each_event in events:
        raw = each_event.find("raw")
        transport = each_event.find("transport")
        if raw is not None and transport is not None:
            try:
                extracted_hosts = re.search(pattern, raw.text).groups()
                extracted_hosts = [h for h in extracted_hosts if h]
            except Exception as e:
                print(f"Exception occurred for event: {raw.text}")
                print(e)
            else:
                if len(extracted_hosts) == 1:
                    host = extracted_hosts[0]
                    print(
                        f"Found matching unique host value. Assigning host value to: {host}"
                    )
                    transport.set("host", host)
                else:
                    print(
                        f"Unexpected behavior for pattern: {pattern} and sample {raw.text}"
                    )
    tree.write(
        os.path.join(output_dir, output_filename),
        encoding="utf-8",
        xml_declaration=True,
    )


def main():
    parser = argparse.ArgumentParser(
        description="Assign host value to transport stanza based on provided regular expression"
    )
    parser.add_argument("file", help="xml file with samples that need host assignment")
    parser.add_argument(
        "-r", "--regex", help="Regular expression needed for host assignment"
    )
    parser.add_argument(
        "-o",
        "--output_dir",
        default=None,
        help="Output dir for xml file with assigned host",
    )
    args = parser.parse_args()
    sample_path = args.file
    pattern = args.regex
    output_dir = args.output_dir
    assign_host(sample_path, pattern, output_dir)


if __name__ == "__main__":
    main()
