# Common Tests

## Test Scenarios

**1. Events ingested are properly tokenised or not.**

 ```python
 test_events_with_untokenised_values
 ```

 Testcase verifies that all the events have been properly tokenised.
 That is event does not contain any token from the conf file in its raw form i.e enclosed within ##.

 When `--untokenised-sourcetype-patterns` is supplied as a JSON array, the search is
 restricted to those sourcetype patterns. This is useful on shared Splunk stacks,
 where events from multiple add-ons are indexed together. Each add-on's test job
 should pass its own patterns. If omitted, the test retains its historical all-index
 search behavior.
