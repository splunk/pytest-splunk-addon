# CIM Compatibility Tests

## Overview

The CIM tests are written with a purpose of testing the compatibility of the add-on with CIM Data Models (Based on Splunk_SA_CIM 4.15.0).
An add-on is said to be CIM compatible if it fulfils the following two criteria:

1. The add-on extracts all the fields with valid values, which are marked as required by the [Data Model Definitions](https://github.com/splunk/pytest-splunk-addon/tree/main/pytest_splunk_addon/standard_lib/data_models).
2. Any event for the add-on is not mapped with more than one data model.

______________________________________________________________________

To generate test cases only for CIM compatibility, append the following marker to pytest command:

 ```console
 -m  splunk_searchtime_cim
 ```

## Test Scenarios


**1. Testcase for each eventtype mapped with a dataset.**

 ```python
 test_cim_required_fields[<tags_stanza>::<dataset>]
 ```

 Testcase verifies if an eventtype is mapped with the dataset, events must follow the search constraints of the dataset.

 **Workflow:**

 - Plugin parses tags.conf to get a list of tags for each eventtype.
 - Plugin parses all the [supported datamodels](https://github.com/splunk/pytest-splunk-addon/tree/main/pytest_splunk_addon/standard_lib/data_models).
 - Then it gets a list of the datasets mapped with an eventtype.
 - Generates test case for each eventtype.

**2. Testcases for all required, conditional and cluster fields in dataset.**

 ```python
 test_cim_required_fields[<tags_stanza>::<dataset>::<field_name>]
 ```


#### Testcase Assertions:

 - There should be at least 1 event mapped with the dataset.
 - Each required field should be extracted in all the events mapped with the datasets.
 - Each conditional fields should be extracted in all the events filtered by the condition.
 - If there are interdependent fields, either all fields should be extracted or none of them should be extracted *i.e \["bytes","bytes_in","bytes_out"\].*
 - Fields should not have values other than the expected values defined in field properties.
 - Fields must not have invalid values \[" ", "-", "null", "(null)", "unknown"\].

 **Workflow:**

 - For an eventtype, mapped dataset will be identified as mentioned in [#2 scenario](cim_tests.md#test-scenarios).

 - Test case will be generated for each required fields of a dataset.

 - To generate the test case the following properties of fields will be considered :

    - An filtering condition to filter the events, only for which the field should be verified.
    - Expected values
    - Validation to check the values follows a proper type.
    - List of co-related fields.

 - Generate the query according to the properties of the field mentioned above.

 - Search the query to the Splunk instance.

 - Assert the assertions mentioned in [Testcase assertions](cim_tests.md#testcase-assertions).

**3. Testcase for all not_allowed_in_search fields**

 ```python
 test_cim_fields_not_allowed_in_search[<tags_stanza>::<dataset>]
 ```

 These fields are not allowed to be extracted for the eventtype

 **Workflow:**

 - Plugin collects the list of not_allowed_in_search fields from mapped datasets and [CommonFields.json](https://github.com/splunk/pytest-splunk-addon/blob/main/pytest_splunk_addon/standard_lib/cim_tests/CommonFields.json).
 - Using search query the test case verifies if not_allowed_in_search fields are populated in search or not.

> **_NOTE:_** 
 [CommonFields.json](https://github.com/splunk/pytest-splunk-addon/blob/main/pytest_splunk_addon/standard_lib/cim_tests/CommonFields.json) contains fields which are automatically provided by asset and identity correlation features of applications like Splunk Enterprise Security.


**4. Testcase for all not_allowed_in_props fields**

 ```python
 test_cim_fields_not_allowed_in_props[searchtime_cim_fields]
 ```

 Defining extractions in the configuration files is not allowed for these fields. But if these fields are automatically extracted by Splunk, that's fine *i.e tag*

 **Workflow:**

 - Plugin gets a list of fields of type not_allowed_in_props from CommonFields.json and mapped datasets.
 - Plugin gets a list of fields whose extractions are defined in props using addon_parser.
 - By comparing we obtain a list of fields whose extractions are not allowed but defined.

**5. Testcase to check that eventtype is not be mapped with multiple datamodels.**


 **Workflow:**

 - Parsing tags.conf it already has a list of eventtype mapped with the datasets.
 - Using SPL we check that each eventtype is not be mapped with multiple datamodels.

## Testcase Troubleshooting

In case of test case failure check if:

- The add-on to be tested is installed on the Splunk instance.
- Data is generated sufficiently for the addon being tested.
- Splunk licence has not expired.
- Splunk instance is up and running.
- Splunk instance's management port is accessible from the test machine.

If all the above conditions are satisfied, further analysis of the test is required.
For every CIM validation test case there is a defined structure for the stack trace.

 ```text
 AssertionError: <<error_message>>
     Source   | Sourcetype      | Field | Event Count | Field Count | Invalid Field Count | Invalid Values
     -------- | --------------- | ------| ----------- | ----------- | ------------------- | --------------
       str    |       str       |  str  |     int     |     int     |         int         |       str

     Search =  <Query>

     Properties for the field :: <field_name>
     type= Required/Conditional
     condition= Condition for field
     validity= EVAL conditions
     expected_values=[list of expected values]
     negative_values=[list of negative values]
 ```

 Get the search query from the stack trace and execute it on the Splunk instance and verify which specific type of events are causing failure.

 If a field validating test case is failing, check the field's properties from the table provided for the reason of failure.
