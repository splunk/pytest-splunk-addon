# -*- coding: utf-8 -*-

from .fields_tests import FieldTests
from .cim_tests import CIMTests


class BaseTest(FieldTests, CIMTests):
    pass