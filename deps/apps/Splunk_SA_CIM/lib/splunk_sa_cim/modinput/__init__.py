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
    "FieldValidationException"
]
