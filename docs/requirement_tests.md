# Requirement Tests

## Overview

- The tests are written with a purpose of testing the proper functioning of the fields extractions of the add-on.
- Requirement tests use XML sample files with embedded field expectations (`cim_fields`, `other_mappings`)

______________________________________________________________________

To generate only requirement tests, append the following marker to pytest command:

 ```console
 -m  splunk_requirements
 ```

## XML Sample File Structure for Requirement Tests

Requirement tests require XML format sample files with `requirement_test_sample = 1` in the conf file.

### Transport Node Usage

The `<transport>` node in XML samples has specific meaning for requirement tests:

```xml
<transport type="modinput" host="sample_host" source="test_source" sourcetype="test:sourcetype" />
```

| Attribute | Behavior in Requirement Tests |
|-----------|------------------------------|
| `type` | Used for syslog header stripping (if `type="syslog"`). NOT used for ingestion. |
| `host` | **Overrides** the host value that is recorded in both the ingested event metadata and the search query generated for that event. |
| `source` | **Overrides** the source value that is recorded in the ingested event metadata and the search query generated for that event. |
| `sourcetype` | Used in field extraction test searches (not ingestion) |

**Important:** The actual ingestion is still driven by the conf file's `input_type`, `sourcetype`, and other metadata settings, but any `<transport host>` or `<transport source>` values found in the XML are merged into the `SampleEvent` metadata before ingestion and before the search query is generated (see `pytest_splunk_addon/sample_generation/sample_stanza.py`). That means those XML overrides affect the payload submitted to Splunk and the constraints that the requirement tests evaluate, not just the search query.

### Scenarios

- **Requirement test sample with `<transport host/source>` overrides:**  
  The XML parser injects these override values into `SampleEvent.metadata`, the ingestor emits them in the indexed event, and the search generator reuses them so the test looks for the same host/source.
- **Field test sample with `<transport type="syslog">`:**  
  Only the syslog header stripping behavior is affected; the host/source/sourcetype are still driven by the conf stanza (`host_type`, `host`, `source`, `sourcetype_to_search`) and tokens.
- **Events without XML transport overrides:**  
  Ingestors rely entirely on stanza metadata; searches use `host`/`source`/`sourcetype_to_search` from the conf file or tokens.

## Test Scenarios

**1. Fields should be extracted as defined in the cim_fields and other_mappings.**

 ```python
 test_requirements_fields[sample_name::<stanza>::host::<host>]
 ```

 Testcase verifies that fields are getting extracted with the values defined in the cim_fields and other_mappings in sample xml.
 Here &lt;stanza&gt; is the stanza name defined in the pytest-splunk-addon-data.conf and
 &lt;host&gt; is the host of the event

 **Workflow:**

 - Plugin gets the list of events and the fields defined under cim_fields and other_mappings for each event
 - For each event, plugin generates a search query to retrieve all the fields extracted by splunk.
 - For each event, all the fields defined in the cim_fields and other_mappings should be extracted with the values defined in sample xml.

**2. Event should be mapped with the datamodel defined in the sample xml**

 ```python
 test_datamodels[<datamodel>::sample_name::<stanza>::host::<host>]
 ```

 Testcase verifies that the event is mapped with the datamodel defined in the sample xml.
 Here &lt;datamodel&gt; is the name of the datamodel that the event should be mapped with, &lt;stanza&gt; is the stanza name defined in the pytest-splunk-addon-data.conf and &lt;host&gt; is the host of the event

 **Workflow:**

 - Plugin gets the events and its expected datamodel from the sample xml
 - Plugin generates a search query for that event and validates if the values of tags field are according to the datamodel defined in sample xml.

**3. All the cim recommended field should be extracted**

 ```python
 test_cim_fields_recommended[<datamodel>::sample_name::<stanza>::host::<host>]
 ```

 Testcase verifies that all the cim recommended fields of mapped datamodel are extracted for the event defined in the sample xml.
 Here &lt;datamodel&gt; is the name of the datamodel that the event should be mapped with, &lt;stanza&gt; is the stanza name defined in the pytest-splunk-addon-data.conf and &lt;host&gt; is the host of the event

 **Workflow:**

 - For each events, plugin gets the list of fields defined under cim_fields and missing_recommended_fields.
 - Field list retrieved from the sample xml should be equal to the list of recommended fields defined in the datamodel schema.

## Testcase Troubleshooting

In the case of test-case failure check if:

 - The add-on to be tested is installed on the Splunk instance.
 - Splunk licence has not expired.
 - Splunk instance is up and running.
 - Splunk instance's management port is accessible from the test machine.

If all the above conditions are satisfied, further analysis of the test is required.
For every test case failure, there is a defined structure for the stack trace.

 ```text
 - test_requirements_fields
 AssertionError: <<error_message>>
     Field | Splunk Value | Expected Value
     ------| ------------ | --------------
      str  |      str     |      str
 Search =  <Query>

 - test_datamodels
 AssertionError: <<error_message>>
     Expected datamodel | Expected tags | Found datamodel | Found tags
     -------------------| ------------- | --------------- | ----------
            str         |      str      |       str       |    str
 Search =  <Query>

 - test_cim_fields_recommended
 AssertionError: <<error_message>>
 Search =  <Query>
 ```

Get the search query from the stack trace and execute it on the Splunk instance and verify which specific event is causing failure.
