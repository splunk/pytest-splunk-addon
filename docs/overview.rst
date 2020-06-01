
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

1.2.0
""""""""""""""""""""""""""

    **New Features:**

    * Plugin now generates CIM compliance report for the add-ons, which provides insights to the user about the compatibility of the add-ons with the supported CIM data models.
    * Provided support of setup fixtures which can be used for making necessary configurations in the testing environment required for test execution. 
    * Optimisation of the SPL search query for faster execution of the test cases.
    * Added ``--search-index``, ``--search-retry``, ``--search-interval`` pytest arguments to provide custom values of Splunk index, retries and time interval respectively.

    **Bugfixes:**

    * Invalid search query generation for Malware Data Model is now fixed.

    **Known Issues:**

    * Fields for modular regular expressions are not extracted in the plugin.

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
