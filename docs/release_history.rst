.. _release_history:

=================
Release History
=================

**GitHub**

The best way to track the development of pytest-splunk-addon is through `the GitHub Repo <https://github.com/splunk/pytest-splunk-addon/>`_.

1.3.12 (2020-11-09)
""""""""""""""""""""""""""
    **Changes:**

    * Updated the documentation 
    * Added ``--ignore-addon-errors`` pytest arguments to suppress internal errors
    * Updated ``--no-splunk-cleanup`` to ``--splunk-cleanup`` pytest param so that you have to toggle the data cleanup on
    * Moved splunk_setup fixture from search_util to individual test case.
    * Updated waits for lookups to 60 secs

1.3.11 (2020-10-27)
""""""""""""""""""""""""""
    **Changes:**

    * Fixed string literal causing SyntaxError issues within Helmut Lib
    * Added a cleanup of events before testing, which can be toggled with a CLI param ``--no-splunk-cleanup``
    * Added ``--splunk-web-scheme`` pytest argument and updated our tests to utilize HTTPS
    * Updated Pytest-Splunk-Addon package to remove static fixtures that are now installed as part of the environment

1.3.9 (2020-10-15)
""""""""""""""""""""""""""
    **Changes:**

    * Updated the test environments to utilize Python Poetry to install requirements. 
    * Updated config.yml file to utilize poetry to install dependencies
    * Cleaned up some of the outdated environment requirements 
    * Updated Splunk_docker fixture to utilize poetry install 
    * Updated documentation for Pytest-Splunk-Addon 
    * Updated forwarder params for Pytest-Splunk-Addon, and added the pytest param ``is_responsive_hec``

1.3.6 (2020-9-25)
""""""""""""""""""""""""""
    **Changes:**

    * Added support for ingestion of data via Pytest-Splunk-Addon with a user-defined Index 
    * Fixed an issue with the Splunk rest_uri fixture in splunk.py


1.3.5 (2020-9-14)
""""""""""""""""""""""""""
    **Changes:**

    * Updated the host pattern from using ``_`` to using ``-``
    * Updated host generation logic to fix an issue for unique IP based hosts from being duplicated due to a limit. Now hosts are getting genreated uniquely.


1.3.4 (2020-9-11)
""""""""""""""""""""""""""
    **Changes:**

    * Fixed an issue when threading with Syslog in which we can run out of connections 

1.3.3 (2020-9-09)
""""""""""""""""""""""""""
    **Changes:**

    * Added a file lock when starting Docker 
    * Added log messages to our tests to help debug issues

1.3.2 (2020-8-26)
""""""""""""""""""""""""""
    **Changes:**

    * Enhanced requirements for the following CIM data models:

    +-----------------------+-----------------------------------------------------------+
    | CIM Data Model        |                   Field Name                              | 
    +=======================+===========================================================+
    | Change                | action, object_category, object_id, object_path,          |
    |                       | object_attrs                                              |
    +-----------------------+-----------------------------------------------------------+

    * Added tokenized events in logfiles 

1.3.1 (2020-8-24)
""""""""""""""""""""""""""
    **Changes:**

    * Now handles situations where TRANSFORMS REGEX uses _VAL
    * Pytest-Splunk-Addon now handles eval functions using NULL better 

1.3.0 (2020-8-21)
""""""""""""""""""""""""""
    **Features:**

    * Pytest-splunk-addon now generates data with it's own data generator feature which replaces SA-Eventgen for accuracy. This feature can ingest data using HEC event, HEC Raw, SC4S (TCP and UDP), and HEC metrics
    * pytest-splunk-addon now generates Index Time test cases for your Splunk Technology Add-ons. The plugin is now divided into 5 types of classes: Tests, TestGenerator, SampleGenerator, EventIngestor, and Utility classes. 
    * Added a utility to create a new pytest-splunk-addon-data.conf file from existing eventgen.conf files
    * Backward compatibility for search time tests using existing eventgen.conf
    * Added support of xdist for performance improvements
    * Added ``--thread-count`` pytest param to control the number of threads available for data ingestion

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

    * Event ingestion through SC4S via UDP port
    * File output for structured sources 
    * Support for filed values as host 
    * Validating lock mechanism in pytest-splunk-addon 
    * Fields for modular regular expressions are not extracted in the plugin.
    * Environment cleanup after running indextime tests for multiple local environment tests. 
    * Threading mechanism issue in Pytest-Splunk-Addon 

    **Other Changes:**

    * Intrusion Detection, Network Traffic, Network Resolution, and Web Data Models updated
    * Updated test addons within pytest-splunk-addon with new app.manifest files 


1.2.0 (2020-06-04)
""""""""""""""""""""""""""
    **Features:**

    * Plugin now generates CIM compliance report for the add-ons, which provides insights to the user about the compatibility of the add-ons with the supported CIM data models.
    * Provided support of setup fixtures which can be used for making necessary configurations in the testing environment required for test execution. 
    * Optimisation of the SPL search query for faster execution of the test cases.
    * Added ``--search-index``, ``--search-retry``, ``--search-interval`` pytest arguments to provide custom values of Splunk index, retries and time interval respectively.

    **Bugfixes:**

    * Invalid search query generation for Malware Data Model is now fixed.
    * Invalid search query for clustered fields in CIM testing 

    **Known Issues:**

    * Fields for modular regular expressions are not extracted in the plugin.

1.1.0 (2020-05-02)
""""""""""""""""""""""""""

    **Features:**

    * The codebase was reformatted to an object-oriented approach to increase the readability, scalability, and the reusability of the plugin. 
    * pytest-splunk-addon now generates tests for checking CIM compatibility in your Splunk Technology Add-ons.

    **Bugfixes:**

    * Test cases for fields starting with $ and _KEY are now not generated.
    * The plugin used to fail when test cases where executed parallelly with multiple processes using pytest-xdist. The issue has been fixed.

    **Known Issues:**

    * Invalid search query generation for Malware Data Model, which results in an HTTP 400 Bad Request error.

1.0.3 (2020-04-17)
""""""""""""""""""""""""""

    **Features:**

    * First Light.
    * pytest-splunk-addon generates tests for testing knowledge objects in Splunk Technology Add-ons.
