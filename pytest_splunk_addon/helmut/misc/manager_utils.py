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
"""
@author: Nicklas Ansman-Giertz
@contact: U{ngiertz@splunk.com<mailto:ngiertz@splunk.com>}
@since: 2011-11-23
"""
from pytest_splunk_addon.helmut.exceptions import UnsupportedConnectorError


def create_wrapper_from_connector_mapping(base_class, connector, mappings):
    wrapper = get_wrapper_class_from_connector_mapping(connector, mappings)
    return super(base_class, base_class).__new__(wrapper)


def get_wrapper_class_from_connector_mapping(connector, mappings):
    cls = connector.__class__
    if cls not in mappings:
        raise UnsupportedConnectorError
    return mappings[cls]
