# -*- coding: utf-8 -*-
"""
There are 3 types of tests included:

1. Knowledge objects test cases
2. CIM Compatibility test cases
3. Index Time test cases


The test generation mechanism is divided into 3 types of class

1. Tests: Test templates
2. TestGenerator: Generates the test cases using pytest.params
3. SampleGenerator: Generates the data for which the test cases will be executed.
4. EventIngestor: Ingests the generated data to Splunk.
5. Other utility classes like Add-on parser & Data model handlers.

"""

from .app_test_generator import AppTestGenerator
from .addon_basic import Basic
