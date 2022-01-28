import pytest
from splunklib import binding, client, results
import time
import os

pytest_plugins = "pytester"

def pytest_configure(config):
    config.addinivalue_line("markers", "external: Test search time only")
    config.addinivalue_line("markers", "kubernetes: Test search time only")


class TASetup(object):
    def __init__(self, splunk):
        self.splunk = splunk

    def wait_for_lookup(self, lookup):
        splunk_client = client.connect(**self.splunk)
        for _ in range(60):
            job_result = splunk_client.jobs.oneshot(f" | inputlookup {lookup}")
            for _ in results.ResultsReader(job_result):
                return
            time.sleep(1)

    def enable_savedsearch(self, addon_name, savedsearch):
        splunk_binding = binding.connect(**self.splunk)
        splunk_binding.post(
            f"/servicesNS/nobody/{addon_name}/saved/searches/{savedsearch}/enable",
            data="",
        )


@pytest.fixture(scope="session")
def splunk_setup(splunk):
    ta_setup = TASetup(splunk)
    time.sleep(30)
    ta_setup.enable_savedsearch("TA_SavedSearch", "ta_saved_search_one")
    ta_setup.wait_for_lookup("ta_saved_search_lookup")
