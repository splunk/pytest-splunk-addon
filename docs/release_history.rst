Release History
=================

**GitHub**

The best way to track the development of pytest-splunk-addon is through `the GitHub Repo <https://github.com/splunk/pytest-splunk-addon/>`_.

1.2.0 (2020-06-04)
""""""""""""""""""""""""""
    **Features:**

    * Plugin now generates CIM compliance report for the add-ons, which provides insights to the user about the compatibility of the add-ons with the supported CIM data models.
    * Provided support of setup fixtures which can be used for making necessary configurations in the testing environment required for test execution. 
    * Optimisation of the SPL search query for faster execution of the test cases.
    * Added ``--search-index``, ``--search-retry``, ``--search-interval`` pytest arguments to provide custom values of Splunk index, retries and time interval respectively.

    **Bugfixes:**

    * Invalid search query generation for Malware Data Model is now fixed.

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
