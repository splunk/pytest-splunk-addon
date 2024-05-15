# CIM Compliance Report

## Overview

- CIM compliance report provides insights to an user about the compatibility of the add-on with the supported CIM Data Models, which helps in identifying CIM coverage gaps and helps in understanding those gaps which can be fixed in the add-on.

## What does the report contain?

The report is divided into the following sections:

1. Summary of the number of test cases that failed versus the total number of test cases executed for all the supported Data Models, along with the status of the data model. A list of all possible 'status' values is given below:

     - Passed: All the test cases for the data model are executed successfully.
     - Failed: At least one of the test cases for the data model resulted into failure.
     - N/A: The data model is not mapped with the add-on.

2. Summary of the number of test cases that failed versus the total number of test cases executed for stanzas in tags.conf and the data model mapped with it.

3. Summary of test case results (passed/failed/skipped) for all the fields in the dataset for the tag-stanza it is mapped with.

4. A list of data models which are not supported by the plugin.

## How to generate the report?

There are two ways to generate the CIM Compliance report:

**1. Generating the report while executing the test cases**

- Append the following to [any one of the commands](how_to_use.md#test-execution) used for executing the test cases:

  ```console
  --cim-report <file_name.md>
  ```

**2. Generating the report using the test results stored in the junit-xml file**

- Execute the following command:

  ```console
  cim-report <junit_report.xml> <report.md>
  ```

## Report Generation Troubleshooting

If the CIM Compliance report is not generated, check for the following:

1. If the report was to generated during test case execution, check if CIM compatibility test cases were executed or not. If they were not executed, the report will not be generated.

2. If the report was generated using a JUnit report, check if the provided JUnit report:

     - Exists at the given location.

     - Has a valid format.
   
     - Has all the required properties which includes the following:
          1. Tag_stanza
          2. Data Model
          3. Data Set
          4. Field name
          5. Field type
