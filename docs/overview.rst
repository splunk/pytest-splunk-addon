
Overview
=============
pytest-splunk-addon is an open-source dynamic test plugin for Splunk Apps and Add-ons 
which allows the user to test knowledge objects, CIM compatibility and index time properties. 

Support
-------

* **Python**: 3.7
* **Platforms**: Linux, Windows and MacOS

Features
--------
* Generate tests for Splunk Knowledge objects in Splunk Technology Add-ons.

* Generate tests for checking CIM compatibility in Splunk Technology Add-ons.

* Generate tests for checking Splunk index-time properties in Splunk Technology Add-ons. 

* Validate your add-ons using Splunk + Docker. 

Release notes
-------------

:ref:`Release History Page<release_history>`

Installation
------------
pytest-splunk-addon can be installed via pip from PyPI:

.. code-block:: console
    
    pip3 install pytest-splunk-addon

Or, in any case, if pip is unavailable:

.. code-block:: console
    
    1. git clone https://github.com/splunk/pytest-splunk-addon.git
    2. cd pytest-splunk-addon
    3. poetry install
