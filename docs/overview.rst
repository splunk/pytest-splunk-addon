
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

1.3.0
""""""""""""""""""""""""""

    **New Features:**

    * Removed dependency on SA-Eventgen to generate data for testing.
    * pytest-splunk-addon now generates data independently, which is required for testing.
    * pytest-splunk-addon generates tests for testing index-time properties in Splunk Technology Add-ons.

    **Bugfixes:**

    * Enhanced requirements for the following CIM data models:

    +-----------------------+-----------------------------------------------------------+
    | CIM Data Model        |                   Field Name                              | 
    +=======================+===========================================================+
    | IDS                   | src, dest, src_port, dest_port, user                      |
    +-----------------------+-----------------------------------------------------------+
    | Network Resolution    | src, dest                                                 |
    +-----------------------+-----------------------------------------------------------+
    | Network Traffic       | bytes, bytes_in, bytes_out, icmp_code                     |
    |                       |                                                           |
    |                       | packets, packets_in, packets_out                          |
    |                       |                                                           |    
    |                       | src, src_translated_port, src_port                        |
    |                       |                                                           |
    |                       | dest, dest_translated_port, dest_port                     |
    +-----------------------+-----------------------------------------------------------+
    | Web                   | app, uri_path, url_length                                 |
    +-----------------------+-----------------------------------------------------------+

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
