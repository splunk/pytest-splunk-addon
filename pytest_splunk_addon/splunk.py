#
# Copyright 2021 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import logging
import os
import shutil
from collections import defaultdict
from time import sleep
import json
import pytest
import requests
import splunklib.client as client
from splunksplwrapper.manager.jobs import Jobs
from splunksplwrapper.splunk.cloud import CloudSplunk
from splunksplwrapper.SearchUtil import SearchUtil
from .standard_lib.event_ingestors import IngestorHelper
from .standard_lib.CIM_Models.datamodel_definition import datamodels
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
            "Address of the Splunk Server where search queries will be executed. Do not provide "
            "http scheme in the host. default is 127.0.0.1"
        ),
    )
    group.addoption(
        "--splunk-forwarder-host",
        action="store",
        dest="splunk_forwarder_host",
        help=(
            "Address of the Splunk Forwarder Server. Do not provide "
            "http scheme in the host."
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
        "--splunk-web-scheme",
        action="store",
        dest="splunk_web_scheme",
        default="http",
        help="Enable SSL (HTTPS) in Splunk Web? default is http.",
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
        help="Splunk HTTP event collector token. If an external forwarder is used provide HEC token of forwarder. Please specify it as default value is going to be deprecated.",
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
        "--sc4s-version",
        action="store",
        dest="sc4s_version",
        default="latest",
        help="SC4S version. default is latest",
    )
    group.addoption(
        "--thread-count",
        action="store",
        default=20,
        dest="thread_count",
        help=("Thread count for Data ingestion"),
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
    group.addoption(
        "--discard-eventlogs",
        action="store_false",
        dest="store_events",
        help="Avoids generation of the json files with the tokenised events in the working directory.",
    )

    group.addoption(
        "--splunk-cleanup",
        action="store_true",
        dest="splunk_cleanup",
        help="Enable a Splunk env cleanup (events deletion) before running tests.",
    )
    group.addoption(
        "--ignore-addon-errors",
        action="store",
        dest="ignore_addon_errors",
        help=("Path to file where list of addon related errors are suppressed."),
    )
    group.addoption(
        "--ignore-errors-not-related-to-addon",
        action="store",
        dest="ignore_errors_not_related_to_addon",
        help=("Path to file where list of errors not related to addon are suppressed."),
    )
    group.addoption(
        "--splunk-uf-host",
        action="store",
        dest="splunk_uf_host",
        default="uf",
        help="Address of Universal Forwarder Server.",
    )
    group.addoption(
        "--splunk-uf-port",
        action="store",
        dest="splunk_uf_port",
        default="8089",
        help="Universal Forwarder Management port. default is 8089.",
    )
    group.addoption(
        "--splunk-uf-user",
        action="store",
        dest="splunk_uf_user",
        default="admin",
        help="Universal Forwarder login user.",
    )
    group.addoption(
        "--splunk-uf-password",
        action="store",
        dest="splunk_uf_password",
        default="Chang3d!",
        help="Password of the Universal Forwarder user",
    )
    group.addoption(
        "--event-file-path",
        action="store",
        dest="event_path",
        help="Path to tokenised event directory",
        default="events.pickle",
    )
    group.addoption(
        "--tokenized-event-source",
        action="store",
        dest="tokenized_event_source",
        help="One of (new|pregenerated|store_new)",
        default="store_new",
    )
    group.addoption(
        "--ingest-events",
        action="store",
        dest="ingest_events",
        help="Should ingest events or not (True|False)",
        default="True",
    )
    group.addoption(
        "--execute-test",
        action="store",
        dest="execute_test",
        help="Should execute test or not (True|False)",
        default="True",
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
def splunk_search_util(splunk, request):
    """
    This is a simple connection to Splunk via the SplunkSDK

    Returns:
        splunksplwrapper.SearchUtil.SearchUtil: The SearchUtil object
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
def ignore_internal_errors(request):
    """
    This fixture generates a common list of errors which are suppossed
    to be ignored in test_splunk_internal_errors.

    Returns:
        dict: List of the strings to be ignored in test_splunk_internal_errors
    """
    error_list = []
    splunk_error_file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), ".ignore_splunk_internal_errors"
    )
    with open(splunk_error_file_path) as splunk_errors:
        error_list = [each_error.strip() for each_error in splunk_errors.readlines()]
    if request.config.getoption("ignore_addon_errors"):
        addon_error_file_path = request.config.getoption("ignore_addon_errors")
        if os.path.exists(addon_error_file_path):
            with open(addon_error_file_path, "r") as addon_errors:
                error_list.extend(
                    [each_error.strip() for each_error in addon_errors.readlines()]
                )
    if request.config.getoption("ignore_errors_not_related_to_addon"):
        file_path = request.config.getoption("ignore_errors_not_related_to_addon")
        if os.path.exists(file_path):
            with open(file_path, "r") as non_ta_errors:
                error_list.extend(
                    [each_error.strip() for each_error in non_ta_errors.readlines()]
                )

    yield error_list


@pytest.fixture(scope="session")
def splunk(request, file_system_prerequisite):
    """
    This fixture based on the passed option will provide a real fixture
    for external or docker Splunk

    Returns:
        dict: Details of the splunk instance including host, port, username & password.
    """
    splunk_type = request.config.getoption("splunk_type")
    LOGGER.info("Get the Splunk instance of splunk_type=%s", splunk_type)
    splunk_fixture = f"splunk_{splunk_type}"
    try:
        request.fixturenames.append(splunk_fixture)
        splunk_info = request.getfixturevalue(splunk_fixture)
    except Exception as e:
        raise Exception(f"Failed to get Splunk fixture ({splunk_fixture}): {e}")

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
def uf(request):
    """
    This fixture based on the passed option will provide a real fixture
    for external or docker uf configuration

    Returns:
        dict: Details of uf which includes host, port, username and password
    """
    if request.config.getoption("splunk_type") == "external":
        request.fixturenames.append("uf_external")
        uf = request.getfixturevalue("uf_external")
    elif request.config.getoption("splunk_type") == "docker":
        request.fixturenames.append("uf_docker")
        uf = request.getfixturevalue("uf_docker")
    else:
        raise Exception
    yield uf


@pytest.fixture(scope="session")
def uf_docker(docker_services, tmp_path_factory, worker_id, request):
    """
    Provides IP of the uf server and management port based on pytest-args(splunk_type)
    """
    LOGGER.info("Starting docker_service=uf")
    os.environ["CURRENT_DIR"] = os.getcwd()
    if worker_id:
        # get the temp directory shared by all workers
        root_tmp_dir = tmp_path_factory.getbasetemp().parent
        fn = root_tmp_dir / "pytest_docker"
        with FileLock(str(fn) + ".lock"):
            docker_services.start("uf")
    uf_info = {
        "uf_host": docker_services.docker_ip,
        "uf_port": docker_services.port_for("uf", 8089),
        "uf_username": request.config.getoption("splunk_uf_user"),
        "uf_password": request.config.getoption("splunk_uf_password"),
    }
    for _ in range(RESPONSIVE_SPLUNK_TIMEOUT):
        if is_responsive_uf(uf_info):
            break
        sleep(1)
    return uf_info


@pytest.fixture(scope="session")
def uf_external(request):
    """
    Provides IP of the uf server and management port based on pytest-args(splunk_type)
    """
    uf_info = {
        "uf_host": request.config.getoption("splunk_uf_host"),
        "uf_port": request.config.getoption("splunk_uf_port"),
        "uf_username": request.config.getoption("splunk_uf_user"),
        "uf_password": request.config.getoption("splunk_uf_password"),
    }
    return uf_info


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
    # configuration of environment variables needed by docker-compose file
    os.environ["SPLUNK_APP_PACKAGE"] = request.config.getoption("splunk_app")
    try:
        config = configparser.ConfigParser()
        config.read(
            os.path.join(
                request.config.getoption("splunk_app"),
                "default",
                "app.conf",
            )
        )
        os.environ["SPLUNK_APP_ID"] = config["package"]["id"]
    except Exception:
        os.environ["SPLUNK_APP_ID"] = "TA_package"
    os.environ["SPLUNK_HEC_TOKEN"] = request.config.getoption("splunk_hec_token")
    os.environ["SPLUNK_USER"] = request.config.getoption("splunk_user")
    os.environ["SPLUNK_PASSWORD"] = request.config.getoption("splunk_password")
    os.environ["SPLUNK_VERSION"] = request.config.getoption("splunk_version")
    os.environ["SC4S_VERSION"] = request.config.getoption("sc4s_version")

    LOGGER.info("Starting docker_service=splunk")
    if worker_id:
        # get the temp directory shared by all workers
        root_tmp_dir = tmp_path_factory.getbasetemp().parent
        fn = root_tmp_dir / "pytest_docker"
        # if you encounter docker-compose not found modify shell path in your IDE to use /bin/bash
        with FileLock(str(fn) + ".lock"):
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

    splunk_info["forwarder_host"] = splunk_info.get("host")

    LOGGER.info(
        "Docker container splunk info. host=%s, port=%s, port_web=%s port_hec=%s port_s2s=%s",
        docker_services.docker_ip,
        docker_services.port_for("splunk", 8089),
        docker_services.port_for("splunk", 8088),
        docker_services.port_for("splunk", 8000),
        docker_services.port_for("splunk", 9997),
    )

    for _ in range(RESPONSIVE_SPLUNK_TIMEOUT):
        if is_responsive_splunk(splunk_info) and is_responsive_hec(
            request, splunk_info
        ):
            break
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
        "port_hec": request.config.getoption("splunk_hec"),
        "port_s2s": request.config.getoption("splunk_s2s"),
        "port_web": request.config.getoption("splunk_web"),
        "host": request.config.getoption("splunk_host"),
        "port": request.config.getoption("splunkd_port"),
        "username": request.config.getoption("splunk_user"),
        "password": request.config.getoption("splunk_password"),
    }
    if not request.config.getoption("splunk_forwarder_host"):
        splunk_info["forwarder_host"] = splunk_info.get("host")
    else:
        splunk_info["forwarder_host"] = request.config.getoption(
            "splunk_forwarder_host"
        )

    for _ in range(RESPONSIVE_SPLUNK_TIMEOUT):
        if is_responsive_splunk(splunk_info) and is_responsive_hec(
            request, splunk_info
        ):
            break
        sleep(1)

    if not is_responsive_splunk(splunk_info):
        raise Exception(
            "Could not connect to the external Splunk Instance"
            "Please check the log file for possible errors."
        )
    if not is_responsive_hec(request, splunk_info):
        raise Exception(
            "Could not connect to Splunk HEC"
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
    uri = f'https://{splunk["host"]}:{splunk["port"]}/'
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
    uri = f'{request.config.getoption("splunk_hec_scheme")}://{splunk["forwarder_host"]}:{splunk["port_hec"]}/services/collector'
    LOGGER.info("Fetched splunk_hec_uri=%s", uri)

    return splunk_session, uri


@pytest.fixture(scope="session")
def splunk_web_uri(request, splunk):
    """
    Provides a uri to the Splunk web port
    """
    uri = f'{request.config.getoption("splunk_web_scheme")}://{splunk["host"]}:{splunk["port_web"]}/'
    LOGGER.info("Fetched splunk_web_uri=%s", uri)
    return uri


@pytest.fixture(scope="session")
def splunk_ingest_data(request, splunk_hec_uri, sc4s, uf, splunk_events_cleanup):
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
        splunk_clear_eventdata: Unused but required to ensure fixture deleting all events will be run before ingesting new events

    TODO:
        For splunk_type=external, data will not be ingested as manual configurations are required.
    """
    if request.config.getoption("ingest_events").lower() in ["n", "no", "false", "f"]:
        return
    global PYTEST_XDIST_TESTRUNUID
    if (
        "PYTEST_XDIST_WORKER" not in os.environ
        or os.environ.get("PYTEST_XDIST_WORKER") == "gw0"
    ):
        addon_path = request.config.getoption("splunk_app")
        config_path = request.config.getoption("splunk_data_generator")
        ingest_meta_data = {
            "uf_host": uf.get("uf_host"),
            "uf_port": uf.get("uf_port"),
            "uf_username": uf.get("uf_username"),
            "uf_password": uf.get("uf_password"),
            "session_headers": splunk_hec_uri[0].headers,
            "splunk_hec_uri": splunk_hec_uri[1],
            "sc4s_host": sc4s[0],  # for sc4s
            "sc4s_port": sc4s[1][514],  # for sc4s
        }
        thread_count = int(request.config.getoption("thread_count"))
        store_events = request.config.getoption("store_events")
        IngestorHelper.ingest_events(
            ingest_meta_data,
            addon_path,
            config_path,
            thread_count,
            store_events,
        )
        sleep(50)
        if "PYTEST_XDIST_WORKER" in os.environ:
            with open(os.environ.get("PYTEST_XDIST_TESTRUNUID") + "_wait", "w+"):
                PYTEST_XDIST_TESTRUNUID = os.environ.get("PYTEST_XDIST_TESTRUNUID")

    else:
        while not os.path.exists(os.environ.get("PYTEST_XDIST_TESTRUNUID") + "_wait"):
            sleep(1)


@pytest.fixture(scope="session")
def splunk_events_cleanup(request, splunk_search_util):
    """
    Deletes all events from all indexes to ensure tests are being run on clean environment.

    Note that events are hidden from search but they are still available on disk according to
    `Splunk doc <https://docs.splunk.com/Documentation/Splunk/8.0.6/Indexer/RemovedatafromSplunk#How_to_delete>`_

    Args:
        splunk_search_util: Other fixture preparing connection to Splunk Search.

    """
    if request.config.getoption("splunk_cleanup"):
        LOGGER.info("Running the old events cleanup")
        splunk_search_util.deleteEventsFromIndex()
    else:
        LOGGER.info("Events cleanup was disabled.")


@pytest.fixture(scope="session")
def file_system_prerequisite():
    """
    File system prerequisite before running tests.
    Creating uf_files directory to write tokenized events for uf_file_monitor input.
    """
    UF_FILE_MONTOR_DIR = "uf_files"
    monitor_dir = os.path.join(os.getcwd(), UF_FILE_MONTOR_DIR)
    if (
        "PYTEST_XDIST_WORKER" not in os.environ
        or os.environ.get("PYTEST_XDIST_WORKER") == "gw0"
    ):
        if os.path.exists(monitor_dir):
            shutil.rmtree(monitor_dir, ignore_errors=True)
        os.mkdir(monitor_dir)


@pytest.fixture(scope="session")
def splunk_dm_recommended_fields():
    """
    Returns function which gets recommended fields from Splunk for given datamodel

    Note that data is being dynamically retrieved from Splunk. When CIM add-on version changes
    retrieved data may differ
    """
    recommended_fields = defaultdict(list)

    def update_recommended_fields(model, datasets, cim_version):
        model_key = f"{cim_version}:{model}:{':'.join(datasets)}".strip(":")

        if model_key not in recommended_fields:
            LOGGER.info(f"Fetching {model_key} definition")
            datamodel_per_cim = datamodels.get(cim_version) or datamodels["latest"]
            datamodel = datamodel_per_cim.get(model, {})
            if datamodel == {}:
                LOGGER.info(f"No recommended fields for {model}")
            for object_name, value in datamodel.items():
                if (
                    object_name == "BaseEvent"
                    or object_name in datasets
                    or object_name == model
                ):
                    recommended_fields[model_key] += value

        return recommended_fields

    return update_recommended_fields


def is_responsive_uf(uf):
    """
    Verify if the management port of Universal Forwarder is responsive or not

    Args:
        uf (dict): details of the Universal Forwarder instance

    Returns:
        bool: True if Universal Forwarder is responsive. False otherwise
    """
    try:
        LOGGER.info(
            "Trying to connect Universal Forwarder instance...  splunk=%s",
            json.dumps(uf),
        )
        client.connect(
            username=uf["uf_username"],
            password=uf["uf_password"],
            host=uf["uf_host"],
            port=uf["uf_port"],
        )
        LOGGER.info("Connected to Universal Forwarder instance.")

        return True
    except Exception as e:
        LOGGER.warning(
            "Could not connect to Universal Forwarder Instance. Will try again. exception=%s",
            str(e),
        )
        return False


def is_responsive_splunk(splunk):
    """
    Verify if the management port of Splunk is responsive or not.

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
            "Could not connect to Splunk Instance. Will try again. exception=%s",
            str(e),
        )
        return False


def is_responsive_hec(request, splunk):
    """
    Verify if the hec port of Splunk is responsive or not

    Args:
        splunk (dict): details of the Splunk instance

    Returns:
        bool: True if Splunk HEC is responsive. False otherwise
    """
    try:
        LOGGER.info(
            "Trying to connect Splunk HEC...  splunk=%s",
            json.dumps(splunk),
        )
        response = requests.get(  # nosemgrep: splunk.disabled-cert-validation
            f'{request.config.getoption("splunk_hec_scheme")}://{splunk["forwarder_host"]}:{splunk["port_hec"]}/services/collector/health/1.0',
            verify=False,
        )
        LOGGER.debug("Status code: {}".format(response.status_code))
        if response.status_code in (200, 201):
            LOGGER.info("Splunk HEC is responsive.")
            return True
        return False
    except Exception as e:
        LOGGER.warning(
            "Could not connect to Splunk HEC. Will try again. exception=%s",
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


def pytest_unconfigure(config):
    if PYTEST_XDIST_TESTRUNUID:
        if os.path.exists(PYTEST_XDIST_TESTRUNUID + "_wait"):
            os.remove(PYTEST_XDIST_TESTRUNUID + "_wait")
        if os.path.exists(PYTEST_XDIST_TESTRUNUID + "_events"):
            os.remove(PYTEST_XDIST_TESTRUNUID + "_events")
