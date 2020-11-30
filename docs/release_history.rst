Release History
=================

**GitHub**

The best way to track the development of pytest-splunk-addon is through `the GitHub Repo <https://github.com/splunk/pytest-splunk-addon/>`_.

1.3.12 (2020-11-09)
""""""""""""""""""""""""""
    **Changes:**

    * Updated the documentation 
    * Updated pytest params (added --ignore-addon-errors, and updated --no-splunk-cleanup to --splunk-cleanup so that you have to toggle the cleanup on)
    * Updated splunk_setup 
    * Updated waits for lookups

1.3.11 (2020-10-27)
""""""""""""""""""""""""""
    **Changes:**

    * Fixed string literal causing SyntaxError issues within Helmut Lib
    * Added a cleanup of events before testing, which can be toggled with a CLI param (--no-splunk-cleanup)

1.3.10 (2020-10-16)
""""""""""""""""""""""""""
    **Changes:**

    * Added pytest-splunk-addon params (--splunk-web-scheme) and updated our tests to utilize HTTPS

1.3.9 (2020-10-15)
""""""""""""""""""""""""""
    **Changes:**

    * Updated config.yml file
    * Cleanup outdated environment requirements 

1.3.8 (2020-10-15)
""""""""""""""""""""""""""
    **Changes:**

    * Updated requirements for Poetry install and CircleCI test environment

1.3.7 (2020-10-14)
""""""""""""""""""""""""""
    **Changes:**

    * Changes to params related to external forwarder 
    * Updated Splunk_docker fixture 
    * Updated documentation for Pytest-Splunk-Addon 
    * Updated forwarder params for Pytest-Splunk-Addon (Added param "is_responsive")
    * Updated the test environments to utilize Python Poetry to install requirements. 

1.3.6 (2020-9-24)
""""""""""""""""""""""""""
    **Changes:**

    * Added support for ingestion of data via Pytest-Splunk-Addon with a user defined Index 
    * Fixed Splunk rest_uri fixture in splunk.py


1.3.5 (2020-9-14)
""""""""""""""""""""""""""
    **Changes:**

    * Updated the host pattern
    * Updated host generation logic 


1.3.4 (2020-9-11)
""""""""""""""""""""""""""
    **Changes:**

    * Fixed an issue of when threading with syslog we can run out of connections 

1.3.3 (2020-9-04)
""""""""""""""""""""""""""
    **Changes:**

    * Added a file lock when starting Docker 
    * Added log messages to our tests

1.3.2 (2020-8-25)
""""""""""""""""""""""""""
    **Changes:**

    * CIM requirements change (Updates to action and object fields)
    * Added tokenized events in logfiles 

1.3.1 (2020-8-23)
""""""""""""""""""""""""""
    **Changes:**

    * Now handles situations where TRANSFORMS REGEX uses _VAL
    * Handles eval functions using NULL better 

1.3.0 (2020-8-21)
""""""""""""""""""""""""""
    **Features:**

    * pytest-splunk-addon now generates data with it's own data generator feature which replaces eventgen for accuracy. This feature can ingest data using HEC event, HEC Raw, SC4S (TCP and UDP), and HEC metrics
    * pytest-splunk-addon now generates Index Time test cases for your Splunk Technology Add-ons. The plugin is now divided into 5 types of classes: Tests, TestGenerator, SampleGenerator, EventIngestor, and Utility classes. 
    * Added a utility to create a new pytest-splunk-addon-data.conf file from existing eventgen.conf files
    * Backward compatibility for search time tests using existing eventgen.conf
    * Support of xdist for performance improvements
    * CircleCI and Jenkins Integration for Indextime Tests
    * Added --thread-count param to control the number of threads available for data ingestion

    **Bugfixes:**

    * Corrected incorrect requirements for CIM fields

    **Known Issues:**

    * Event ingestion through SC4S bia UDP port
    * File ouput for structured sources 
    * Support for filed values as host 
    * Validatibng lock mechanism in pytest-splunk-addon 
    * Timeout failures in CircleCI 
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

    * The codebase was reformatted to an object-oriented approach to increase the readability, scalability and the reusability of the plugin. 
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
