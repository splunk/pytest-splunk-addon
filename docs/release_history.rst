.. _release_history:

=================
Release History
=================

**GitHub**

The best way to track the development of pytest-splunk-addon is through `the GitHub Repo <https://github.com/splunk/pytest-splunk-addon/>`_.

1.4.0
""""""""""""""""""""""""""
    **Changes:**

    * Plugin now generates and executes tests to validate savedsearches defined in savedsearches.conf.

    **Known Issues:**

    * Event ingestion through SC4S via UDP port
    * Fields for modular regular expressions are not extracted in the plugin.


1.3.15
""""""""""""""""""""""""""
    **Changes:**

    * Fixed issue that skipped generation of test cases for some field of REPORT.
    * Updated the default log level to INFO for the logs in **pytest_splunk_addon.log**
    * Enhanced requirements for the following CIM data models:

    +-----------------------+-----------------------------------------------------------+
    | CIM Data Model        |                   Field Name                              |
    +=======================+===========================================================+
    | Change                | Updated the search_constraints                            |
    +-----------------------+-----------------------------------------------------------+
    | Network Traffic       | dest_ip, dest_mac, src_ip, src_mac                        |
    |                       |                                                           |
    |                       | icmp_code, icmp_type, dest_zone, src_zone                 |
    |                       |                                                           |
    |                       | dest_translated_ip, src_translated_ip                     |
    +-----------------------+-----------------------------------------------------------+
    | Web                   | cookie, http_referrer, site                               |
    +-----------------------+-----------------------------------------------------------+

    **Known Issues:**

    * Event ingestion through SC4S via UDP port
    * Fields for modular regular expressions are not extracted in the plugin.


1.3.12 (2020-11-09)
""""""""""""""""""""""""""
    **Changes:**

    * Added ``--ignore-addon-errors`` pytest param to suppress Splunk Addon internal errors.
    * Updated ``--no-splunk-cleanup`` pytest param to ``--splunk-cleanup`` which is used to clean the data on the Splunk instance before testing.

    **Known Issues:**

    * Event ingestion through SC4S via UDP port
    * Fields for modular regular expressions are not extracted in the plugin.

1.3.11 (2020-10-27)
""""""""""""""""""""""""""
    **Changes:**

    * Fixed string literal causing SyntaxError within helmut lib.
    * Added ``--no-splunk-cleanup`` CLI param, which disables the cleanup of Splunk environment before the tests execute.
    * Added ``--splunk-web-scheme`` pytest argument which can be used to set the web scheme (http/https) of the Splunk instance.
    * Updated pytest-splunk-addon package to remove static fixtures that are now installed as part of the environment.

    **Known Issues:**

    * Event ingestion through SC4S via UDP port
    * Fields for modular regular expressions are not extracted in the plugin.

1.3.9 (2020-10-15)
""""""""""""""""""""""""""
    **Changes:**

    * Updated build process which uses python's poetry to install dependencies.
    * Added support in pytest-splunk-addon to test with on-prem forwarder configured to a standalone or SH of  cloud stack by providing SH in --splunk-host and forwarder in --splunk-forwarder-host and other appropriate params.

    **Known Issues:**

    * Event ingestion through SC4S via UDP port
    * Fields for modular regular expressions are not extracted in the plugin.

1.3.6 (2020-9-25)
""""""""""""""""""""""""""
    **Changes:**

    * Added support for ingestion of data via pytest-splunk-addon with a user-defined index ``index = <index_name>``.

    **Known Issues:**

    * Event ingestion through SC4S via UDP port
    * Fields for modular regular expressions are not extracted in the plugin.

1.3.5 (2020-9-14)
""""""""""""""""""""""""""
    **Changes:**

    * Updated the host pattern from using ``_`` to using ``-``.
    * Updated host generation logic to fix an issue for unique IP based hosts from being duplicated due to a limit. Now hosts are getting generated uniquely.

    **Known Issues:**

    * Event ingestion through SC4S via UDP port
    * Fields for modular regular expressions are not extracted in the plugin.


1.3.4 (2020-9-11)
""""""""""""""""""""""""""
    **Changes:**

    * Removed threading mechanism while sending data using SC4S as SC4S expects sequential ingestion of data rather than parallel ingestion.

    **Known Issues:**

    * Event ingestion through SC4S via UDP port
    * Fields for modular regular expressions are not extracted in the plugin.

1.3.3 (2020-9-09)
""""""""""""""""""""""""""
    **Changes:**

    * Added log messages to our tests to help debug issues.

    **Known Issues:**

    * Event ingestion through SC4S via UDP port
    * Fields for modular regular expressions are not extracted in the plugin.

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

    * Now, the tokenised events can be stored in json files in the *.tokenized_events* folder. If these files are not required, use the ``--discard-eventlogs`` option when executing the tests.

    **Known Issues:**

    * Event ingestion through SC4S via UDP port
    * Fields for modular regular expressions are not extracted in the plugin.

1.3.1 (2020-8-24)
""""""""""""""""""""""""""
    **Changes:**

    * Now handles situations where TRANSFORMS REGEX uses _VAL in transforms.conf.
    * pytest-splunk-addon now handles eval functions using NULL more efficiently.

    **Known Issues:**

    * Event ingestion through SC4S via UDP port
    * Fields for modular regular expressions are not extracted in the plugin.

1.3.0 (2020-8-21)
""""""""""""""""""""""""""
    **Features:**

    * pytest-splunk-addon now generates data with it's own data generator feature which replaces SA-Eventgen for accuracy. This feature can ingest data using HEC event, HEC Raw and SC4S (TCP).
    * pytest-splunk-addon now generates Index Time test cases for your Splunk Technology Add-ons.
    * Added a utility to create a new pytest-splunk-addon-data.conf file from existing eventgen.conf file.
    * Backward compatibility for search time tests using existing eventgen.conf.

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
    * Fields for modular regular expressions are not extracted in the plugin.

1.2.0 (2020-06-04)
""""""""""""""""""""""""""
    **Features:**

    * Plugin now generates CIM compliance report for the add-ons, which provides insights to the user about the compatibility of the add-ons with the supported CIM data models.
    * Provided support of setup fixtures which can be used for making necessary configurations in the testing environment required for test execution. 
    * Optimisation of the SPL search query for faster execution of the test cases.
    * Added ``--search-index``, ``--search-retry``, ``--search-interval`` pytest arguments to provide custom values of Splunk index, retries and time interval respectively.

    **Bugfixes:**

    * Invalid search query generation for Malware Data Model is now fixed.
    * Invalid search query for clustered fields in CIM testing.

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
