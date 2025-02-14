# Release Notes - Pytest-splunk-addon 6.0.0

## Breaking Changes
- Removed the support of cim-field-report generation.


## New features

- Added support for CIM v6.0.2
  - New data models added:
    - Data Access
    - Database
    - Event Signature
    - Interprocess Messaging
    - Computer Inventory
    - JVM
    - Performance
    - Ticket Management
  - Updated fields with expected values and conditions.
    - Eg: Added expected values ["critical","high","medium","low","informational"] for severity field in Malware data model.
  - For existing data models updated fields to required or optional based on CIM App Jsons.
    - Eg: For Alert data model, body field is now marked as optional(as it is deprecated) and description is marked as required which was previously optional.
    - So now if addon does not extract the description field for events tagged with Alert data model, then this will lead to failures for tests template: `test_cim_required_fields*` for those samples
  - Furthermore, recommended fields have also been added to data models
    - Eg: For Data Access fields like object_category and user_name are added as recommended fields.
    - Again if the addon does not extract these fields then tests with test template : `test_cim_fields_recommended*` will fail for those samples.
  - If the failures for test templates shown above are observed then it is recommended to extract those fields as the updates in all the Data models have been made with guidance of the SMEs.

## Bug fixes

- Fixed the issue with the token replacement for the fields defined under `other_mappings` for the sample event.