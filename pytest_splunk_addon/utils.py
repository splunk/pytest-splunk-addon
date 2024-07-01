#
# Copyright 2024 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os


def check_first_worker() -> bool:
    """
    returns True if the current execution is under gw0 (first worker)
    """
    return (
        "PYTEST_XDIST_WORKER" not in os.environ
        or os.environ.get("PYTEST_XDIST_WORKER") == "gw0"
    )
