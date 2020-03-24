.. pytest-splunk-addon documentation master file, created by
   sphinx-quickstart on Tue Mar 24 12:52:03 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to pytest-splunk-addon's documentation!
===============================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:


About test cases
-----------------

* "test_common_<testcase>" - test cases that are not specific to a specific configuration element
* "test_<conf>_<testcase>" - Configuration dependent test cases

.. csv-table:: a title
   :header: "class", "testcase", "description"
   :widths: 15, 14, 40

   "Basic", "test_common_internal_errors", "Check Splunk's internal index for errors"
   "Basic", "test_props_sourcetype", "Verify source type is present in the even stream"
   "Basic", "test_props_sourcetype_fields", "Verify each specific field is generated"
   "Basic", "test_props_sourcetype_fields_no_dash", "Verify a field does not have a - value"
   "Basic", "test_props_sourcetype_fields_no_empty", "Verify a field is not extracted as empty" 


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
