
Overview
=============
pytest-splunk-addon is an open-source dynamic test plugin for Splunk Apps and Add-ons which allows the user to test knowledge objects and CIM compatibility. 

Support
-------

* **Python**: 3.7
* **Platforms**: Linux, Windows and MacOS

Features
--------
* Generate tests for Splunk Knowledge objects in Splunk Technology Add-ons.

* Generate tests for checking CIM compatibility in Splunk Technology Add-ons.

* Validate your add-ons using Splunk + Docker. 

Release notes
-------------

1.1.0 (2020-05-02)
""""""""""""""""""""""""""

    **New Features:**

    * The codebase was reformatted to an object-oriented approach to increase the readability, scalability and the reusability of the plugin. 
    * pytest-splunk-addon now generates tests for checking CIM compatibility in your Splunk Technology Add-ons.

    **Bugfixes:**

    * Test cases for fields starting with $ and _KEY are now not generated.

    * The plugin used to fail when test cases where executed parallelly with multiple processes using pytest-xdist. The issue has been fixed.

    **Known Issues:**

    * Invalid search query generation for Malware Data Model, which results in an HTTP 400 Bad Request error.

Installation
------------
pytest-splunk-addon can be installed via pip from PyPI:

.. code-block:: console
    
    pip3 install pytest-splunk-addon

Or, in any case, if pip is unavailable:

.. code-block:: console
    
    1. git clone https://github.com/splunk/pytest-splunk-addon.git
    2. cd pytest-splunk-addon
    3. python3 setup.py install
