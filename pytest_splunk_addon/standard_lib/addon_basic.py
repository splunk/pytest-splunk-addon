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
        cases for an Add-on.
    """
    pass
