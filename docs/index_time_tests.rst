Index Time Tests
=======================

Overview
-------------------

* The tests are written with a purpose of testing the proper functioning of the index-time properties of the add-on.
* Index time properties are applied on the events when they are ingested into the Splunk instance.
* The index time properties which are tested are as follows:

    1. Key Fields Extraction
    2. Timestamp (_time)
    3. LINE_BREAKER

Prerequisites
""""""""""""""""

* `pytest-splunk-addon-data.conf` file which contains all the required data
  executing the tests. The conf file should follow the specifications as mentioned :ref:`here <conf_spec>`.

--------------------------------

.. _index_time_tests:

To generate test cases only for index time properties, append the following marker to pytest command:

    .. code-block:: console

        -m  splunk_indextime --splunk-data-generator=<Path to the conf file>

    .. note::
        --splunk-data-generator should contain the path to *pytest-splunk-addon-data.conf*,
        as the test cases will not execute on *eventgen.conf* file.


Test Scenarios
--------------

.. _key_fields:

**1. Test case for key fields extraction:**

    .. code-block:: python

        test_indextime_key_fields[<sourcetype>::<host_name>]

    * Test case verifies if all the key fields are extracted properly, 
      as mentioned in the `pytest-splunk-addon-data.conf` file.
    * The key fields which are checked are as follows:

        * src
        * src_port
        * dest
        * dest_port
        * dvc
        * host
        * user
        * url

    .. _test_assertions_key_field:

    * This test case will not be generated if there are no key fields specified for the event.
    * Key field can be assign to token using field property. `i.e token.n.field = <KEY_FIELD>`

    Testcase assertions:

    * There should be at least 1 event with the sourcetype and host.
    * The values of the key fields obtained from the event 
      must match with the values of the key fields which was used in generating and ingesting the event.

    **Workflow:**

    * To generate the test case, the following properties will be required:

        * sourcetype and host in the event.
        * Key fields in the event for which the test case is executed.

    * Generates an SPL query according to the properties mentioned above. 
    * Execute the SPL query in a Splunk instance.
    * Assert the test case results as mentioned in :ref:`testcase assertions<test_assertions_key_field>`.

**2. Test case for _time property:**

    .. code-block:: python

        test_indextime_time[<sourcetype>::<host_name>]

    * Test case verifies if the timestamp for the event is assigned properly.
    * The timestamp is assigned to the _time field which is validated by the test case.
    * This test case will be generated if timestamp_type = event in stanza.
    * _time field can be assign to token using field property. i.e `token.n.field = _time`

    Testcase assertions:

    * There should be at least 1 event with the sourcetype and host.
    * There should be at least 1 token with field _time in stanza.
    * One event should have only one token with token.n.field = _time.
    * Every event should have token with token.n.field = _time.
    * The values of the _time fields obtained from the event 
      must match with the values of the time values which was used in generating and ingesting the event.

    **Workflow:**

    * Generates an SPL query using sourcetype and host from the event. 
    * Execute the SPL query in a Splunk instance.
    * The value of _time obtained from the search query is matched
      with the _time value assigned to the event before ingesting it.

    .. note::
        The test case for _time field will not be generated if `timestamp_type = plugin` in
        pytest-splunk-addon-data.conf

**3. Test case for line-breaker property:**

    .. code-block:: python

        test_indextime_line_breaker[<sourcetype>::<host_name>]

    * Test case verifies if the LINE_BREAKER property used in props.conf works properly.
    * If sample_count is not provided in pytest-splunk-addon-data.conf, it will take
      sample_count = 1.

    Testcase assertions:

    * Number of events for particular sourcetype and host should match with value of 
      `expected_event_count` which is calculated by pytest-splunk-addon from the `sample_count` 
      parameter provided in the pytest-splunk-addon-data.conf.

    **Workflow:**

    * Generates an SPL query using sourcetype and host from the event. 
    * Execute the SPL query in a Splunk instance.
    * The number of results obtained from the search query is matched with the 
      *expected_event_count* value, which is calculated by the plugin.

Testcase Troubleshooting
------------------------

In the case test-case failure check if:

    - The add-on to be tested is installed on the Splunk instance.
    - Data is generated for the addon being tested.
    - Splunk licence has not expired.
    - Splunk instance is up and running.
    - Splunk instance's management port is accessible from the test machine.

If all the above conditions are satisfied, further analysis of the test is required.
For every test case failure, there is a defined structure for the stack trace [1]_.

    .. code-block:: text

        AssertionError: <<error_message>>
            Search =  <Query>

Get the search query from the stack trace and execute it on the Splunk instance and verify which specific type of events are causing failure.

------------

.. [1] Stacktrace is the text displayed in the Exception block when the Test fails.
