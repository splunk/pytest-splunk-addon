# Release Notes - Pytest-splunk-addon 6.0.0


## New features

- Extended the LR schema. Now you can use notes inside \<event\>  and field notes as well.
  - Notes inside \<event\>:
    ```bash
    <note>some note</note>
    ```
  - Field notes:
    ```bash
    <field name="action" value="created" note="some field level note" />
    ```
 - Added support for CIM v5.3.2
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

 - Added support for CLEAN_KEYS param
   - Now if Addons has field names in reports stanzas which have non-alphanumeric chars then those chars would be first converted to "_" and then tests would be generated as by default in splunk CLEAN_KEYS is set to true.
   - Moreover, if any report stanzas has explicitly set CLEAN_KEYS=false then for those reports, field conversion would not happen and tests would be generated as it is.
   - Eg: In the below stanza tests for server_contact field would be generated instead of server-contact.
   ```
         [example_report]
         FIELDS = server-contact
   ```
   - Similarly, if in the example_report CLEAN_KEYS = false is provided then tests for server-contact would be generated as is.


## Improvements
 - Refactoring change to remove standard_lib nested folder.
 - Merged respective docker-compose* and pytest* files into one.
   - Now we have common files docker-compose.yml and pytest.ini for ci and local execution.
 - Added validation if a same field is present in cim_fields and missing_recommended_fields for sample and raise warning highlighting the same.

## Bug fixes

 - Fixed the url rule for url["path"] and url["query"]
   - url["path"] will result into a path. eg: /path
   - url["query"] will result into a query. eg: ?a=b
 - Fixed an issue of duplicate logging of warnings by every worker while parsing conf files.
