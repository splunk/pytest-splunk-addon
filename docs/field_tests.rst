Fields Extraction Tests
=======================

Overview
-------------------

* The field tests are written with a purpose of testing the proper functioning of the search-time knowledge objects of the add-on.
* Search-time knowledge objects are extracted/generated when a search query is executed on a Splunk Instance.
* The search-time knowledge objects include the following:

    1. Extract
    2. Report
    3. Lookups
    4. Fieldalias
    5. Eval
    6. Eventtypes
    7. Tags

Test Scenarios
--------------

**1. Events should be present in source/sourcetype defined in props.conf stanza.**

    .. code-block:: python

        test_props_fields[<stanza>]

    Here <stanza> is the source/sourcetype that is defined in the stanza.
    
    | Testcase verifies if the defined source/sourcetype has events or not.

    **Workflow:**

    * Plugin get the list of defined sourcetypes by parsing props.conf
    * For each sourcetype plugin generates a SPL search query and asserts event_count > 0.

**2. Fields mentioned under source/sourcetype should be extracted**

    .. code-block:: python

        test_props_fields[<stanza>::field::<fieldname>]

    Here <stanza> is the source/sourcetype that is defined in the stanza and <fieldname> is name of field which is extracted under source/sourcetype.

    **Workflow:**

    * Plugin generates a list of fields extracted under the source/sourcetype by parsing the knowledge objects like Extract, Eval, Fieldalias etc.
    * For each field plugin generates a SPL search query and asserts event_count > 0.

**3. Negative scenarios for field values**

    .. code-block:: python

        test_props_fields_no_dash_not_empty[<stanza>::field::<fieldname>]

    **Workflow:**

    * A search query to check if the field has invalid values like [" ", "-", "null", "(null)", "unknown"].
    * Plugin generates a SPL search query for each field collected in above scenario which checks for invalid values and asserts event_count == 0.

**4. All the fields mentioned in an EXTRACT, REPORT, LOOKUP should be extracted in a single event.**

    .. code-block:: python

        test_props_fields[<stanza>::EXTRACT-<classname>]
        test_props_fields[<stanza>::LOOKUP-<classname>]
        test_props_fields[<stanza>::REPORT-<classname>::<transforms_stanza>]

    **Workflow:** 

    * While parsing the conf file when plugin finds one of these EXTRACT, REPORT, LOOKUP it gets the list of fields extracted in the knowledge object and generates a testcase.
    * While parsing REPORT for each transforms stanza fields are collected for the stanza and a grouped testcase is generated.
    * For all the fields in the testcase it generates a single SPL search query including the stanza and asserts event_count > 0.
    * This verifies that all the fields are extracted IN the same event

**5. Events should be present in each eventtype**

    .. code-block:: python

        test_eventtype[eventtype=<eventtype>]

    **Workflow:** 

    * For each eventtype mentioned in eventtypes.conf plugin generates an SPL search query and asserts event_count > 0 for the eventtype.

**6. Tags defined in tags.conf should be applied to the events.**

    .. code-block:: python

        test_tags[<tag_stanza>::tag::<tag>]

    **Workflow:** 

    * In tags.conf for each tag defined in the stanza plugin generates a testcase.
    * For each tag plugin generates a search query including the stanza and the tag and asserts event_count > 0

Testcase Troubleshooting
------------------------

In case of test case failure check if:

    - addon to be tested is installed on the splunk instance.
    - data is generated sufficiently for the addon being tested.
    - splunk licence has not expired.
    - splunk instance is up and running.
    - splunk instance's management port is accessible from test machine.

If all the above conditions are satisfied, further analysis on the test is required.
For every CIM validation test case there is a defined structure for the stacktrace [1]_.

    .. code-block:: text

        AssertionError: <<error_message>>
            Search =  <Query>

    Get the search query from the stacktrace and execute it on the splunk instance and verify which specific type of events are causing failure.

.. raw:: html

   <hr width=100%>

.. [1] Stacktrace is the text displayed in the Exception block when the Test fails.
