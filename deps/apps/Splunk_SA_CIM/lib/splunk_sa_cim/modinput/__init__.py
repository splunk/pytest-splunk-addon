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

"""
Copyright (C) 2005 - 2019 Splunk Inc. All Rights Reserved.
"""
from .base_modinput import logger
from .xml_modinput import XmlModularInput
from .json_modinput import JsonModularInput
from .fields import Field
from .fields import BooleanField
from .fields import DelimitedField
from .fields import DurationField
from .fields import FloatField
from .fields import IntegerField
from .fields import IntervalField
from .fields import JsonField
from .fields import ListField
from .fields import RangeField
from .fields import RegexField
from .fields import SeverityField
from .fields import FieldValidationException

ModularInput = XmlModularInput
__all__ = [
    "logger",
    "ModularInput",
    "XmlModularInput",
    "JsonModularInput",
    "Field",
    "BooleanField",
    "DelimitedField",
    "DurationField",
    "FloatField",
    "IntegerField",
    "IntervalField",
    "JsonField",
    "ListField",
    "RangeField",
    "RegexField",
    "SeverityField",
    "FieldValidationException",
]
