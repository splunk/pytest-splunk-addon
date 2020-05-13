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

Testcase Generation
-------------------

This are the list of conf files parsed by this tool in order to generate the test cases for knowledge objects

* props.conf

* transforms.conf

* tags.conf

* eventtypes.conf
  
Test cases for the following types of field extractions are supported :

* EVAL

* EXTRACT

* FIELDALIAS

* LOOKUP 

* REPORT 

For every field extraction there are two two test cases:

* Positive-To check whether field is extracted and it is not dash or empty

* Negative-To check whether field is dash or empty

To generate test cases only for knowledge objects than user can appened following markers to pytest command as per need:

.. code-block:: console

    -m  splunk_searchtime_fields           


Testcase Format
---------------

1. **test_props_fields[<sourcetype>]**

Here <sourcetype> is the sourcetype that is defined in the stanza in props.conf


2. **test_props_fields[<sourcetype>::<classname>]**

This type of test case will combine all the fields mentioned in the classname to verify all the fields are extracted in the same events using the mentioned extractions.

For the following classname, grouped test case will be generated

* REPORT

* EXTRACT

* LOOKUP

3. **test_props_fields_positive[<sourcetype>::field::<fieldname>]**

Here <sourcetype> is the sourcetype that is defined in the stanza and <fieldname> is name of field which is extracted under <sourcetype>

4. **test_tags[eventtype=<eventtype>::tag::<tag>]**

Here <eventtype> is eventtype that is taged using <tag> mentioned in tags.conf 

5. **test_eventtype[eventtype=<eventtype>]**

Here <eventtype> is eventtype mentioned in eventtypes.conf 


Testcase Troubleshooting
------------------------

If the test case fails than user can check the search query that is generated for testing the field extraction.

User can verify using the following steps

    1. Check whether the data for that sourcetype is getting generated or not.
 
    2. Check in the config file to verify whether extraction for fields are valid or not.

    3. Check the query on splunk ui in which the add-on is installed and verify whether the field is extracted or not.

