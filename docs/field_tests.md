# Knowledge Object Tests

## Overview

- The tests are written with a purpose of testing the proper functioning of the search-time knowledge objects of the add-on.

- Search-time knowledge objects are extracted/generated when a search query is executed on a Splunk Instance.

- The search-time knowledge objects include the following:
     1. Extract
     2. Report
     3. Lookups
     4. Fieldalias
     5. Eval
     6. Eventtypes
     7. Tags
     8. Savedsearches

______________________________________________________________________

To generate test cases only for knowledge objects, append the following marker to pytest command:

 ```console
 -m  splunk_searchtime_fields
 ```

## Test Scenarios

**1. Events should be present in source/sourcetype defined in props.conf stanza.**

 ```python
 test_props_fields[<stanza>]
 ```

 Testcase verifies that there are events mapped with source/sourcetype.
 Here &lt;stanza&gt; is the source/sourcetype that is defined in the stanza.

 **Workflow:**

 - Plugin gets the list of defined sourcetypes by parsing props.conf
 - For each sourcetype, plugin generates an SPL search query and asserts event_count  0.
 
 **Note:** Sourcetypes can be defined in two ways:
 - **Direct stanzas**: `[sourcetype_name]` in props.conf
 - **TRANSFORMS-defined**: Sourcetypes dynamically set via TRANSFORMS directives that reference transforms.conf entries with `FORMAT = sourcetype::<sourcetype_name>`
 
 Both types of sourcetypes are automatically discovered and tested for event coverage.

**2. Fields mentioned under source/sourcetype should be extracted**

 ```python
 test_props_fields[<stanza>::field::<fieldname>]
 ```

 Testcase verifies that the field should be extracted in the source/sourcetype.
 Here &lt;stanza&gt; is the source/sourcetype that is defined in the stanza and
 &lt;fieldname&gt; is the name of a field which is extracted under source/sourcetype.

 **Workflow:**

 - Plugin generates a list of fields extracted under the source/sourcetype by parsing the knowledge objects like Extract, Eval, Fieldalias etc.
 - For each field, plugin generates an SPL search query and asserts event_count  0.

**3. Negative scenarios for field values**

 ```python
 test_props_fields_no_dash_not_empty[<stanza>::field::<fieldname>]
 ```

 Testcase verifies that the field should not have "-" (dash) or "" (empty) as a value.
 Here &lt;stanza&gt; is the source/sourcetype that is defined in the stanza and
 &lt;fieldname&gt; is name of field which is extracted under source/sourcetype.

 **Workflow:**

 - Plugin generates a list of fields extracted under the source/sourcetype.
 - For each field, plugin generates a search query to check if the field has invalid values like \[" ", "-"\].
 - For each field, the event count should be 0.

**4. All the fields mentioned in an EXTRACT, REPORT, LOOKUP should be extracted in a single event.**

 ```python
 test_props_fields[<stanza>::EXTRACT-<classname>]
 test_props_fields[<stanza>::LOOKUP-<classname>]
 test_props_fields[<stanza>::REPORT-<classname>::<transforms_stanza>]
 ```

 All the fields mentioned in EXTRACT, REPORT or LOOKUP can be interdependent.
 The test case verifies that the extractions are working fine and all the fields are
 being extracted in a single event.
 The reason for keeping the test is to identify the corner cases where the fields are being
 extracted in several events but the extractions mentioned in EXTRACT, REPORT or LOOKUP is not
 working due to invalid regex/lookup configuration.

 **Workflow:**

 - While parsing the conf file when the plugin finds one of EXTRACT, REPORT, LOOKUP
   the plugin gets the list of fields extracted and generates a test case.
 - For all the fields in the test case it generates a single SPL search query including the stanza and asserts event_count > 0.
 - This verifies that all the fields are extracted in the same event.

**5. Events should be present in each eventtype**

 ```python
 test_eventtype[eventtype=<eventtype>]
 ```

 Test case verifies that there are events mapped with the eventtype.
 Here eventtype is an eventtype mentioned in eventtypes.conf.

 **Workflow:**

 - For each eventtype mentioned in eventtypes.conf plugin generates an SPL search query and asserts event_count > 0 for the eventtype.

**6. Tags defined in tags.conf should be applied to the events.**

 ```python
 test_tags[<tags_stanza>::tag::<tag>]
 ```

 Test case verifies that the there are events mapped with the tag.
 Here &lt;tag_stanza&gt; is a stanza mentioned in tags.conf and &lt;tag&gt; is an individual tag
 applied to that stanza.

 **Workflow:**

 - In tags.conf for each tag defined in the stanza, the plugin generates a test case.
 - For each tag, the plugin generates a search query including the stanza and the tag and asserts event_count > 0.

**7. Search query should be present in each savedsearches.**

 ```python
 test_savedsearches[<savedsearch_stanza>]
 ```

 Test case verifies that the search mentioned in savedsearch.conf generates valid search results.
 Here savedsearch_stanza is a stanza mentioned in savedsearches.conf file.

 **Workflow:**

 - In savedsearches.conf for each stanza, the plugin generates a test case.
 - For each stanza mentioned in savedsearches.conf plugin generates an SPL search query and asserts event_count > 0 for the savedsearch.

## Testcase Troubleshooting

In the case of test-case failure check if:

 - The add-on to be tested is installed on the Splunk instance.
 - Data is generated sufficiently for the add-on being tested.
 - Data is generated sufficiently in the specific index, it is being tested.
 - Splunk licence has not expired.
 - Splunk instance is up and running.
 - Splunk instance's management port is accessible from the test machine.

If all the above conditions are satisfied, further analysis of the test is required.
For every test case failure, there is a defined structure for the stack trace.

 ```text
 AssertionError: <<error_message>>
     Search =  <Query>
 ```

Get the search query from the stack trace and execute it on the Splunk instance and verify which specific type of events are causing failure.

## Performance Optimization

### Caching for pytest-xdist

When running tests with pytest-xdist (multiple workers), the plugin automatically caches parsed configuration files and generated test parameters to avoid redundant work across workers.

**What is cached:**
- Parsed configuration: props.conf, transforms.conf, tags.conf, eventtypes.conf, savedsearches.conf
- Generated test parameters for all fixtures

**How it works:**
- The first worker to request a cache key parses the data and saves it
- Other workers load from the shared cache instead of re-parsing
- Per-key locking prevents deadlocks when nested cache lookups occur
- Atomic writes with integrity hashing prevent cache corruption

**Cache files:**
- Location: `{temp_dir}/pytest-splunk-addon/{testrunuid}_{app_hash}_parser_cache`
- Cleaned up at process exit by the first worker (gw0)

**Note:** Caching only activates when running under pytest-xdist. Single-worker execution parses files directly without caching overhead.
