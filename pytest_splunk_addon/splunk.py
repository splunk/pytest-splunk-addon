import logging
import os
import pytest
import requests
from splunk_appinspect import App

from .helmut.manager.jobs import Jobs
from .helmut.splunk.cloud import CloudSplunk
from .helmut_lib.SearchUtil import SearchUtil

import pytest
import requests
import urllib3
import splunklib.client as client
from time import sleep
import re

logger = logging.getLogger()


def pytest_addoption(parser):
    """Add options for interaction with Splunk this allows the tool to work in two modes
    docker mode which is typically used by developers on their workstation manages a single instance of splunk
    external interacts with a single instance of splunk that is lifecycle managed by another process such as a ci/cd pipeline    
    """
    group = parser.getgroup("splunk-addon")

    group.addoption(
        "--splunk_app",
        action="store",
        dest="splunk_app",
        default="package",
        help="Path to Splunk app",
    )
    group.addoption(
        "--splunk_type",
        action="store",
        dest="splunk_type",
        default="external",
        help="Type of Splunk",
    )
    group.addoption(
        "--splunk_host",
        action="store",
        dest="splunk_host",
        default="127.0.0.1",
        help="Address of the Splunk Server",
    )
    group.addoption(
        "--splunk_port",
        action="store",
        dest="splunk_port",
        default="8089",
        help="Splunk rest port",
    )
    group.addoption(
        "--splunk_web",
        action="store",
        dest="splunk_web",
        default="8000",
        help="Splunk web port",
    )
    group.addoption(
        "--splunk_user",
        action="store",
        dest="splunk_user",
        default="admin",
        help="Splunk login user",
    )
    group.addoption(
        "--splunk_password",
        action="store",
        dest="splunk_password",
        default="Changed@11",
        help="Splunk password",
    )
    group.addoption(
        "--splunk_version",
        action="store",
        dest="splunk_version",
        default="latest",
        help="Splunk version",
    )


@pytest.fixture(scope="session")
def docker_compose_files(pytestconfig):
    """Get an absolute path to the  `docker-compose.yml` file. Override this
    fixture in your tests if you need a custom location."""
    print(os.path.join(str(pytestconfig.invocation_dir), "docker-compose.yml"))

    return [os.path.join(str(pytestconfig.invocation_dir), "docker-compose.yml")]


def is_responsive_splunk(splunk):
    try:
        client.connect(
            username=splunk["username"],
            password=splunk["password"],
            host=splunk["host"],
            port=splunk["port"],
        )
        return True
    except Exception:
        return False


def is_responsive(url):
    """This function is called to verify the connection is accepted used to prevent tests from running before Splunk is ready """
    try:
        response = requests.get(url)
        if response.status_code != 500:
            return True
    except ConnectionError:
        return False


@pytest.fixture(scope="session")
def splunk(request):
    """
    This fixture based on the passed option will provide a real fixture for external or docker Splunk
    """
    if request.config.getoption("splunk_type") == "external":
        request.fixturenames.append("splunk_external")
        splunk = request.getfixturevalue("splunk_external")
    elif request.config.getoption("splunk_type") == "docker":

        os.environ["SPLUNK_USER"] = request.config.getoption("splunk_user")
        os.environ["SPLUNK_PASSWORD"] = request.config.getoption("splunk_password")
        os.environ["SPLUNK_VERSION"] = request.config.getoption("splunk_version")

        request.fixturenames.append("splunk_docker")
        splunk = request.getfixturevalue("splunk_docker")
    else:
        raise Exception

    yield splunk


@pytest.fixture(scope="session")
def splunk_docker(request, docker_services):
    """
    Splunk docker depends on lovely-pytest-docker to create the docker instance of Splunk this may be changed in the future
    docker-compose.yml in the project root must have a service "splunk" exposing port 8000 and 8089
    """
    docker_services.start("splunk")

    splunk = {
        "host": docker_services.docker_ip,
        "port": docker_services.port_for("splunk", 8089),
        "port_web": docker_services.port_for("splunk", 8000),
        "username": request.config.getoption("splunk_user"),
        "password": request.config.getoption("splunk_password"),
    }
    c = 0
    while c < 30:
        c += 1
        docker_services.wait_until_responsive(
            timeout=180.0, pause=0.5, check=lambda: is_responsive_splunk(splunk)
        )
        sleep(1)

    return splunk


@pytest.fixture(scope="session")
def splunk_external(request):
    """
    This fixture provides the connection properties to Splunk based on the pytest args
    """
    splunk = {
        "host": request.config.getoption("splunk_host"),
        "port": request.config.getoption("splunk_port"),
        "port_web": request.config.getoption("splunk_web"),
        "username": request.config.getoption("splunk_user"),
        "password": request.config.getoption("splunk_password"),
    }

    while not is_responsive_splunk(splunk):
        sleep(1)

    return splunk


@pytest.fixture(scope="session")
def splunk_search_util(splunk):
    """
    This is a simple connection to Splunk via the SplunkSDK
    """
    cs = CloudSplunk(
        splunkd_host=splunk["host"],
        splunkd_port=splunk["port"],
        username=splunk["username"],
        password=splunk["password"],
    )

    conn = cs.create_logged_in_connector()
    jobs = Jobs(conn)

    return SearchUtil(jobs, logger)


@pytest.fixture(scope="session")
def splunk_rest_uri(splunk):
    """
    Provides a uri to the Splunk rest port
    """
    s = requests.Session()
    s.auth = (splunk["username"], splunk["password"])
    uri = f'https://{splunk["host"]}:{splunk["port"]}/'

    return s, uri


@pytest.fixture(scope="session")
def splunk_web_uri(splunk):
    """
    Provides a uri to the Splunk web port
    """
    uri = f'http://{splunk["host"]}:{splunk["port_web"]}/'

    return uri
