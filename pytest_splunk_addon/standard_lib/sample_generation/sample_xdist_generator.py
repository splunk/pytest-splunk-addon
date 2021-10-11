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
from . import SampleGenerator
import os
import pickle
from filelock import FileLock
import json
import pytest


class SampleXdistGenerator:
    def __init__(self, addon_path, config_path=None, process_count=4):
        self.addon_path = addon_path
        self.process_count = process_count
        self.config_path = config_path

    def get_samples(self, store_events):

        if self.tokenized_event_source == "pregenerated":
            with open(self.event_path, "rb") as file_obj:
                store_sample = pickle.load(file_obj)
                if store_events and (
                    "PYTEST_XDIST_WORKER" not in os.environ
                    or os.environ.get("PYTEST_XDIST_WORKER") == "gw0"
                ):
                    try:
                        tokenized_events = store_sample.get("tokenized_events")
                        self.store_events(tokenized_events)
                    except Exception as e:
                        pytest.exit(str(e))
                return store_sample

        if "PYTEST_XDIST_WORKER" in os.environ:
            file_path = os.environ.get("PYTEST_XDIST_TESTRUNUID") + "_events"
            with FileLock(str(file_path) + ".lock"):
                if os.path.exists(file_path):
                    with open(file_path, "rb") as file_obj:
                        store_sample = pickle.load(file_obj)
                else:
                    sample_generator = SampleGenerator(
                        self.addon_path, self.config_path
                    )
                    tokenized_events = list(sample_generator.get_samples())
                    store_sample = {
                        "conf_name": SampleGenerator.conf_name,
                        "tokenized_events": tokenized_events,
                    }
                    if store_events:
                        self.store_events(tokenized_events)
                    with open(file_path, "wb") as file_obj:
                        pickle.dump(store_sample, file_obj)
        else:
            sample_generator = SampleGenerator(self.addon_path, self.config_path)
            tokenized_events = list(sample_generator.get_samples())
            store_sample = {
                "conf_name": SampleGenerator.conf_name,
                "tokenized_events": tokenized_events,
            }
            if store_events:
                self.store_events(tokenized_events)
        if self.tokenized_event_source == "store_new" and not self.event_stored:
            with open(self.event_path, "wb") as file_obj:
                pickle.dump(store_sample, file_obj)
            self.event_stored = True
        return store_sample

    def store_events(self, tokenized_events):
        if not os.path.exists(os.path.join(os.getcwd(), ".tokenized_events")):
            os.makedirs(os.path.join(os.getcwd(), ".tokenized_events"))
        tokenized_samples_dict = {}
        for each_event in tokenized_events:
            if each_event.sample_name not in tokenized_samples_dict:
                if each_event.metadata.get("input_type") not in [
                    "modinput",
                    "windows_input",
                ]:
                    expected_count = int(
                        each_event.metadata.get("expected_event_count")
                    ) * int(each_event.metadata.get("sample_count"))
                else:
                    expected_count = each_event.metadata.get("expected_event_count")
                tokenized_samples_dict[each_event.sample_name] = {
                    "metadata": {
                        "host": each_event.metadata.get("host"),
                        "source": each_event.metadata.get("source"),
                        "sourcetype": each_event.metadata.get("sourcetype"),
                        "timestamp_type": each_event.metadata.get("timestamp_type"),
                        "input_type": each_event.metadata.get("input_type"),
                        "expected_event_count": expected_count,
                        "index": each_event.metadata.get("index", "main"),
                    },
                    "events": [
                        {
                            "event": each_event.event,
                            "key_fields": each_event.key_fields,
                            "time_values": each_event.time_values,
                        }
                    ],
                }
            else:
                tokenized_samples_dict[each_event.sample_name]["events"].append(
                    {
                        "event": each_event.event,
                        "key_fields": each_event.key_fields,
                        "time_values": each_event.time_values,
                    }
                )

        for sample_name, tokenized_sample in tokenized_samples_dict.items():
            with open(
                "{}.json".format(
                    os.path.join(os.getcwd(), ".tokenized_events", sample_name)
                ),
                "w",
            ) as eventfile:
                eventfile.write(
                    json.dumps({sample_name: tokenized_sample}, indent="\t")
                )
