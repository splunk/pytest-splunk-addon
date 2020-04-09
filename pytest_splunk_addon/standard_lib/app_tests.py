# -*- coding: utf-8 -*-
"""
Base class for test cases. Provides test cases to verify
field extractions and CIM compatibility.
"""

from .fields_tests import FieldTests
from .cim_tests import CIMTests


class BaseTest(FieldTests, CIMTests):
    """
    Base class for test cases. Inherit this class to include the test 
cases for an Add-on.
    """
    pass