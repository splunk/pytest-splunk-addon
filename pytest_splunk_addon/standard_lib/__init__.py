# -*- coding: utf-8 -*-
"""
There are 2 types of tests included

1. Fields based test cases
2. CIM based test cases 

The test generation mechanism is divided into 3 types of class

1. Tests: Test templates
2. TestGenerator: Generates the test cases using pytest.params 
3. Other utility classes like Add-on parser & Data model handlers 

"""

from .app_test_generator import AppTestGenerator
from .addon_basic import Basic
