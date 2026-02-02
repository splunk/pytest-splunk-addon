#
# Copyright 2026 Splunk Inc.
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


def get_ep_compatible_input_types():
    """
    Dynamically determine which input types are compatible with Splunk Edge Processor mode.
    
    Returns input types that use HECEventIngestor, which is the only ingestor that supports
    UUID via indexed fields parameter. This is required for EP mode because EP transforms
    events, making literal content matching unreliable.
    
    Note: This function is defined in utils.py (not ingestor_helper.py) to avoid circular imports.
    
    Returns:
        tuple: Input types that use HECEventIngestor (e.g., ("modinput", "windows_input"))
    """
    # Import here to avoid circular dependency
    from .event_ingestors.ingestor_helper import IngestorHelper
    
    return tuple(
        input_type 
        for input_type, ingestor_class in IngestorHelper.INGEST_METHODS.items() 
        if ingestor_class.__name__ == "HECEventIngestor"
    )
