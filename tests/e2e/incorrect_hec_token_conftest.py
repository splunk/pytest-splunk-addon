import os
import pytest
import requests

pytest_plugins = "pytester"


def pytest_configure(config):
    config.addinivalue_line("markers", "external: Test search time only")
    config.addinivalue_line("markers", "docker: Test search time only")
    config.addinivalue_line("markers", "doc: Test Sphinx docs")


@pytest.fixture(scope="session")
def docker_compose_file(request):
    """
    Get an absolute path to the  `docker-compose.yml` file. Override this
    fixture in your tests if you need a custom location.

    Returns:
        string: the path of the `docker-compose.yml` file

    """
    docker_compose_path = os.path.join(
        str(request.config.invocation_dir), "docker-compose.yml"
    )
    # LOGGER.info("docker-compose path: %s", docker_compose_path)

    return [docker_compose_path]


@pytest.fixture(scope="session")
def docker_services_project_name(pytestconfig):
    rootdir = str(pytestconfig.rootdir)
    docker_compose_v2_rootdir = rootdir.lower().replace("/", "")
    return f"pytest{docker_compose_v2_rootdir}"


@pytest.fixture(scope="session")
def splunk_hec_uri(splunk, request):
    splunk_session = requests.Session()
    splunk_session.headers = {"Authorization": f"Splunk test-token"}
    uri = f'{request.config.getoption("splunk_hec_scheme")}://{splunk["forwarder_host"]}:{splunk["port_hec"]}/services/collector'
    return splunk_session, uri
