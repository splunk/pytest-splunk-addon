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
# DEPRECATED: This module is kept for backward compatibility.
# Use ``from splunk_cim_models import datamodels`` instead.
import warnings as _warnings

_warnings.warn(
    "Importing datamodels from pytest_splunk_addon.CIM_Models.datamodel_definition "
    "is deprecated. Use 'from splunk_cim_models import datamodels' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from splunk_cim_models.datamodel_definition import datamodels  # noqa: F401, E402

__all__ = ["datamodels"]
