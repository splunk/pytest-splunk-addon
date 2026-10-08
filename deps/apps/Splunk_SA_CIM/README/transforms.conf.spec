[<unique_transform_stanza_name>]
reverse_lookup_honor_case_sensitive_match = {default|true|false}
* Optional setting.
* This setting does not apply to KV Store lookups.
* Default: true
* When set to true, and case_sensitive_match is true Splunk software performs case-sensitive matching for
  all fields in a reverse lookup.
* When set to true, and case_sensitive_match is false Splunk software performs case-insensitive matching for
  all fields in a reverse lookup.
* When set to false, Splunk software performs case-insensitive matching for
  all fields in a reverse lookup.
