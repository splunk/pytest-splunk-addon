# -*- coding: utf-8 -*-
"""
Includes the test scenarios to check the CIM compatibility of an Add-on.
"""

import logging

class CIMTests:
    """
    Test scenarios to check the CIM compatibility of an Add-on 
    Supported Test scenarios:
        - The eventtype should exctract all required fields of data model 
        - One eventtype should not be mapped with more than one data model 
        - TODO 
    """
    logger = logging.getLogger()


    def test_cim_fields(self):
        # Search query
        pass 

    def test_cim_only_one_model(self):
        # List the data models mapped for a tags.conf stanza 
        # Fail if it has more than one mapped. 
        pass
