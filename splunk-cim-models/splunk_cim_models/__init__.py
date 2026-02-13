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
"""
Splunk CIM (Common Information Model) data model definitions and schemas.

This package provides:
- ``datamodels``: A dict mapping CIM versions to per-model recommended field lists.
- ``DATA_MODELS_PATH``: Filesystem path to the directory of data model JSON files.
- ``COMMON_FIELDS_PATH``: Filesystem path to CommonFields.json.
- ``DATAMODEL_SCHEMA_PATH``: Filesystem path to DatamodelSchema.json.
"""
import os

from .datamodel_definition import datamodels  # noqa: F401

_PKG_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_MODELS_PATH = os.path.join(_PKG_DIR, "data_models")
COMMON_FIELDS_PATH = os.path.join(_PKG_DIR, "CommonFields.json")
DATAMODEL_SCHEMA_PATH = os.path.join(_PKG_DIR, "DatamodelSchema.json")
