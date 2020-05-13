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

**1. Testing if data is present in source/sourcetype defined in props.conf stanza.**

Testcase: 

.. code-block:: python

    test_props_fields[<stanza>]

Here <stanza> is the source/sourcetype that is defined in the stanza.
| Testcase verifies if the defined source/sourcetype has events or not.

Workflow:

* Plugin get the list of defined sourcetypes by parsing props.conf
* For each sourcetype plugin generates a SPL search query and asserts event_count > 0.

**2. Testing fields extracted under source/sourcetype**

Testcase: 

.. code-block:: python

    test_props_fields[<stanza>::field::<fieldname>]

Here <stanza> is the source/sourcetype that is defined in the stanza and <fieldname> is name of field which is extracted under source/sourcetype.

Workflow:

* Plugin generates a list of fields extracted under the source/sourcetype by parsing the knowledge objects like Extract, Eval, Fieldalias etc.
* For each field plugin generates a SPL search query and asserts event_count > 0.

**3. All the fields mentioned in an EXTRACT, REPORT, LOOKUP must be extracted from a single event.**

Testcase:

.. code-block:: python

    test_props_fields[<stanza>::EXTRACT-<classname>]
    test_props_fields[<stanza>::LOOKUP-<classname>]
    test_props_fields[<stanza>::REPORT-<classname>::<transforms_stanza>]

Workflow: 

* While parsing the conf file when plugin finds one of these EXTRACT, REPORT, LOOKUP it gets the list of fields extracted in the knowledge object and generates a testcase.
* While parsing REPORT for each transforms stanza fields are collected for the stanza and a grouped testcase is generated.
* For all the fields in the testcase it generates a single SPL search query including the stanza and asserts event_count > 0.
* This verifies that all the fields are extracted IN the same event

**4. Testing if data is present in each eventtype**

Testcase:

.. code-block:: python

    test_eventtype[eventtype=<eventtype>]

Workflow: 

* For each eventtype mentioned in eventtypes.conf plugin generates an SPL search query and asserts event_count > 0 for the eventtype.



**5. Testing if tags defined in tags.conf are applied to the event.**

Testcase:

.. code-block:: python

    test_tags[<tag_stanza>::tag::<tag>]

Workflow: 

* In tags.conf for each tag defined in the stanza plugin generates a testcase.
* For each tag plugin generates a search query including the stanza and the tag and asserts event_count > 0
