Release History
=================

**GitHub**

The best way to track the development of pytest-splunk-addon is through `the GitHub Repo <https://github.com/splunk/pytest-splunk-addon/>`_.

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
