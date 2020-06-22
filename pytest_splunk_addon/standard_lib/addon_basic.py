# -*- coding: utf-8 -*-
"""
Base class for test cases. Provides test cases to verify
field extractions and CIM compatibility.
"""

from .fields_tests import FieldTestTemplates
from .cim_tests import CIMTestTemplates
from .index_tests import IndexTimeTestTemplate


class Basic(FieldTestTemplates, CIMTestTemplates, IndexTimeTestTemplate):
    """
    Base class for test cases. Inherit this class to include the test 
    cases for an Add-on. Only implement the common tests here, all the other 
    specific test case should be implemented in a TestTemplate class and Basic 
    should inherit it.
    """
    def test_one(self, splunk_ingest_data):
        pass

