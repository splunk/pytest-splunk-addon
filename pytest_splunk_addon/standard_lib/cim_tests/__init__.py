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
# -*- coding: utf-8 -*-
"""
Test generation mechanism to verify the CIM compatibility of an Add-on 
"""

from .json_schema import JSONSchema
from .data_set import DataSet
from .data_model import DataModel
from .data_model_handler import DataModelHandler
from .test_generator import CIMTestGenerator
from .test_templates import CIMTestTemplates
from .field_test_helper import FieldTestHelper
