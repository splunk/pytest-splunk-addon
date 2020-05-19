CIM Compatibility Tests
=======================

Overview
-------------------

The CIM tests are written with a purpose of testing the compatibility of the add-on with CIM Data Models.
An add-on is said to be CIM compatible, if it fulfils the two following criteria:

1. The add-on extracts all the fields with valid values, which are marked as required by the CIM Data Model.
2. Any event for the add-on is not mapped with more than one data model.

---------------------

To generate test cases only for CIM compatibility, append the following marker to pytest command:

    .. code-block:: console

        -m  splunk_searchtime_cim

Test Scenarios
--------------

**1. Add-on Splunk_SA_CIM should be installed on the given splunk instance**

    .. code-block:: python

        test_app_installed[Splunk_SA_CIM]

    Splunk_SA_CIM add-on should be installed on the Splunk instance to test the other scenarios. 

.. _mapped_datasets:

**2. Testcase for each eventtype mapped with a dataset.**

    .. code-block:: python

        test_cim_required_fields[eventtype=<eventtype>::<dataset>]

    Testcase verifies if an eventtype is mapped with the dataset, events must follow the search constrainsts of the dataset.

    **Workflow:**

    * Plugin parses tags.conf to get a list of tags for each eventtype.
    * Plugin parses all the `supported datamodels <https://github.com/splunk/pytest-splunk-addon/tree/master/pytest_splunk_addon/standard_lib/data_models>`_.
    * Then it gets a list of the datasets mapped with an eventtype.
    * Generates testcase for each eventtype.

**3. Testcases for all required, conditional and cluster fields in dataset.**

    .. code-block:: python

        test_cim_required_fields[eventtype=<eventtype>::<dataset>::<field_name>]

    .. _test_assertions:

    Testcase assertions:

    * There should be at least 1 event mapped with the dataset.
    * Each required field should be extracted in all the events mapped with the datasets.
    * Each conditional fields should be extracted in all the events filtered by the condition.
    * If there are inter dependent fields, either all fields should be extracted or none of them should be extracted *i.e ["bytes","bytes_in","bytes_out"].*
    * Fields should not have values other than the expected values defined in field properties.
    * Fields must not have invalid values [" ", "-", "null", "(null)", "unknown"].

    **Workflow:**

    * For an eventtype, mapped dataset will be identified as mentioned in :ref:`#2 scenario<mapped_datasets>`.
    * Test case will be generated for each required fields of an dataset.
    * To generate the test case the following properties of fields will be considered :

        * An filtering condition to filter the events, only for which the field should be verified.
        * Expected values 
        * Validation to check the values follows a proper type.
        * List of co-related fields.
    * Generate the query according to the properties of the field mentioned above.  
    * Search the query to the Splunk instance.
    * Assert the assertions mentioned in :ref:`Testcase assertions<test_assertions>`.


**4. Testcase for all not_allowed_in_search fields**

    .. code-block:: python

        test_cim_fields_not_allowed_in_search[eventtype=<eventtype>::<dataset>]

    These fields are not allowed to be extracted for the eventtype

    **Workflow:**

    * Plugin collects the list of not_allowed_in_search fields from mapped datasets and `CommonFields.json <https://github.com/splunk/pytest-splunk-addon/blob/master/pytest_splunk_addon/standard_lib/cim_tests/CommonFields.json>`_.
    * Using search query the testcase verifies if not_allowed_in_search fields are populated in search or not.

    .. note::
      `CommonFields.json <https://github.com/splunk/pytest-splunk-addon/blob/master/pytest_splunk_addon/standard_lib/cim_tests/CommonFields.json>`_ contains fields which are are automatically provided by asset and identity correlation features of applications like Splunk Enterprise Security.

**5. Testcase for all not_allowed_in_props fields**

    .. code-block:: python

        test_cim_fields_not_allowed_in_props[searchtime_cim_fields]

    Defining extractions in the configuration files is not allowed for these fields. But if these fields are automatically extracted by Splunk thats fine *i.e tag*
    
    **Workflow:**

    * Plugin gets a list of fields of type not_allowed_in_props from CommonFields.json and mapped datasets.
    * Plugin gets a list of fields whose extractions are defined in props using addon_parser.
    * By comparing we obtain a list of fields whose extractions are not allowed but defined.

**6. Testcase to check that eventtype is not be mapped with multiple datamodels.**

    .. code-block:: python

        test_eventtype_mapped_multiple_cim_datamodel
    
    **Workflow:**

    * Parsing tags.conf it already has a list of eventtype mapped with the datasets.
    * Using SPL we check that each eventtype is not be mapped with multiple datamodels.

Testcase Troubleshooting
------------------------

In case of test case failure check if:

    - The add-on to be tested is installed on the splunk instance.
    - Data is generated sufficiently for the addon being tested.
    - Splunk_SA_CIM is installed on the Splunk instance.
    - The splunk licence has not expired.
    - The splunk instance is up and running.
    - The splunk instance's management port is accessible from test machine.

If all the above conditions are satisfied, further analysis on the test is required.
For every CIM validation test case there is a defined structure for the stacktrace [1]_.

    .. code-block:: text

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

    Get the search query from the stacktrace and execute it on the splunk instance and verify which specific type of events are causing failure.

    If a field validating test case is failing, check the field's properties from the table provided for the reason of failure. 

------------

.. [1] Stacktrace is the text displayed in the Exception block when the Test fails.

