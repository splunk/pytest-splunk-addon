Common Tests
=======================

Test Scenarios
--------------

**1. Events ingested are properly tokenised or not.**

    .. code-block:: python

        test_events_with_untokenised_values

    Testcase verifies that all the events have been properly tokenised.
    That is event does not contain any token from the conf file in its raw form i.e enclosed within ##.