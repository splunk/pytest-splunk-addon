
Overview
=============
Pytest splunk addon is an open-source dynamic test tool for Splunk Apps and Add-ons which allows the user to test splunk addons for knowledge objects and  for CIM compatibility. 

Support
-------

**Platforms**: Linux, Windows and MacOS

**Python**: 3.7

Features
--------
* Generate tests for Splunk Knowledge objects in your Splunk Technology Add-ons.

* Generate tests for checking CIM compatibility in your Splunk Technology Add-ons.

* Validate your add-ons using Splunk + Docker. 

Release notes
-------------

1.1.0 (2020-05-02)
""""""""""""""""""""""""""

**New Features:**

* Codebase was reformatted to an object-oriented approach to increase the readability, scalability and the reusability of the tool. 
* Pytest-splunk-addon now generates tests for checking CIM compatibility in your Splunk Technology Add-ons.

**Bugfixes:**

* Test cases for fields starting with $ and _KEY are now not generated.

* The tool used to fail when test cases where executed parallely with multiple processes using pytest-xdist. The issue has been fixed.

**Known Issues:**

* Invalid search query generation for Malware Data Model, which results into a HTTP 400 Bad Request error. It will be fixed in the next release.




Installation
------------
pytest-splunk-addon can be installed via pip from PyPI:

.. code-block:: console
    
    pip install pytest-splunk-addon

Or, in any case if pip is unavailable:

.. code-block:: console
    
    1. Download the pytest-splunk-addon package from PyPI.
    2. Navigate into the directory containing setup.py
    3. python setup.py install
