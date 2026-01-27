# Copyright 2026 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
