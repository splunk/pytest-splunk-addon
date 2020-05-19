# -*- coding: utf-8 -*-
"""
Base class for test cases. Provides test cases to verify
field extractions and CIM compatibility.
"""

from .fields_tests import FieldTestTemplates
from .cim_tests import CIMTestTemplates


class Basic(FieldTestTemplates, CIMTestTemplates):
    """
    Base class for test cases. Inherit this class to include the test 
    cases for an Add-on. Only implement the common tests here, all the other 
    specific test case should be implemented in a TestTemplate class and Basic 
    should inherit it.
    """
    pass
