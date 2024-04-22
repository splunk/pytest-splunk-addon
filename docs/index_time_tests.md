# Index Time Tests

## Overview

- The tests are written with a purpose of testing the proper functioning of the index-time properties of the add-on.

- Index time properties are applied on the events when they are ingested into the Splunk instance.

- The index time properties which are tested are as follows:
     1. Key Fields Extraction
     2. Timestamp (\_time)
     3. LINE_BREAKER

### Prerequisites

- `pytest-splunk-addon-data.conf` file which contains all the required data
  executing the tests. The conf file should follow the specifications as mentioned {ref}`here <conf_spec`.

______________________________________________________________________


To generate test cases only for index time properties, append the following marker to pytest command:

 ```console
 -m  splunk_indextime --splunk-data-generator=<Path to the conf file
 ```

> **_NOTE:_** --splunk-data-generator should contain the path to *pytest-splunk-addon-data.conf*,
 as the test cases will not execute on *eventgen.conf* file.

## Test Scenarios


**1. Test case for key fields extraction:**

 ```python
 test_indextime_key_fields[<sourcetype::<host_name]
 ```

 - Test case verifies if all the key fields are extracted properly,
   as mentioned in the `pytest-splunk-addon-data.conf` file.

 - The key fields which are checked are as follows:

    - src
    - src_port
    - dest
    - dest_port
    - dvc
    - host
    - user
    - url


 - This test case will not be generated if there are no key fields specified for the event.
 - Key field can be assign to token using field property. `i.e token.n.field = <KEY_FIELD`

 Testcase assertions:

 - There should be at least 1 event with the sourcetype and host.
 - The values of the key fields obtained from the event
   must match with the values of the key fields which was used in generating and ingesting the event.

 **Workflow:**

 - To generate the test case, the following properties will be required:

    - sourcetype and host in the event.
    - Key fields in the event for which the test case is executed.

 - Generates an SPL query according to the properties mentioned above.

 - Execute the SPL query in a Splunk instance.

 - Assert the test case results as mentioned in {ref}`testcase assertions<test_assertions_key_field`.

**2. Test case for \_time property:**

 ```python
 test_indextime_time[<sourcetype::<host_name]
 ```

 - Test case verifies if the timestamp for the event is assigned properly.
 - The timestamp is assigned to the \_time field which is validated by the test case.
 - This test case will be generated if timestamp_type = event in stanza.
 - \_time field can be assign to token using field property. i.e `token.n.field = _time`

 Testcase assertions:

 - There should be at least 1 event with the sourcetype and host.
 - There should be at least 1 token with field \_time in stanza.
 - One event should have only one token with token.n.field = \_time.
 - Every event should have token with token.n.field = \_time.
 - The values of the \_time fields obtained from the event
   must match with the values of the time values which was used in generating and ingesting the event.

 **Workflow:**

 - Generates an SPL query using sourcetype and host from the event.
 - Execute the SPL query in a Splunk instance.
 - The value of \_time obtained from the search query is matched
   with the \_time value assigned to the event before ingesting it.

> **_NOTE:_** The test case for \_time field will not be generated if `timestamp_type = plugin` in
 pytest-splunk-addon-data.conf

**3. Test case for line-breaker property:**

 ```python
 test_indextime_line_breaker[<sourcetype::<host_name]
 ```

 - Test case verifies if the LINE_BREAKER property used in props.conf works properly.
 - If sample_count is not provided in pytest-splunk-addon-data.conf, it will take
   sample_count = 1.

 Testcase assertions:

 - Number of events for particular sourcetype and host should match with value of
   `expected_event_count` which is calculated by pytest-splunk-addon from the `sample_count`
   parameter provided in the pytest-splunk-addon-data.conf.

 **Workflow:**

 - Generates an SPL query using sourcetype and host from the event.
 - Execute the SPL query in a Splunk instance.
 - The number of results obtained from the search query is matched with the
   *expected_event_count* value, which is calculated by the plugin.

## Testcase Troubleshooting

In the case test-case failure check if:

 - The add-on to be tested is installed on the Splunk instance.
 - Data is generated for the addon being tested.
 - Splunk licence has not expired.
 - Splunk instance is up and running.
 - Splunk instance's management port is accessible from the test machine.

If all the above conditions are satisfied, further analysis of the test is required.
For every test case failure, there is a defined structure for the stack trace [^footnote-1].

 ```text
 AssertionError: <<error_message
     Search =  <Query
 ```

Get the search query from the stack trace and execute it on the Splunk instance and verify which specific type of events are causing failure.

## FAQ

1. What is the source of data used while testing with pytest-splunk-addon 1.3.0 and above?

      - pytest-splunk-addon relies on samples available in addon folder under path provided `--splunk-app` or `--splunk-data-generator` options.

2. When do I assign timestamp_type = event to test the time extraction (\_time) for a stanza?

      - When the Splunk assigns \_time value from a timestamp present in event based on props configurations, you should assign `timestamp_type=event` for that sample stanza.

      - Example :
        : For this sample, Splunk assigns the value `2020-06-23T00:00:00.000Z` to `_time`.

          ```text
          2020-06-23T00:00:00.000Z test_sample_1 test_static=##token_static_field## . . .
          ```

          In this scenario the value `2020-06-23T00:00:00.000Z` should be tokenized, stanza should have `timestamp_type=event` and the token should also have `token.0.field = _time` as shown below:

          ```text
          token.0.token = (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+)
          token.0.replacementType = timestamp
          token.0.replacement = %Y-%m-%dT%H:%M:%S
          token.0.field = _time
          ```

3. When do I assign timestamp_type = plugin to test the time extraction (\_time) for a stanza?

     - When there is no timestamp available in event or the props configurations are written to have the Splunk default timestamp assigned instead timestamp present in event, you should assign `timestamp_type=plugin` for that sample stanza.
     - No \_time test generates for the sample stanza when `timestamp_type = plugin`.
     - Example:
       - For this sample, Splunk assigns the default time value to `_time`.

         ```text
         test_sample_1 test_static=##token_static_field## src=##token_src_ipv4## . . .
         ```

         In this scenario, the stanza should have `timestamp_type=plugin`.

4. When do I assign host_type = plugin for a sample stanza?

    - When there are no configurations written in props to override the host value in event and Splunk default host value is assigned for host field instead of a value present in event, you should assign `host_type=plugin` for that sample stanza.

5. When do I assign host_type = event for a sample stanza?

     - When there are some configurations written in props to override the host value for an event you should assign `host_type=event` for that sample stanza.
     - Example:
            : For this sample, Splunk assigns the value sample_host to host based on the props configurations present in addon

              ```text
              test_modinput_1 host=sample_host static_value_2=##static_value_2## . . .
              ```

              In this scenario the value "sample_host" should be tokenized, stanza should have `host_type=event` and the token should also have `token.0.field = host` as shown below:

              ```text
              token.0.token = ##host_value##
              token.0.replacementType = random
              token.0.replacement = host["host"]
              token.0.field = host
              ```

6. Can I test any field present in my event as Key Field in Key Fields tests?

    - No, Key Fields are defined in plugin and only below fields can be validated as part of Key Field tests.
       - src
       - src_port
       - dest
       - dest_port
       - dvc
       - host
       - user
       - url

7. What if I don't assign any field as key_field in a particular stanza even if its present in props?

     - No test would generate to test Key Fields for that particular stanza and thus won't be correctly tested. 
 
8. When do I assign token.\<n.field = \<field_name to test the Key Fields for an event?

     - When there props configurations written in props to extract any of the field present in Key Fields list, you should add `token.<n.field = <field_name` to the token for that field value.
     - Example:
       : For this sample, there is report written in props that extracts `127.0.0.1` as `src`,

         ```text
         2020-06-23T00:00:00.000Z test_sample_1 127.0.0.1
         ```

         In this scenario the value `127.0.0.1` should be tokenized and the token should also have `token.0.field = src` as shown below:

         ```text
         token.0.token = ##src_value##
         token.0.replacementType = random
         token.0.replacement = src["ipv4"]
         token.0.field = src
         ```

______________________________________________________________________

[^1]: Stacktrace is the text displayed in the Exception block when the Test fails.
