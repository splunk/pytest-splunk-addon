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
        "--thread-count",
        action="store",
        default=20,
        dest="thread_count",
        help=("Thread count for Data ingestion"),
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


@pytest.fixture(scope="session")
def splunk_ingest_data(request, splunk_setup, sc4s):
    """
    Generates events for the add-on and ingests into Splunk.
    The ingestion can be done using the following methods:
        1. HEC Event
        2. HEC Raw
        3. SC4S:TCP or SC4S:UDP
        4. HEC Metrics

    Args:
    splunk_setup: Splunk Fixture post setup
    sc4s(tuple): Details for sc4s server and TCP port

    TODO: For splunk_type=external, data will not be ingested as
    manual configurations are required.
    """
    global PYTEST_XDIST_TESTRUNUID
    if (
        "PYTEST_XDIST_WORKER" not in os.environ
        or os.environ.get("PYTEST_XDIST_WORKER") == "gw0"
    ):
        addon_path = request.config.getoption("splunk_app")
        config_path = request.config.getoption("splunk_data_generator")

        sc4s_ip, sc4s_port = sc4s.get_service(514)
        splunk_hec_uri = splunk_setup.splunk_hec_uri()
        ingest_meta_data = {
            "session_headers": splunk_hec_uri[0].headers,
            "splunk_hec_uri": splunk_hec_uri[1],
            "sc4s_host": sc4s_ip,
            "sc4s_port": sc4s_port,  # for sc4s
        }
        thread_count = int(request.config.getoption("thread_count"))
        store_events = request.config.getoption("store_events")
        IngestorHelper.ingest_events(
            ingest_meta_data, addon_path, config_path, thread_count, store_events
        )
        sleep(50)
        if "PYTEST_XDIST_WORKER" in os.environ:
            with open(os.environ.get("PYTEST_XDIST_TESTRUNUID") + "_wait", "w+"):
                PYTEST_XDIST_TESTRUNUID = os.environ.get("PYTEST_XDIST_TESTRUNUID")

    else:
        while not os.path.exists(os.environ.get("PYTEST_XDIST_TESTRUNUID") + "_wait"):
            sleep(1)


def pytest_unconfigure(config):
    if PYTEST_XDIST_TESTRUNUID:
        if os.path.exists(PYTEST_XDIST_TESTRUNUID + "_wait"):
            os.remove(PYTEST_XDIST_TESTRUNUID + "_wait")
        if os.path.exists(PYTEST_XDIST_TESTRUNUID + "_events"):
            os.remove(PYTEST_XDIST_TESTRUNUID + "_events")
