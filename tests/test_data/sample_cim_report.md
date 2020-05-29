# CIM AUDIT REPORT 

##  Summary

| Data Model | Status | Fail/Total  |
 |:----------|:------|:---------- |
| Alerts | N/A | -  |
| Authentication | Passed | 0/1  |
| Certificates | N/A | -  |
| Change | Passed | 0/1  |
| DLP | N/A | -  |
| Email | N/A | -  |
| Endpoint | N/A | -  |
| Intrusion_Detection | N/A | -  |
| Malware | Passed | 0/1  |
| Network_Resolution | N/A | -  |
| Network_Sessions | N/A | -  |
| Network_Traffic | Failed | 1/1  |
| Updates | N/A | -  |
| Vulnerabilities | N/A | -  |
| Web | N/A | -  |


## Tag Stanza Mapping

| Tag Stanza | Data Model | Data Set | Fail/Total  |
 |:----------|:----------|:--------|:---------- |
| file_authentication | Authentication | Default_Authentication | 0/1  |
| tag_stanza_1 | Change | All_Changes | 0/1  |
| file_integrity_monitoring | Malware | Malware_Attacks | 0/1  |
| event_traffic | Network_Traffic | All_Traffic | 1/1  |


## Field Summary
### file_authentication - Default_Authentication
| Field | Type | Test Status | Failure Message  |
 |:-----|:----|:-----------|:--------------- |
| change_type | required | Skipped | -  |

### tag_stanza_1 - All_Changes
| Field | Type | Test Status | Failure Message  |
 |:-----|:----|:-----------|:--------------- |
| action | required | Passed | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa  |

### file_integrity_monitoring - Malware_Attacks
| Field | Type | Test Status | Failure Message  |
 |:-----|:----|:-----------|:--------------- |
| dest | required | Passed | -  |

### event_traffic - All_Traffic
| Field | Type | Test Status | Failure Message  |
 |:-----|:----|:-----------|:--------------- |
| command | conditional | Failed | AssertionError: Field command is not extracted in any events.  |


## Skipped Tests Summary

| Tag Stanza | Data Set | Field  |
 |:----------|:--------|:----- |
| file_authentication | Default_Authentication | change_type  |

### Not Supported Datamodels
| Name  |
 |:---- |
| Application_State  |
| Change_Analysis  |
| Compute_Inventory  |
| Databases  |
| Event_Signatures  |
| Interprocess_Messaging  |
| JVM  |
| Performance  |
| Splunk_Audit  |
| Splunk_CIM_Validation  |
| Ticket_Management  |

