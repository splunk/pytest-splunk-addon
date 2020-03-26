# -*- coding: utf-8 -*-
import os
import shutil
import logging
import pytest

logger = logging.getLogger("test_pytest_splunk_addon")

test_connection_only = """
        def test_connection_splunk(splunk_search_util):
            search = "search (index=_internal) | head 5"

             # run search
            result = splunk_search_util.checkQueryCountIsGreaterThanZero(
                search,
                interval=1, retries=1)
            assert result
    """


@pytest.mark.external
def test_splunk_connection_external(testdir):
    """Make sure that pytest accepts our fixture."""

    # create a temporary pytest test module
    testdir.makepyfile(test_connection_only)

    # Copy the content of source to destination
    shutil.copytree(
        os.path.join(testdir.request.fspath.dirname, "addons/TA_fiction"),
        os.path.join(testdir.tmpdir, "tests/package"),
    )

    # run pytest with the following cmd args
    result = testdir.runpytest(
        "--splunk-type=external",
        "--splunk-app=tests/package",
        "--splunk-type=external",
        f"--splunk-host=splunk",
        f"--splunk-port=8089",
        "--splunk-password=Changed@11",
        "-v",
    )

    # fnmatch_lines does an assertion internally
    logger.info(
        "Result from the test execution: \nstdout=%s\nstderr=%s",
        "\n".join(result.stdout.lines),
        "\n".join(result.stderr.lines),
    )
    result.assert_outcomes(passed=1, failed=0)

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


@pytest.mark.docker
def test_splunk_connection_docker(testdir):
    """Make sure that pytest accepts our fixture."""

    # create a temporary pytest test module
    testdir.makepyfile(test_connection_only)

    # Copy the content of source to destination

    shutil.copytree(
        os.path.join(testdir.request.fspath.dirname, "addons/TA_fiction"),
        os.path.join(testdir.tmpdir, "tests/package"),
    )

    shutil.copy(
        os.path.join(testdir.request.fspath.dirname, "Dockerfile"),
        os.path.join(testdir.tmpdir, "tests/"),
    )
    shutil.copy(
        os.path.join(testdir.request.fspath.dirname, "docker-compose.yml"),
        os.path.join(testdir.tmpdir, "tests/"),
    )
    # run pytest with the following cmd args
    result = testdir.runpytest(
        "--splunk-type=docker",
        "--splunk-app=tests/package",
        "--splunk-password=Changed@11",
        "-v",
    )

    # fnmatch_lines does an assertion internally
    logger.info(
        "Result from the test execution: \nstdout=%s\nstderr=%s",
        "\n".join(result.stdout.lines),
        "\n".join(result.stderr.lines),
    )
    result.assert_outcomes(passed=1, failed=0)

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


@pytest.mark.docker
def test_splunk_app_fiction(testdir):
    """Make sure that pytest accepts our fixture."""

    testdir.makepyfile(
        """
        from pytest_splunk_addon.standard_lib.addon_basic import Basic
        class Test_App(Basic):
            def empty_method():
                pass

    """
    )

    shutil.copytree(
        os.path.join(testdir.request.fspath.dirname, "addons/TA_fiction"),
        os.path.join(testdir.tmpdir, "tests/package"),
    )

    shutil.copy(
        os.path.join(testdir.request.fspath.dirname, "Dockerfile"),
        os.path.join(testdir.tmpdir, "tests/"),
    )
    shutil.copy(
        os.path.join(testdir.request.fspath.dirname, "docker-compose.yml"),
        os.path.join(testdir.tmpdir, "tests/"),
    )
    # run pytest with the following cmd args
    result = testdir.runpytest(
        "--splunk-type=docker",
        "--splunk-app=tests/package",
        "--splunk-password=Changed@11",
        "-v",
    )

    logger.info(
        "Result from the test execution: \nstdout=%s\nstderr=%s",
        "\n".join(result.stdout.lines),
        "\n".join(result.stderr.lines),
    )
    result.assert_outcomes(passed=10, failed=0)

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


@pytest.mark.docker
def test_splunk_app_broken_sourcetype(testdir):
    """Make sure that pytest accepts our fixture."""

    testdir.makepyfile(
        """
        from pytest_splunk_addon.standard_lib.addon_basic import Basic
        class Test_App(Basic):
            def empty_method():
                pass

    """
    )

    shutil.copytree(
        os.path.join(testdir.request.fspath.dirname, "addons/TA_broken_sourcetype"),
        os.path.join(testdir.tmpdir, "tests/package"),
    )

    shutil.copy(
        os.path.join(testdir.request.fspath.dirname, "Dockerfile"),
        os.path.join(testdir.tmpdir, "tests/"),
    )
    shutil.copy(
        os.path.join(testdir.request.fspath.dirname, "docker-compose.yml"),
        os.path.join(testdir.tmpdir, "tests/"),
    )

    # run pytest with the following cmd args
    result = testdir.runpytest(
        "--splunk-type=docker",
        "--splunk-app=tests/package",
        "--splunk-password=Changed@11",
        "-v",
    )

    # fnmatch_lines does an assertion internally
    logger.info(
        "Result from the test execution: \nstdout=%s\nstderr=%s",
        "\n".join(result.stdout.lines),
        "\n".join(result.stderr.lines),
    )
    result.assert_outcomes(passed=4, failed=4)

    # The test suite should fail as this is a negative test
    assert result.ret != 0


def test_help_message(testdir):
    result = testdir.runpytest("--help",)
    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines(
        [
            "splunk-addon:",
            "*--splunk-app=*",
            "*--splunk-host=*",
            "*--splunk-port=*",
            "*--splunk-user=*",
            "*--splunk-password=*",
        ]
    )
