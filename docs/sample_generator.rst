Data Generator
===============

To ingest samples into Splunk, plugin takes `pytest-splunk-addon-data.conf` or `eventgen.conf` as input. 
The sample generation & ingestion takes place before executing the testcases. 
For index-time test cases, there are multiple metadata required about the sample file for which `pytest-splunk-addon-data.conf` must be created and provided to the pytest command.

To create the `pytest-splunk-addon-data.conf` file, a utility can be used.
Detailed steps on how to create the conf using utility can be found :ref:`here <generate_conf>`.

.. _conf_spec:

pytest-splunk-addon-data.conf.spec
------------------------------------------------
**Default Values**::

    [default]
    host_type = plugin
    input_type = default
    index = main
    sourcetype = pytest-splunk-addon
    source = pytest-splunk-addon:{{input_type}}
    sourcetype_to_search = {{sourcetype}}
    sample_count = 1
    timestamp_type = event
    count = 0
    earliest = now
    latest = now
    timezone = 0000
    breaker = {{regex}}
    host_prefix = {{host_prefix}}

[<sample file name>]
    * The stanza can contain the sample File Name or Regex to match multiple sample files.
    * The sample file should be located in samples folder under the Add-on package. 
    * Example1: [sample_file.samples] would collect samples from file sample_file.samples
    * Example2: [sample_*.samples] would collect samples from both sample_file.samples and sample_sample.samples.

sourcetype = <sourcetype>
    * sourcetype to be assigned to the sample events

source = <source>
    * source to be assigned to the sample events
    * default value: pytest-splunk-addon:{{input_type}}

sourcetype_to_search = <sourcetype>
    * The sourcetype used to search events
    * This would be different then sourcetype= param in cases where TRANSFORMS is used to update the sourcetype index time.

host_type = plugin | event
    * This key determines if host is assigned from event or default host should be assigned by plugin.
    * If the value is plugin, the plugin will generate host with format of "stanza_{count}" to uniquely identify the events.
    * If the value is event, the host field should be provided for a token using "token.<n>.field = host". 

input_type = modinput | scripted_input | syslog_tcp | file_monitor | windows_input | default
    * The input_type used in addon to ingest data of a sourcetype used in stanza.
    * The way with which the sample data is ingested in Splunk depends on Splunk. The most similar ingesting approach is used for each input_type to get accurate index-time testing.
    * For example, in an Add-on, a sourcetype "alert" is ingested through syslog in live environment, provide input_type=syslog_tcp.

index = <index>
    * The index used to ingest the data.
    * The index must be configured beforehand.
    * If the index is not available then the data will not get ingested into Splunk and a warning message will be printed.
    * Custom index is not supported for syslog_tcp or syslog_udp

sample_count = <count>
    * The no. of events present in the sample file.
    * This parameter will be used to calculate the total number of events which will be generated from the sample file.
    * If `input_type = modinput`, do not provide this parameter.

expected_event_count = <count>
    * The no. of events this sample stanza should generate.
    * The parameter will be used to test the line breaking in index-time tests.
    * To calculate expected_event_count 2 parameters can be used. 1) Number of events in the sample file. 2) Number of values of replacementType=all tokens in the sample file. Both the parameters can be multiplied to get expected_event_count.
    * For example, if sample contains 3 lines & a token has replacement_type=all and replacement has list of 2 values, then 6 events will be generated.
    * This parameter is optional, if it is not provided by the user, it will be calculated automatically by the pytest-splunk-addon.

timestamp_type = plugin | event
    * This key determines if _time is assigned from event or default _time should be assigned by plugin.
    * The parameter will be used to test the time extraction in index-time tests.
    * If value is plugin, the plugin will assign the time while ingesting the event.
    * If value is event, that means the time will be extracted from event and therfore, there should be a token provided with token.<n>.field = _time.

breaker = <regex>
    * The breaker is used to breakdown the sample file into multiple events, based on the regex provided.
    * This parameter is optional. If it is not provided by the user, the events will be ingested into Splunk,
      as per the *input_type* provided.

host_prefix = <host_prefix>
    * This param is used as an identification for the **host** field, for the events which are ingested using SC4S.

Token replacement settings 
-----------------------------
The following replacementType -> replacement values are supported

+-----------------+-------------------------------------------------------------------------------+
| ReplacementType |                                  Replacement                                  |
+=================+===============================================================================+
| static          | <string>                                                                      |
+-----------------+-------------------------------------------------------------------------------+
| timestamp       | <strptime>                                                                    |
+-----------------+-------------------------------------------------------------------------------+
| random          | ipv4                                                                          |
+-----------------+-------------------------------------------------------------------------------+
| random          | ipv6                                                                          |
+-----------------+-------------------------------------------------------------------------------+
| random          | mac                                                                           |
+-----------------+-------------------------------------------------------------------------------+
| random          | guid                                                                          |
+-----------------+-------------------------------------------------------------------------------+
| random          | integer[<start>:<end>]                                                        |
+-----------------+-------------------------------------------------------------------------------+
| random          | float[<start.numzerosforprecision>:<end.numzerosforprecision>]                |
+-----------------+-------------------------------------------------------------------------------+
| random          | list[< "," separated list>]                                                   |
+-----------------+-------------------------------------------------------------------------------+
| random          | hex([integer])                                                                |
+-----------------+-------------------------------------------------------------------------------+
| random          | file[<replacment file name, CSV file supported>:<column number / CSV header>] |
+-----------------+-------------------------------------------------------------------------------+
| random          | dest["host", "ipv4", "ipv6", "fqdn"]                                          |
+-----------------+-------------------------------------------------------------------------------+
| random          | src["host", "ipv4", "ipv6", "fqdn"]                                           |
+-----------------+-------------------------------------------------------------------------------+
| random          | host["host", "ipv4", "ipv6", "fqdn"]                                          |
+-----------------+-------------------------------------------------------------------------------+
| random          | dvc["host", "ipv4", "ipv6", "fqdn"]                                           |
+-----------------+-------------------------------------------------------------------------------+ 
| random          | user["name", "email", "domain_user", "distinquised_name"]                     |
+-----------------+-------------------------------------------------------------------------------+
| random          | url["ip_host", "fqdn_host", "path", "query", "protocol"]                      |
+-----------------+-------------------------------------------------------------------------------+
| random          | email                                                                         |
+-----------------+-------------------------------------------------------------------------------+
| random          | src_port                                                                      |
+-----------------+-------------------------------------------------------------------------------+
| random          | dest_port                                                                     |
+-----------------+-------------------------------------------------------------------------------+
| file            | <replacment file name, CSV file supported>:<column number / CSV header>       |
+-----------------+-------------------------------------------------------------------------------+
| all             | integer[<start>:<end>]                                                        |
+-----------------+-------------------------------------------------------------------------------+
| all             | list[< , separated list>]                                                     |
+-----------------+-------------------------------------------------------------------------------+
| all             | file[<replacment file name, CSV file supported>:<column number / CSV header>] |
+-----------------+-------------------------------------------------------------------------------+

token.<n>.token = <regular expression> 
    * "n" is a number starting at 0, and increasing by 1.
    * PCRE expression used to identify segment for replacement.
    * If one or more capture groups are present the replacement will be performed on group 1.


token.<n>.replacementType = static | timestamp | random | all | file
    * "n" is a number starting at 0, and increasing by 1.
    * For static, the token will be replaced with the value specified in the replacement setting.
    * For timestamp, the token will be replaced with the strptime specified in the replacement setting. Strptime directive: https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior
    * For random, the token will be replaced with a randomly picked type-aware value
    * For all, For each possible replacement value, a new event will be generated and the token will be replaced with it. The configuration can be used where a token replacement contains multiple templates/values and all of the values are important and should be ingested at least once. The number of events will be multiplied by the number of values in the replacement. For example, if sample contains 3 lines & a token replacement has list of 2 values, then 6 events will be generated. For a replacement if replacementType='all' is not supported, then be default plugin will consider replacementType="random".
    * For file, the token will be replaced with a random value retrieved from a file specified in the replacement setting.


token.<n>.replacement = <string> | <strptime> | ["list","of","values"] | guid | ipv4 | ipv6 | mac | integer[<start>:<end>] | float[<start>:<end>] | hex(<i>) | <file name> | <file name>:<column number> | host | src | dest | dvc | user | url | email | src_port | dest_port
    * "n" is a number starting at 0, and increasing by 1.
    * For <string>, the token will be replaced with the value specified.
    * For <strptime>, a strptime formatted string to replace the timestamp with
    * For guid, the token will be replaced with a random GUID value.
    * For ipv4, the token will be replaced with a random valid IPv4 Address (i.e. 10.10.200.1).
    * For ipv6, the token will be replaced with a random valid IPv6 Address (i.e. c436:4a57:5dea:1035:7194:eebb:a210:6361).
    * For mac, the token will be replaced with a random valid MAC Address (i.e. 6e:0c:51:c6:c6:3a).
    * For integer[<start>:<end>], the token will be replaced with a random integer between start and end values where <start> is a number greater than 0 and <end> is a number greater than 0 and greater than or equal to <start>. For replacement=all, one event will be generated for each value of integer within range <start> and <end>.
    * For float[<start>:<end>], the token will be replaced with a random float between start and end values where <end> is a number greater than or equal to <start>. For floating point numbers, precision will be based off the precision specified in <start>. For example, if we specify 1.0, precision will be one digit, if we specify 1.0000, precision will be four digits.
    * For hex(<i>), the token will be replaced with i number of Hexadecimal characters [0-9A-F] where "i" is a number greater than 0.
    * For list, the token will be replaced with a random member of the JSON list provided. For replacement=all, one event will be generated for each value within the list
    * For <replacement file name>, the token will be replaced with a random line in the replacement file.

        * Replacement file name should be a fully qualified path (i.e. $SPLUNK_HOME/etc/apps/windows/samples/users.list).
        * Windows separators should contain double forward slashes "\\" (i.e. $SPLUNK_HOME\\etc\\apps\\windows\\samples\\users.list).
        * Unix separators will work on Windows and vice-versa.
        * Column numbers in mvfile references are indexed at 1, meaning the first column is column 1, not 0.
    * For host["host", "ipv4", "ipv6", "fqdn"], 4 types of host replacement are supported. Either one or multiple from the list can be provided to randomly replace the token. 

        * For host["host"], the token will be replaced with a sequential host value with pattern "host_sample_host_<number>".
        * For host["ipv4"], the token will be replaced with a random valid IPv4 Address.
        * For host["ipv6"], the token will be replaced with a random valid IPv6 Address from fdee:1fe4:2b8c:3264:0:0:0:0 range.
        * For host["fqdn"], the token will be replaced with a sequential fqdn value with pattern "host_sample_host.sample_domain<number>.com".
    * For src["host", "ipv4", "ipv6", "fqdn"], 4 types of src replacement are supported. Either one or multiple from the list can be provided to randomly replace the token. 

        * For src["host"], the token will be replaced with a sequential host value with pattern "src_sample_host_<number>".
        * For src["ipv4"], the token will be replaced with a random valid IPv4 Address from 10.1.0.0 range.
        * For src["ipv6"], the token will be replaced with a random valid IPv6 Address from fdee:1fe4:2b8c:3261:0:0:0:0 range.
        * For src["fqdn"], the token will be replaced with a sequential fqdn value with pattern "src_sample_host.sample_domain<number>.com".
    * For dest["host", "ipv4", "ipv6", "fqdn"], 4 types of dest replacement are supported. Either one or multiple from the list can be provided to randomly replace the token. 

        * For dest["host"], the token will be replaced with a sequential host value with pattern "dest_sample_host_<number>".
        * For dest["ipv4"], the token will be replaced with a random valid IPv4 Address from 10.100.0.0 range.
        * For dest["ipv6"], the token will be replaced with a random valid IPv6 Address from fdee:1fe4:2b8c:3262:0:0:0:0 range.
        * For dest["fqdn"], the token will be replaced with a sequential fqdn value with pattern "dest_sample_host.sample_domain<number>.com".
    * For dvc["host", "ipv4", "ipv6", "fqdn"], 4 types of dvc replacement are supported. Either one or multiple from the list can be provided to randomly replace the token.

        * For dvc["host"], the token will be replaced with a sequential host value with pattern "dvc_sample_host_<number>".
        * For dvc["ipv4"], the token will be replaced with a random valid IPv4 Address from 172.16.0-50.0 range.
        * For dvc["ipv6"], the token will be replaced with a random valid IPv6 Address from fdee:1fe4:2b8c:3263:0:0:0:0 range.
        * For dvc["fqdn"], the token will be replaced with a sequential fqdn value with pattern "dvc_sample_host.sample_domain<number>.com".
    * For user["name", "email", "domain_user", "distinquised_name"], 4 types of user replacement are supported. Either one or multiple from the list can be provided to randomly replace the token.

        * For user["name"], the token will be replaced with a random name with pattern "user<number>".
        * For user["email"], the token will be replaced with a random email with pattern "user<number>@email.com".
        * For user["domain_user"], the token will be replaced with a random domain user pattern sample_domain.com\user<number>.
        * For user["distinquised_name"], the token will be replaced with a distinquised user with pattern CN=user<number>.
    * For url["full", "ip_host", "fqdn_host", "path", "query", "protocol"], 6 types of url replacement are supported. Either one or multiple from the list can be provided to randomly replace the token.

        * For url["ip_host"], the url to be replaced will contain ip based address.
        * For url["fqdn_host"], the url to be replaced will contain fqdn address.
        * For path["path"], the url to be replaced will contain path with pattern "/<path>".
        * For url["query"], the url to be replaced will contain query with pattern "?<query>=<value>".
        * For url["protocol"], the url to be replaced will contain protocol with pattern "<https or http>://".
        * For url["full"], the url contain all the parts mentioned above i.e. ip_host, fqdn_host, path, query, protocol.
        * Example 1: url["ip_host", "path", "query"], will be replaced with pattern <ip_address>/<path>?<query>=<value>
        * Example 2: url["fqdn_host", "path", "protocol"], will be replaced with pattern <https or http>://<fqdn_address>/<path>
        * Example 3: url["ip_host", "fqdn_host", "path", "query", "protocol"], will be replaced with pattern <https or http>://<ip_address or fqdn_address>/<path>?<query>=<value>
        * Example 4: url["full"], will be replaced same as example 3.
    * For email, the token will be replaced with a random email. If the same sample has a user token as well, the email and user tokens will be replaced with co-related values. 
    * For src_port, the token will be replaced with a random source port value between 4000 and 5000 
    * For dest_port, the token will be replaced with a random dest port value from (80,443,25,22,21)

token.<n>.field = <field_name>
    * "n" is a number starting at 0, and increasing by 1.
    * Assign the field_name for which the tokenized value will be extracted.
    * For this :ref:`key fields <key_fields>`, the index time test cases will be generated.
    * Make sure props.conf contains extractions to extract the value from the field.
    * If this parameter is not provided, the default value will be same as the token name.

.. note::
    Make sure token name is not same as that any of :ref:`key field <key_fields>` values.


Example
---------
.. code-block:: console

    [sample_file.samples]

    sourcetype = juniper:junos:secintel:structured
    sourcetype_to_search = juniper:junos:secintel:structured
    source = pytest-splunk-addon:syslog_tcp
    host_type = plugin
    input_type = syslog_tcp
    index = main
    timestamp_type = event
    sample_count = 10

    token.0.token = (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z)
    token.0.replacementType = timestamp
    token.0.replacement = %Y-%m-%dT%H:%M:%S

    token.1.token = ##token1##
    token.1.replacementType = static
    token.1.replacement = sample_value

    token.2.token = ##Src_Addr##
    token.2.replacementType = random
    token.2.replacement = src["ipv4"]
    token.2.field = src

    token.3.token = ##Dest_Addr##
    token.3.replacementType = random
    token.3.replacement = dest["ipv4"]

    token.4.token = ##Src_Port##
    token.4.replacementType = random
    token.4.replacement = src_port
    token.4.field = src_port

    token.5.token = ##Dest_Port##
    token.5.replacementType = random
    token.5.replacement = dest_port

    token.6.token = ##dvc##
    token.6.replacementType = random
    token.6.replacement = dvc["fqdn","host"]
    token.6.field = dvc

    token.7.token = ##User##
    token.7.replacementType = random
    token.7.replacement = user["name"]

    token.8.token = ##HTTP_Host##
    token.8.replacementType = random
    token.8.replacement = host["fqdn"]

    token.9.token = ##ReferenceIDhex##
    token.9.replacementType = random
    token.9.replacement = hex(8)

    token.10.token = ##Ip##
    token.10.replacementType = random
    token.10.replacement = ipv4

    token.11.token = ##Ipv6##
    token.11.replacementType = random
    token.11.replacement = ipv6

    token.12.token = ##Name##
    token.12.replacementType = random
    token.12.replacement = list["abc.exe","def.exe","efg.exe"]

    token.13.token = ##Name##
    token.13.replacementType = all
    token.13.replacement = list["abc.exe","def.exe","efg.exe"]

    token.14.token = ##email##
    token.14.replacementType = random
    token.14.replacement = email

    token.15.token = ##mac##
    token.15.replacementType = random
    token.15.replacement = mac

    token.16.token = ##memUsedPct##
    token.16.replacementType = random
    token.16.replacement = float[1.0:99.0]

    token.17.token = ##guid##
    token.17.replacementType = random
    token.17.replacement = guid

    token.18.token = ##size##
    token.18.replacementType = random
    token.18.replacement = integer[1:10]

    token.19.token = ##integer_all##
    token.19.replacementType = all
    token.19.replacement = integer[1:5]

    token.20.token = ##url##
    token.20.replacementType = random
    token.20.replacement = url["ip_host", "fqdn_host", "path", "query", "protocol"]

    token.21.token = ##DHCP_HOST##
    token.21.replacementType = random
    token.21.replacement = file[/path/linux.host.sample]

    token.22.token = ##DHCP_HOST_all##
    token.22.replacementType = all
    token.22.replacement = file[/path/linux.host.sample]
