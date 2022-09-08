#
# Copyright 2021 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# CIM 4.20.2
# Defines tags associated with data models. Used to determine the DM's associated with tags returned by the Splunk
# search for eg: 'tag': "['authentication', 'insecure', 'network', 'resolution', 'dns', 'success']" matches
# 'Authentication': ['authentication'], 'Authentication_Insecure_Authentication': ['authentication', 'insecure'],
# 'Network_Resolution': ['network', 'resolution', 'dns']
dict_datamodel_tag = {
    "Alerts": ["alert"],
    "Authentication": ["authentication"],
    "Authentication_Default_Authentication": ["default", "authentication"],
    "Authentication_Insecure_Authentication": ["authentication", "insecure"],
    "Authentication_Insecure_Authentication.2": ["authentication", "cleartext"],
    "Authentication_Privileged_Authentication": ["authentication", "privileged"],
    "Certificates": ["certificate"],
    "Certificates_SSL": ["certificate", "ssl"],
    "Change": ["change"],
    "Change_Auditing_Changes": ["change", "audit"],
    "Change_Endpoint_Changes": ["change", "endpoint"],
    "Change_Network_Changes": ["change", "network"],
    "Change_Account_Management": ["change", "account"],
    "Change_Instance_Changes": ["change", "instance"],
    "Compute_Inventory_CPU": ["inventory", "cpu"],
    "Compute_Inventory_Memory": ["inventory", "memory"],
    "Compute_Inventory_Network": ["inventory", "network"],
    "Compute_Inventory_Storage": ["inventory", "storage"],
    "Compute_Inventory_OS": ["inventory", "system", "version"],
    "Compute_Inventory_User": ["inventory", "user"],
    "Compute_Inventory_User_Default_Accounts": ["inventory", "user", "default"],
    "Compute_Inventory_Virtual_OS": ["inventory", "virtual"],
    "Compute_Inventory_Virtual_OS_Snapshot": ["inventory", "virtual", "snapshot"],
    "Compute_Inventory_Virtual_OS_Tools": ["inventory", "virtual", "tools"],
    "Databases": ["database"],
    "Databases_Database_Instance": ["database", "instance"],
    "Databases_Database_Instance_Instance_Stats": ["database", "instance", "stats"],
    "Databases_Database_Instance_Session_Info": ["database", "instance", "session"],
    "Databases_Database_Instance_Lock_Info": ["database", "instance", "lock"],
    "Databases_Database_Query": ["database", "query"],
    "Databases_Database_Query_Tablespace": ["database", "query", "tablespace"],
    "Databases_Database_Query_Query_Stats": ["database", "query", "stats"],
    "DLP": ["dlp", "incident"],
    "Email": ["email"],
    "Email_Delivery": ["email", "delivery"],
    "Email_Content": ["email", "content"],
    "Email_Filtering": ["email", "filter"],
    "Endpoint_Ports": ["listening", "port"],
    "Endpoint_Processes": ["process", "report"],
    "Endpoint_Filesystem": ["endpoint", "filesystem"],
    "Endpoint_Services": ["service", "report"],
    "Endpoint_Registry": ["endpoint", "registry"],
    "Event_Signatures_Signatures": ["track_event_signatures"],
    "Interprocess_Messaging": ["messaging"],
    "Intrusion_Detection": ["ids", "attack"],
    "JVM": ["jvm"],
    "JVM_Runtime": ["jvm", "runtime"],
    "JVM_OS": ["jvm", "os"],
    "JVM_Classloading": ["jvm", "classloading"],
    "JVM_Memory": ["jvm", "memory"],
    "JVM_Threading": ["jvm", "threading"],
    "JVM_Compilation": ["jvm", "compilation"],
    "Malware_Malware_Attacks": ["malware", "attack"],
    "Malware_Malware_Operations": ["malware", "operations"],
    "Network_Resolution_DNS": ["network", "resolution", "dns"],
    "Network_Sessions": ["network", "session"],
    "Network_Sessions_Session_Start": ["network", "session", "start"],
    "Network_Sessions_Session_End": ["network", "session", "end"],
    "Network_Sessions_DHCP": ["network", "session", "dhcp"],
    "Network_Sessions_VPN": ["network", "session", "vpn"],
    "Network_Traffic": ["network", "communicate"],
    "Performance_CPU": ["performance", "cpu"],
    "Performance_Facilities": ["performance", "facilities"],
    "Performance_Memory": ["performance", "memory"],
    "Performance_Storage": ["performance", "storage"],
    "Performance_Network": ["performance", "network"],
    "Performance_OS": ["performance", "os"],
    "Performance_OS_Timesync": ["performance", "os", "time", "synchronize"],
    "Performance_OS_Uptime": ["performance", "os", "uptime"],
    "Splunk_Audit": ["modaction"],
    "Splunk_Audit_Modular_Action_Invocations": ["modaction", "invocation"],
    "Ticket_Management": ["ticketing"],
    "Ticket_Management_Change": ["ticketing", "change"],
    "Ticket_Management_Incident": ["ticketing", "incident"],
    "Ticket_Management_Problem": ["ticketing", "problem"],
    "Updates": ["update", "status"],
    "Updates_Update_Errors": ["update", "error"],
    "Vulnerabilities": ["report", "vulnerability"],
    "Web": ["web"],
    "Web_Proxy": ["web", "proxy"],
    "Web_Storage": ["web", "storage"],
    "Data_Access": ["data", "access"],
}
