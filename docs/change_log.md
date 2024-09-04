# v6.0.0

 - Extended the LR schema. Now you can use notes inside <event>  and field notes as well.
 - Fixed the url rule for url["path"] and url["query"]
   - url["path"] will result into a path. eg: /path
   - url["query"] will result into a query. eg: ?a=b
 - Added support for cim v5.3.2
   - For existing data models updated fields to required or optional based on CIM App Jsons.
   - New data models added:
     - Data Access
     - Database
     - Event Signature
     - Interprocess Messaging
     - Computer Inventory
     - JVM
     - Performance
     - Ticket Management
 - Refactoring change to remove standard_lib nested folder.
 - Fixed an issue of duplicate logging of warnings by every worker while parsing conf files.