# -*- coding: utf-8 -*-
"""
There are 2 types of tests included

1. Fields based test cases
2. CIM based test cases 

The test generation mechanism is divided into 3 types of class

1. Tests: Test templates
2. TestGenerator: Generates the test cases using pytest.params 
3. Other utility classes like Add-on parser & Data model handlers 

General modules/packaged used across the package 

1. app_tests
2. app_test_generator
3. addon_parser

To test the Field extractions, the following modules of fields_tests package are utilized 

1. fields_tests
2. fields_test_generator
3. field_bank

To test the CIM compatibility, the following modules of cim_tests package are utilized 

1. cim_tests
2. cim_test_generator
3. data_model_handler
4. data_model
5. data_set

"""

from .app_test_generator import AppTestGenerator
from .addon_basic import Basic
