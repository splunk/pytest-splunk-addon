# -*- coding: utf-8 -*-
"""
Module usage:
- splunk_appinspect: To parse the configuration files from Add-on package
- helmut : To connect to a Splunk instance. source: splunk-sdk
- helmut_lib: Provides various Utility functions to search on Splunk. Source: splunk-sdk
"""

import logging
import os
from time import sleep
import json
import pytest
import requests
import splunklib.client as client
from .helmut.manager.jobs import Jobs
from .helmut.splunk.cloud import CloudSplunk
from .helmut_lib.SearchUtil import SearchUtil

RESPONSIVE_SPLUNK_TIMEOUT = 3600  # seconds

LOGGER = logging.getLogger("pytest_splunk_addon")


def pytest_addoption(parser):
    """Add options for interaction with Splunk this allows the tool to work in two modes
    1) docker mode which is typically used by developers on their workstation
        manages a single instance of splunk
    2) external interacts with a single instance of splunk that is lifecycle managed
        by another process such as a ci/cd pipeline
    """
    group = parser.getgroup("splunk-addon")

    group.addoption(
        "--splunk-app",
        action="store",
        dest="splunk_app",
        default="package",
        help=(
            "Path to Splunk app package. The package should have the "
            "configuration files in the default folder."
        ),
    )
    group.addoption(
        "--splunk-type",
        action="store",
        dest="splunk_type",
        default="external",
        help=(
            "Type of the Splunk instance. supports external & docker "
            "as a value. Default is external."
        ),
    )
    group.addoption(
        "--splunk-host",
        action="store",
        dest="splunk_host",
        default="127.0.0.1",
        help=(
            "Address of the Splunk Server. Do not provide "
            "http scheme in the host. default is 127.0.0.1"
        ),
    )
    group.addoption(
        "--splunk-port",
        action="store",
        dest="splunkd_port",
        default="8089",
        help="Splunk Management port. default is 8089.",
    )
    group.addoption(
        "--splunkweb-port",
        action="store",
        dest="splunk_web",
        default="8000",
        help="Splunk web port. default is 8000.",
    )
    group.addoption(
        "--splunk-user",
        action="store",
        dest="splunk_user",
        default="admin",
        help="Splunk login user. The user should have search capabilities.",
    )
    group.addoption(
        "--splunk-password",
        action="store",
        dest="splunk_password",
        default="Chang3d!",
        help="Password of the Splunk user",
    )
    group.addoption(
        "--splunk-version",
        action="store",
        dest="splunk_version",
        default="latest",
        help=(
            "Splunk version to spin up with docker while splunk-type "
            " is set to docker. Examples, 1) latest: latest Splunk Enterprise"
            " packaged, built from the develop branch. 2) 8.0.0: GA release"
            " of 8.0.0. "
        ),
    )


@pytest.fixture(scope="session")
def docker_compose_files(pytestconfig):
    """
    Get an absolute path to the  `docker-compose.yml` file. Override this
    fixture in your tests if you need a custom location.

    Returns:
        string: the path of the `docker-compose.yml` file

    """
    docker_compose_path = os.path.join(
        str(pytestconfig.invocation_dir), "docker-compose.yml"
    )
    LOGGER.info("docker-compose path: %s", docker_compose_path)

    return [docker_compose_path]


def is_responsive_splunk(splunk):
    """
    Verify if Splunk is responsive or not

    Args:
        splunk (dict): details of the Splunk instance

    Returns:
        bool: True if Splunk is responsive. False otherwise
    """
    try:
        LOGGER.info(
            "Trying to connect Splunk instance...  splunk=%s",
            json.dumps(splunk),
        )
        client.connect(
            username=splunk["username"],
            password=splunk["password"],
            host=splunk["host"],
            port=splunk["port"],
        )
        LOGGER.info("Connected to Splunk instance.")
        return True
    except Exception as e:
        LOGGER.warning(
            "Could not connect to Splunk yet. Will try again. exception=%s",
            str(e),
        )
        return False


def is_responsive(url):
    """
    This function is called to verify the connection is accepted
    used to prevent tests from running before Splunk is ready

    Args:
        url (str): url to check if it's responsive or not

    Returns:
        bool: True if Splunk is responsive. False otherwise
    """
    try:
        LOGGER.info("Trying to connect with url=%s", url)
        response = requests.get(url)
        if response.status_code != 500:
            LOGGER.info("Connected to the url")
            return True
    except ConnectionError as e:
        LOGGER.warning(
            "Could not connect to url yet. Will try again. exception=%s",
            str(e),
        )
        return False


@pytest.fixture(scope="session")
def splunk(request):
    """
    This fixture based on the passed option will provide a real fixture
    for external or docker Splunk

    Returns:
        dict: Details of the splunk instance including host, port, username & password.
    """
    splunk_type = request.config.getoption("splunk_type")
    LOGGER.info("Get the Splunk instance of splunk_type=%s", splunk_type)
    if splunk_type == "external":
        request.fixturenames.append("splunk_external")
        splunk_info = request.getfixturevalue("splunk_external")
    elif splunk_type == "docker":

        os.environ["SPLUNK_USER"] = request.config.getoption("splunk_user")
        os.environ["SPLUNK_PASSWORD"] = request.config.getoption(
            "splunk_password"
        )
        os.environ["SPLUNK_VERSION"] = request.config.getoption(
            "splunk_version"
        )

        request.fixturenames.append("splunk_docker")
        splunk_info = request.getfixturevalue("splunk_docker")
    else:
        raise Exception

    yield splunk_info


@pytest.fixture(scope="session")
def splunk_docker(request, docker_services):
    """
    Splunk docker depends on lovely-pytest-docker to create the docker instance
    of Splunk this may be changed in the future.
    docker-compose.yml in the project root must have
    a service "splunk" exposing port 8000 and 8089

    Returns:
        dict: Details of the splunk instance including host, port, username & password.
    """
    LOGGER.info("Starting docker_service=splunk")
    docker_services.start("splunk")

    splunk_info = {
        "host": docker_services.docker_ip,
        "port": docker_services.port_for("splunk", 8089),
        "port_web": docker_services.port_for("splunk", 8000),
        "username": request.config.getoption("splunk_user"),
        "password": request.config.getoption("splunk_password"),
    }

    LOGGER.info(
        "Docker container splunk info. host=%s, port=%s, port_web-%s",
        docker_services.docker_ip,
        docker_services.port_for("splunk", 8089),
        docker_services.port_for("splunk", 8000),
    )

    for _ in range(30):
        docker_services.wait_until_responsive(
            timeout=180.0,
            pause=0.5,
            check=lambda: is_responsive_splunk(splunk_info),
        )
        sleep(1)

    return splunk_info


@pytest.fixture(scope="session")
def splunk_external(request):
    """
    This fixture provides the connection properties to Splunk based on the pytest args

    Returns:
        dict: Details of the splunk instance including host, port, username & password.
    """
    splunk_info = {
        "host": request.config.getoption("splunk_host"),
        "port": request.config.getoption("splunkd_port"),
        "port_web": request.config.getoption("splunk_web"),
        "username": request.config.getoption("splunk_user"),
        "password": request.config.getoption("splunk_password"),
    }

    for _ in range(RESPONSIVE_SPLUNK_TIMEOUT):
        if is_responsive_splunk(splunk_info):
            break
        sleep(1)
    else:
        raise Exception(
            "Could not connect to the external Splunk. "
            "Please check the log file for possible errors."
        )

    return splunk_info


@pytest.fixture(scope="session")
def splunk_search_util(splunk):
    """
    This is a simple connection to Splunk via the SplunkSDK

    Returns:
        helmut_lib.SearchUtil.SearchUtil: The SearchUtil object
    """
    LOGGER.info("Initializing SearchUtil for the Splunk instace.")
    cloud_splunk = CloudSplunk(
        splunkd_host=splunk["host"],
        splunkd_port=splunk["port"],
        username=splunk["username"],
        password=splunk["password"],
    )

    conn = cloud_splunk.create_logged_in_connector()
    jobs = Jobs(conn)
    LOGGER.info("initialized SearchUtil for the Splunk instace.")

    return SearchUtil(jobs, LOGGER)


@pytest.fixture(scope="session")
def splunk_rest_uri(splunk):
    """
    Provides a uri to the Splunk rest port
    """
    splunk_session = requests.Session()
    splunk_session.auth = (splunk["username"], splunk["password"])
    uri = f'https://{splunk["host"]}:{splunk["port"]}/'
    LOGGER.info("Fetched splunk_rest_uri=%s", uri)

    return splunk_session, uri


@pytest.fixture(scope="session")
def splunk_web_uri(splunk):
    """
    Provides a uri to the Splunk web port
    """
    uri = f'http://{splunk["host"]}:{splunk["port_web"]}/'
    LOGGER.info("Fetched splunk_web_uri=%s", uri)
    return uri
