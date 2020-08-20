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
from .standard_lib.event_ingestors import IngestorHelper
import configparser
from filelock import FileLock

RESPONSIVE_SPLUNK_TIMEOUT = 300  # seconds

LOGGER = logging.getLogger("pytest-splunk-addon")
PYTEST_XDIST_TESTRUNUID = ""

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
        "--splunk-hec-scheme",
        action="store",
        dest="splunk_hec_scheme",
        default="https",
        help="Splunk HTTP event collector port. default is https.",
    )
    group.addoption(
        "--splunk-hec-port",
        action="store",
        dest="splunk_hec",
        default="8088",
        help="Splunk HTTP event collector port. default is 8088.",
    )
    group.addoption(
        "--splunk-hec-token",
        action="store",
        dest="splunk_hec_token",
        default="9b741d03-43e9-4164-908b-e09102327d22",
        help='Splunk HTTP event collector token. default is "9b741d03-43e9-4164-908b-e09102327d22".',
    )
    group.addoption(
        "--splunk-port",
        action="store",
        dest="splunkd_port",
        default="8089",
        help="Splunk Management port. default is 8089.",
    )
    group.addoption(
        "--splunk-s2s-port",
        action="store",
        dest="splunk_s2s",
        default="9997",
        help="Splunk s2s port. default is 9997.",
    )
    group.addoption(
        "--splunk-s2s-scheme",
        action="store",
        dest="splunk_s2s_scheme",
        default="tcp",
        help="Splunk s2s scheme. tls|tcp default is tcp.",
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
            " is set to docker. Examples, "
            " 1) latest: latest Splunk Enterprise tagged by the https://github.com/splunk/docker-splunk"
            " 2) 8.0.0: GA release of 8.0.0."
        ),
    )
    group.addoption(
        "--splunk-dm-path",
        action="store",
        dest="splunk_dm_path",
        help=(
            "Path to the datamodels directory"
            "Relative or absolute path can be provided."
            "Json files are expected in the directory."
            "Json files must follow the schema mentioned in DatamodelSchema.json"
            "pytest-splunk-addon\pytest_splunk_addon\standard_lib\cim_tests\DatamodelSchema.json"
        ),
    )
    group.addoption(
        "--splunk-data-generator",
        action="store",
        dest="splunk_data_generator",
        default="pytest-splunk-addon-data.conf",
        help=("Path to pytest-splunk-addon-data.conf."),
    )
    group.addoption(
        "--sc4s-host",
        action="store",
        dest="sc4s_host",
        default="127.0.0.1",
        help="Address of the sc4s Server",
    )
    group.addoption(
        "--sc4s-port",
        action="store",
        dest="sc4s_port",
        default="514",
        help="SC4S Port. default is 514",
    )
    group.addoption(
        "--thread-count",
        action="store",
        default=20,
        dest="thread_count",
        help=(
            "Thread count for Data ingestion"
        ),
    )
    group.addoption(
        "--search-index",
        action="store",
        dest="search_index",
        default="*",
        help="Splunk index of which the events will be searched while testing.",
    )
    group.addoption(
        "--search-retry",
        action="store",
        dest="search_retry",
        default=0,
        type=int,
        help="Number of retries to make if there are no events found while searching in the Splunk instance.",
    )
    group.addoption(
        "--search-interval",
        action="store",
        dest="search_interval",
        default=0,
        type=int,
        help="Time interval to wait before retrying the search query.",
    )
    group.addoption(
        "--cim-report",
        action="store",
        dest="cim_report",
        help="Create a markdown report summarizing CIM compliance. Provide a relative or absolute path where the report should be created",
    )


@pytest.fixture(scope="session")
def splunk_setup(splunk):
    """
    Override this fixture in conftest.py, if any setup is required before the test session.
    splunk fixture can provide the details of the splunk instance in dict format.

    **Possible setups required**:

        1. Enable Saved-searches before running the tests
        2. Restart Splunk
        3. Configure inputs of an Add-on.

    **Example**::

        from splunklib import binding
        @pytest.fixture(scope="session")
        def splunk_setup(splunk):
            splunk_binding = binding.connect(**splunk)
            splunk_binding.post(
                f"/servicesNS/nobody/{addon_name}/saved/searches/{savedsearch}/enable"
                , data=''
            )

    """
    pass


@pytest.fixture(scope="session")
def splunk_search_util(splunk, splunk_setup, request):
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
    search_util = SearchUtil(jobs, LOGGER)
    search_util.search_index = request.config.getoption("search_index")
    search_util.search_retry = request.config.getoption("search_retry")
    search_util.search_interval = request.config.getoption("search_interval")

    return search_util


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
        os.environ["SPLUNK_APP_PACKAGE"] = request.config.getoption("splunk_app")
        try:
            config = configparser.ConfigParser()
            config.read(
                os.path.join(
                    request.config.getoption("splunk_app"), "default", "app.conf",
                )
            )
            os.environ["SPLUNK_APP_ID"] = config["package"]["id"]
        except Exception as e:
            pass
            os.environ["SPLUNK_APP_ID"] = "TA_package"
        os.environ["SPLUNK_HEC_TOKEN"] = request.config.getoption("splunk_hec_token")
        os.environ["SPLUNK_USER"] = request.config.getoption("splunk_user")
        os.environ["SPLUNK_PASSWORD"] = request.config.getoption("splunk_password")
        os.environ["SPLUNK_VERSION"] = request.config.getoption("splunk_version")

        request.fixturenames.append("splunk_docker")
        splunk_info = request.getfixturevalue("splunk_docker")
    else:
        raise Exception

    yield splunk_info


@pytest.fixture(scope="session")
def sc4s(request):
    """
    This fixture based on the passed option will provide a real fixture
    for external or docker sc4s configuration

    Returns:
        tuple: Details of SC4S which includes sc4s server IP and its related ports.
    """
    if request.config.getoption("splunk_type") == "external":
        request.fixturenames.append("sc4s_external")
        sc4s = request.getfixturevalue("sc4s_external")
    elif request.config.getoption("splunk_type") == "docker":
        request.fixturenames.append("sc4s_docker")
        sc4s = request.getfixturevalue("sc4s_docker")
    else:
        raise Exception

    yield sc4s


@pytest.fixture(scope="session")
def splunk_docker(
    request, docker_services, docker_compose_files, tmp_path_factory, worker_id
):
    """
    Splunk docker depends on lovely-pytest-docker to create the docker instance
    of Splunk this may be changed in the future.
    docker-compose.yml in the project root must have
    a service "splunk" exposing port 8000 and 8089

    Returns:
        dict: Details of the splunk instance including host, port, username & password.
    """
    LOGGER.info("Starting docker_service=splunk")

    if worker_id:
        # get the temp directory shared by all workers
        root_tmp_dir = tmp_path_factory.getbasetemp().parent
        fn = root_tmp_dir / "pytest_docker"
        with FileLock(str(fn) + ".lock"):
            if fn.is_file():
                sleep(10)

    docker_services.start("splunk")

    splunk_info = {
        "host": docker_services.docker_ip,
        "port": docker_services.port_for("splunk", 8089),
        "port_hec": docker_services.port_for("splunk", 8088),
        "port_s2s": docker_services.port_for("splunk", 9997),
        "port_web": docker_services.port_for("splunk", 8000),
        "username": request.config.getoption("splunk_user"),
        "password": request.config.getoption("splunk_password"),
    }

    LOGGER.info(
        "Docker container splunk info. host=%s, port=%s, port_web=%s port_hec=%s port_s2s=%s",
        docker_services.docker_ip,
        docker_services.port_for("splunk", 8089),
        docker_services.port_for("splunk", 8088),
        docker_services.port_for("splunk", 8000),
        docker_services.port_for("splunk", 9997),
    )

    docker_services.wait_until_responsive(
        timeout=180.0, pause=0.5, check=lambda: is_responsive_splunk(splunk_info),
    )

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
        "port_hec": request.config.getoption("splunk_hec"),
        "port_s2s": request.config.getoption("splunk_s2s"),
        "port_web": request.config.getoption("splunk_web"),
        "username": request.config.getoption("splunk_user"),
        "password": request.config.getoption("splunk_password"),
    }

    for _ in range(RESPONSIVE_SPLUNK_TIMEOUT):
        if is_responsive_splunk(splunk_info):
            break
        sleep(1)

    if not is_responsive_splunk(splunk_info):
        raise Exception(
            "Could not connect to the external Splunk. "
            "Please check the log file for possible errors."
        )

    return splunk_info


@pytest.fixture(scope="session")
def sc4s_docker(docker_services, tmp_path_factory, worker_id):
    """
    Provides IP of the sc4s server and related ports based on pytest-args(splunk_type)
    """
    if worker_id:
        # get the temp directory shared by all workers
        root_tmp_dir = tmp_path_factory.getbasetemp().parent
        fn = root_tmp_dir / "pytest_docker"
        with FileLock(str(fn) + ".lock"):
            if fn.is_file():
                sleep(10)

    docker_services.start("sc4s")

    ports = {514: docker_services.port_for("sc4s", 514)}
    for x in range(5000, 5007):
        ports.update({x: docker_services.port_for("sc4s", x)})

    return docker_services.docker_ip, ports


@pytest.fixture(scope="session")
def sc4s_external(request):
    """
    Provides IP of the sc4s server and related ports based on pytest-args(splunk_type)
    TODO: For splunk_type=external, data will not be ingested as 
    manual configurations are required.
    """
    ports = {514: int(request.config.getoption("sc4s_port"))}
    for x in range(5000, 5050):
        ports.update({x: x})

    return request.config.getoption("sc4s_host"), ports


@pytest.fixture(scope="session")
def splunk_rest_uri(splunk):
    """
    Provides a uri to the Splunk rest port
    """
    splunk_session = requests.Session()
    splunk_session.auth = (splunk["username"], splunk["password"])
    uri = f'https://{splunk["host"]}:{splunk["port_hec"]}/'
    LOGGER.info("Fetched splunk_rest_uri=%s", uri)

    return splunk_session, uri


@pytest.fixture(scope="session")
def splunk_hec_uri(request, splunk):
    """
    Provides a uri to the Splunk hec port
    """
    splunk_session = requests.Session()
    splunk_session.headers = {
        "Authorization": f'Splunk {request.config.getoption("splunk_hec_token")}'
    }
    uri = f'{request.config.getoption("splunk_hec_scheme")}://{splunk["host"]}:{splunk["port_hec"]}/services/collector'
    LOGGER.info("Fetched splunk_hec_uri=%s", uri)

    return splunk_session, uri


@pytest.fixture(scope="session")
def splunk_web_uri(splunk):
    """
    Provides a uri to the Splunk web port
    """
    uri = f'http://{splunk["host"]}:{splunk["port_web"]}/'
    LOGGER.info("Fetched splunk_web_uri=%s", uri)
    return uri


@pytest.fixture(scope="session")
def splunk_ingest_data(request, splunk_hec_uri, sc4s):
    """
    Generates events for the add-on and ingests into Splunk.
    The ingestion can be done using the following methods:
        1. HEC Event
        2. HEC Raw
        3. SC4S:TCP or SC4S:UDP
        4. HEC Metrics

    Args:
    splunk_hec_uri(tuple): Details for hec uri and session headers
    sc4s(tuple): Details for sc4s server and TCP port

    TODO: For splunk_type=external, data will not be ingested as
    manual configurations are required.
    """
    global PYTEST_XDIST_TESTRUNUID
    if ("PYTEST_XDIST_WORKER" not in os.environ or os.environ.get("PYTEST_XDIST_WORKER") == "gw0"):
        addon_path = request.config.getoption("splunk_app")
        config_path = request.config.getoption("splunk_data_generator")

        ingest_meta_data = {
            "session_headers": splunk_hec_uri[0].headers,
            "splunk_hec_uri": splunk_hec_uri[1],
            "sc4s_host": sc4s[0],  # for sc4s
            "sc4s_port": sc4s[1][514]  # for sc4s
        }
        thread_count = int(request.config.getoption("thread_count"))
        IngestorHelper.ingest_events(ingest_meta_data, addon_path, config_path, thread_count)
        sleep(50)
        if ("PYTEST_XDIST_WORKER" in os.environ):
            with open(os.environ.get("PYTEST_XDIST_TESTRUNUID") + "_wait", "w+"):
                PYTEST_XDIST_TESTRUNUID = os.environ.get("PYTEST_XDIST_TESTRUNUID")

    else:
        while not os.path.exists(os.environ.get("PYTEST_XDIST_TESTRUNUID") + "_wait"):
            sleep(1)


def is_responsive_splunk(splunk):
    """
    Verify if the management port of Splunk is responsive or not

    Args:
        splunk (dict): details of the Splunk instance

    Returns:
        bool: True if Splunk is responsive. False otherwise
    """
    try:
        LOGGER.info(
            "Trying to connect Splunk instance...  splunk=%s", json.dumps(splunk),
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
            "Could not connect to Splunk yet. Will try again. exception=%s", str(e),
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
            "Could not connect to url yet. Will try again. exception=%s", str(e),
        )
        return False

def pytest_unconfigure(config):
    if PYTEST_XDIST_TESTRUNUID:
        if os.path.exists(PYTEST_XDIST_TESTRUNUID + "_wait"):
            os.remove(PYTEST_XDIST_TESTRUNUID + "_wait")
        if os.path.exists(PYTEST_XDIST_TESTRUNUID + "_events"):
            os.remove(PYTEST_XDIST_TESTRUNUID + "_events")
