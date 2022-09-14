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

import xmltodict
import os
import argparse
from collections import defaultdict


def split_samples(sample_path, output_dir=None, splitter="sourcetype"):
    """
    Splits events to separate files based on provided field

    Args:
        sample_path:  path to file with samples
        output_dir:   path to directory where separated files will be stored. Default the same dir as input file
        splitter:     depend on what field samples are split. Default sourcetype, allowed source and host
    """
    if output_dir is None:
        output_dir = os.path.dirname(sample_path)
    with open(sample_path, "r", encoding="utf-8") as sample_file:
        sample_raw = sample_file.read()
    samples = xmltodict.parse(sample_raw)
    events = samples["device"]["event"]
    events = events if type(events) == list else [events]
    separate_events = defaultdict(list)
    for each_event in events:
        if each_event.get("transport", {}).get(f"@{splitter}"):
            splitter_name = each_event["transport"].get(f"@{splitter}")
            separate_events[splitter_name].append(each_event)
        else:
            separate_events["undefined"].append(each_event)
    sample_file_name = os.path.basename(sample_path)
    for splitter_name, events in separate_events.items():
        samples["device"].update(event=events)
        output_file = sample_file_name.split(".")
        parsed_splitter_name = splitter_name.replace("/", "").replace("\\", "")
        output_file.insert(-1, parsed_splitter_name)
        output_file_name = ".".join(output_file)
        with open(
            os.path.join(output_dir, output_file_name), "w", encoding="utf-8"
        ) as output_file:
            xmltodict.unparse(samples, output=output_file, pretty=True, indent="  ")


def main():
    parser = argparse.ArgumentParser(
        description="Split events from xml file into separate files for each sourcetype"
    )
    parser.add_argument("file", help="xml file with samples to split")
    parser.add_argument(
        "-o", "--output_dir", default=None, help="output dir for new xmls"
    )
    parser.add_argument(
        "-s",
        "--splitter",
        default="sourcetype",
        help="splitter used to separate events",
    )
    args = parser.parse_args()
    sample_path = args.file
    output_dir = args.output_dir
    splitter = args.splitter
    split_samples(sample_path, output_dir, splitter)


if __name__ == "__main__":
    main()
