import pytest
from splunklib import binding, client, results
import time
import os

pytest_plugins = "pytester"

def pytest_configure(config):
    config.addinivalue_line("markers", "external: Test search time only")
    config.addinivalue_line("markers", "docker: Test search time only")



@pytest.fixture(scope="session")
def docker_compose_files(request):
    """
    Get an absolute path to the  `docker-compose.yml` file. Override this
    fixture in your tests if you need a custom location.

    Returns:
        string: the path of the `docker-compose.yml` file

    """
    docker_compose_path = os.path.join(
        str(request.config.invocation_dir), "docker-compose.yml"
    )
    #LOGGER.info("docker-compose path: %s", docker_compose_path)

    return [docker_compose_path]


class TASetup(object):
    def __init__(self, splunk):
        self.splunk = splunk

    def wait_for_lookup(self, lookup):
        splunk_client = client.connect(**self.splunk)
        for _ in range(30):
            job_result = splunk_client.jobs.oneshot(f" | inputlookup {lookup}")
            for _ in results.ResultsReader(job_result):
                return
            time.sleep(1)

    def enable_savedsearch(self, addon_name, savedsearch):
        splunk_binding = binding.connect(**self.splunk)
        splunk_binding.post(
            f"/servicesNS/nobody/{addon_name}/saved/searches/{savedsearch}/enable"
            , data=''
        )


@pytest.fixture(scope="session")
def splunk_setup(splunk):
    ta_setup = TASetup(splunk)
    ta_setup.enable_savedsearch("TA_SavedSearch", "ta_saved_search_one")
    ta_setup.wait_for_lookup("ta_saved_search_lookup")
