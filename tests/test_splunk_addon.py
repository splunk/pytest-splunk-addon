# -*- coding: utf-8 -*-
import os
import shutil
import pytest
from flaky import flaky

test_connection_only = """
        def test_connection_splunk(splunk_search_util):
            search = "search (index=_internal) | head 5"

             # run search
            result = splunk_search_util.checkQueryCountIsGreaterThanZero(
                search,
                interval=1, retries=1)
            assert result
    """


@pytest.mark.xfail()
def test_splunk_connection_external(testdir):
    """Make sure that pytest accepts our fixture."""

    # create a temporary pytest test module
    testdir.makepyfile(test_connection_only)

    # Copy the content of
    # source to destination

    destination = shutil.copytree(
        os.path.join(testdir.request.fspath.dirname, 'addons/TA_fiction'),
        os.path.join(testdir.tmpdir, 'tests/package')
    )

    # run pytest with the following cmd args
    result = testdir.runpytest(
        '--splunk_type=external',
        '--splunk_app=tests/package',
        '--splunk_type=external',
        f'--splunk_host=127.0.0.1',
        f'--splunk_port=8089',
        '--splunk_password=Changed@11',
        '-v'
    )

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        '*::test_connection_splunk PASSED*',
    ])

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


def test_splunk_connection_docker(testdir):
    """Make sure that pytest accepts our fixture."""

    # create a temporary pytest test module
    testdir.makepyfile(test_connection_only)

    # Copy the content of
    # source to destination

    destination = shutil.copytree(
        os.path.join(testdir.request.fspath.dirname, 'addons/TA_fiction'),
        os.path.join(testdir.tmpdir, 'tests/package')
    )

    destination = shutil.copy(
        os.path.join(testdir.request.fspath.dirname, 'Dockerfile'),
        os.path.join(testdir.tmpdir, 'tests/')
    )
    destination = shutil.copy(
        os.path.join(testdir.request.fspath.dirname, 'docker-compose.yml'),
        os.path.join(testdir.tmpdir, 'tests/')
    )
    # run pytest with the following cmd args
    result = testdir.runpytest(
        '--splunk_type=docker',
        '--splunk_app=tests/package',
        '--splunk_password=Changed@11',
        '-v'
    )

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        '*::test_connection_splunk PASSED*',
    ])

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


@flaky(max_runs=5, min_passes=1)
def test_splunk_app_fiction(testdir):
    """Make sure that pytest accepts our fixture."""

    testdir.makepyfile("""
        from pytest_splunk_addon.standard_lib.addon_basic import Basic
        class Test_App(Basic):
            def empty_method():
                pass

    """)

    destination = shutil.copytree(
        os.path.join(testdir.request.fspath.dirname, 'addons/TA_fiction'),
        os.path.join(testdir.tmpdir, 'tests/package')
    )

    destination = shutil.copy(
        os.path.join(testdir.request.fspath.dirname, 'Dockerfile'),
        os.path.join(testdir.tmpdir, 'tests/')
    )
    destination = shutil.copy(
        os.path.join(testdir.request.fspath.dirname, 'docker-compose.yml'),
        os.path.join(testdir.tmpdir, 'tests/')
    )
    # run pytest with the following cmd args
    result = testdir.runpytest(
        '--splunk_type=docker',
        '--splunk_app=tests/package',
        '--splunk_password=Changed@11',
        '-v'
    )

    # '*test_fields*splunkd*EXTRACT-two*PASSED*',
    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        '*test_basic_props*splunkd*PASSED*',
    ])

    # '*test_basic_eventtype*splunkd*PASSED*',
    # '*test_fields*splunkd*EXTRACT-one*PASSED*',
    #
    # '*test_fields*splunkd*FIELDALIAS-one*PASSED*'

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


# def test_splunk_app_broken_sourcetype(testdir,splunk_server):
#     """Make sure that pytest accepts our fixture."""
#
#     testdir.makepyfile("""
#         from pytest_splunk_addon.standard_lib.addon_basic import Basic
#         class Test_App(Basic):
#             def empty_method():
#                 pass
#
#     """)
#
#     # run pytest with the following cmd args
#     result = testdir.runpytest(
#         '--splunk_app=/Users/rfaircloth/PycharmProjects/pytest-splunk-addon/tests/addons/TA_broken_sourcetype',
#         f'--splunk_host={splunk_server[0]}',
#         f'--splunk_port={splunk_server[1]}',
#         '--splunk_password=Changed@11',
#         '-v'
#     )
#
#     # fnmatch_lines does an assertion internally
#     result.stdout.fnmatch_lines([
#         '*test_basic_sourcetypes*notvalid*FAILED*',
#         '*test_fields*notvalid::EXTRACT-one* SKIPPED*',
#     ])
#
#     # The test suite should fail as this is a negative test
#     assert result.ret != 0


def test_help_message(testdir):
    result = testdir.runpytest(
        '--help',
    )
    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        'splunk-addon:',
        '*--splunk_app=*',
        '*--splunk_host=*',
        '*--splunk_port=*',
        '*--splunk_user=*',
        '*--splunk_password=*',
    ])
