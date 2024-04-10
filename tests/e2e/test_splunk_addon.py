# -*- coding: utf-8 -*-
import os
import shutil
import logging
import pytest
from tests.e2e import constants
from pytest_splunk_addon.standard_lib.sample_generation import SampleGenerator, Rule

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


def setup_test_dir(testdir):
    shutil.copytree(
        os.path.join(testdir.request.config.invocation_dir, "deps"),
        os.path.join(testdir.tmpdir, "deps"),
    )

    shutil.copytree(
        os.path.join(testdir.request.config.invocation_dir, "tests/e2e/addons"),
        os.path.join(testdir.tmpdir, "tests/addons"),
    )

    shutil.copy(
        os.path.join(testdir.request.config.invocation_dir, "tests/e2e/conftest.py"),
        os.path.join(testdir.tmpdir, ""),
    )

    shutil.copy(
        os.path.join(testdir.request.config.invocation_dir, "Dockerfile.splunk"),
        testdir.tmpdir,
    )
    shutil.copy(
        os.path.join(testdir.request.config.invocation_dir, "Dockerfile.uf"),
        testdir.tmpdir,
    )
    shutil.copy(
        os.path.join(testdir.request.config.invocation_dir, "Dockerfile.tests"),
        testdir.tmpdir,
    )

    shutil.copy(
        os.path.join(testdir.request.config.invocation_dir, "docker-compose.yml"),
        testdir.tmpdir,
    )


@pytest.mark.external
def test_splunk_connection_external(testdir, request):
    """Make sure that pytest accepts our fixture."""

    # create a temporary pytest test module
    testdir.makepyfile(test_connection_only)

    # Copy the content of source to destination
    shutil.copytree(
        os.path.join(testdir.request.fspath.dirname, "addons/TA_fiction"),
        os.path.join(testdir.tmpdir, "package"),
    )
    SampleGenerator.clean_samples()
    Rule.clean_rules()

    # run pytest with the following cmd args
    result = testdir.runpytest(
        f"--splunk-version={request.config.getoption('splunk_version')}",
        "--splunk-app=addons/TA_fiction",
        "--splunk-type=external",
        "--splunk-host=splunk",
        "--splunk-port=8089",
        "--splunk-forwarder-host=splunk",
        "-v",
    )

    # fnmatch_lines does an assertion internally
    result.assert_outcomes(passed=1, failed=0)

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


@pytest.mark.docker
@pytest.mark.splunk_connection_docker
def test_splunk_connection_docker(testdir, request):
    """Make sure that pytest accepts our fixture."""

    # create a temporary pytest test module
    testdir.makepyfile(test_connection_only)

    # Copy the content of source to destination

    shutil.copytree(
        os.path.join(testdir.request.fspath.dirname, "addons/TA_fiction"),
        os.path.join(testdir.tmpdir, "package"),
    )

    setup_test_dir(testdir)
    SampleGenerator.clean_samples()
    Rule.clean_rules()

    # run pytest with the following cmd args
    result = testdir.runpytest(
        f"--splunk-version={request.config.getoption('splunk_version')}",
        "--splunk-type=docker",
        "-v",
    )

    # fnmatch_lines does an assertion internally
    result.assert_outcomes(passed=1, failed=0)

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


@pytest.mark.docker
@pytest.mark.splunk_app_fiction
def test_splunk_app_fiction(testdir, request):
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
        os.path.join(testdir.tmpdir, "package"),
    )

    setup_test_dir(testdir)
    SampleGenerator.clean_samples()
    Rule.clean_rules()

    # run pytest with the following cmd args
    result = testdir.runpytest(
        f"--splunk-version={request.config.getoption('splunk_version')}",
        "--splunk-type=docker",
        "-v",
        "-m splunk_searchtime_fields",
        "--search-interval=4",
        "--search-retry=4",
        "--search-index=*,_internal",
    )

    result.stdout.fnmatch_lines_random(
        constants.TA_FICTION_PASSED + constants.TA_FICTION_SKIPPED
    )
    result.assert_outcomes(
        passed=len(constants.TA_FICTION_PASSED),
        failed=0,
        skipped=len(constants.TA_FICTION_SKIPPED),
    )

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


@pytest.mark.docker
@pytest.mark.splunk_fiction_indextime_wrong_hec_token
def test_splunk_fiction_indextime_wrong_hec_token(testdir, request):
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
        os.path.join(testdir.request.fspath.dirname, "addons/TA_fiction_indextime"),
        os.path.join(testdir.tmpdir, "package"),
    )

    shutil.copytree(
        os.path.join(testdir.request.fspath.dirname, "test_data_models"),
        os.path.join(testdir.tmpdir, "tests/data_models"),
    )

    setup_test_dir(testdir)
    SampleGenerator.clean_samples()
    Rule.clean_rules()
    with open(
        os.path.join(testdir.request.fspath.dirname, "incorrect_hec_token_conftest.py")
    ) as conf_test_file:
        testdir.makeconftest(conf_test_file.read())

    # run pytest with the following cmd args
    result = testdir.runpytest(
        f"--splunk-version={request.config.getoption('splunk_version')}",
        "--splunk-type=docker",
        "-v",
        "--search-interval=0",
        "--search-retry=0",
        "--splunk-data-generator=tests/addons/TA_fiction_indextime/default",
        "--search-index=*,_internal",
    )

    result.assert_outcomes(errors=1, passed=0, failed=0, xfailed=0)
    result.stdout.fnmatch_lines(
        "!!!!!! _pytest.outcomes.Exit: Exiting pytest due to: <class 'Exception'> !!!!!!!"
    )

    assert result.ret != 0


@pytest.mark.docker
@pytest.mark.splunk_app_broken
def test_splunk_app_broken(testdir, request):
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
        os.path.join(testdir.request.fspath.dirname, "addons/TA_broken"),
        os.path.join(testdir.tmpdir, "package"),
    )
    shutil.copy(
        os.path.join(
            testdir.request.config.invocation_dir, ".ignore_splunk_internal_errors"
        ),
        testdir.tmpdir,
    )
    setup_test_dir(testdir)
    SampleGenerator.clean_samples()
    Rule.clean_rules()

    # run pytest with the following cmd args
    result = testdir.runpytest(
        f"--splunk-version={request.config.getoption('splunk_version')}",
        "--splunk-type=docker",
        "-v",
        "-m splunk_searchtime_fields",
        "--search-interval=4",
        "--search-retry=4",
        "--search-index=*,_internal",
        "--ignore-addon-errors=.ignore_splunk_internal_errors",
    )

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines_random(
        constants.TA_BROKEN_PASSED
        + constants.TA_BROKEN_FAILED
        + constants.TA_BROKEN_SKIPPED
    )
    result.assert_outcomes(
        passed=len(constants.TA_BROKEN_PASSED),
        failed=len(constants.TA_BROKEN_FAILED),
        skipped=len(constants.TA_BROKEN_SKIPPED),
    )

    # The test suite should fail as this is a negative test
    assert result.ret != 0


@pytest.mark.docker
@pytest.mark.splunk_app_cim_fiction
def test_splunk_app_cim_fiction(testdir, request):
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
        os.path.join(testdir.request.fspath.dirname, "addons/TA_CIM_Fiction"),
        os.path.join(testdir.tmpdir, "package"),
    )

    shutil.copytree(
        os.path.join(testdir.request.fspath.dirname, "test_data_models"),
        os.path.join(testdir.tmpdir, "tests/data_models"),
    )

    setup_test_dir(testdir)
    SampleGenerator.clean_samples()
    Rule.clean_rules()

    # run pytest with the following cmd args
    result = testdir.runpytest(
        f"--splunk-version={request.config.getoption('splunk_version')}",
        "--splunk-type=docker",
        "--splunk-dm-path=tests/data_models",
        "-v",
        "-m splunk_searchtime_cim",
        "--search-interval=4",
        "--search-retry=4",
        "--search-index=*,_internal",
    )

    result.stdout.fnmatch_lines_random(
        constants.TA_CIM_FICTION_PASSED + constants.TA_CIM_FICTION_SKIPPED
    )
    result.assert_outcomes(
        passed=len(constants.TA_CIM_FICTION_PASSED),
        failed=0,
        skipped=len(constants.TA_CIM_FICTION_SKIPPED),
    )

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


@pytest.mark.docker
@pytest.mark.splunk_app_cim_broken
def test_splunk_app_cim_broken(testdir, request):
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
        os.path.join(testdir.request.fspath.dirname, "addons/TA_CIM_Broken"),
        os.path.join(testdir.tmpdir, "package"),
    )

    shutil.copytree(
        os.path.join(testdir.request.fspath.dirname, "test_data_models"),
        os.path.join(testdir.tmpdir, "tests/data_models"),
    )

    setup_test_dir(testdir)
    SampleGenerator.clean_samples()
    Rule.clean_rules()

    # run pytest with the following cmd args
    result = testdir.runpytest(
        f"--splunk-version={request.config.getoption('splunk_version')}",
        "--splunk-type=docker",
        "--splunk-dm-path=tests/data_models",
        "-v",
        "-m splunk_searchtime_cim",
        "--search-interval=4",
        "--search-retry=4",
        "--search-index=*,_internal",
    )

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines_random(
        constants.TA_CIM_BROKEN_PASSED
        + constants.TA_CIM_BROKEN_FAILED
        + constants.TA_CIM_BROKEN_SKIPPED
    )
    result.assert_outcomes(
        passed=len(constants.TA_CIM_BROKEN_PASSED),
        failed=len(constants.TA_CIM_BROKEN_FAILED),
        skipped=len(constants.TA_CIM_BROKEN_SKIPPED),
    )

    # The test suite should fail as this is a negative test
    assert result.ret != 0


@pytest.mark.docker
@pytest.mark.splunk_fiction_indextime
def test_splunk_fiction_indextime(testdir, request):
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
        os.path.join(testdir.request.fspath.dirname, "addons/TA_fiction_indextime"),
        os.path.join(testdir.tmpdir, "package"),
    )

    shutil.copytree(
        os.path.join(testdir.request.fspath.dirname, "test_data_models"),
        os.path.join(testdir.tmpdir, "tests/data_models"),
    )

    setup_test_dir(testdir)
    SampleGenerator.clean_samples()
    Rule.clean_rules()

    # run pytest with the following cmd args
    result = testdir.runpytest(
        f"--splunk-version={request.config.getoption('splunk_version')}",
        "--splunk-type=docker",
        "-v",
        "--search-interval=0",
        "--search-retry=0",
        "--splunk-data-generator=tests/addons/TA_fiction_indextime/default",
        "--search-index=*,_internal",
    )

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines_random(
        constants.TA_FICTION_INDEXTIME_PASSED + constants.TA_FICTION_INDEXTIME_SKIPPED
    )
    result.assert_outcomes(
        passed=len(constants.TA_FICTION_INDEXTIME_PASSED),
        skipped=len(constants.TA_FICTION_INDEXTIME_SKIPPED),
        failed=0,
    )

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


@pytest.mark.docker
@pytest.mark.splunk_fiction_indextime_broken
def test_splunk_fiction_indextime_broken(testdir, request):
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
        os.path.join(
            testdir.request.fspath.dirname, "addons/TA_fiction_indextime_broken"
        ),
        os.path.join(testdir.tmpdir, "package"),
    )

    shutil.copytree(
        os.path.join(testdir.request.fspath.dirname, "test_data_models"),
        os.path.join(testdir.tmpdir, "tests/data_models"),
    )

    setup_test_dir(testdir)
    SampleGenerator.clean_samples()
    Rule.clean_rules()

    # run pytest with the following cmd args
    result = testdir.runpytest(
        f"--splunk-version={request.config.getoption('splunk_version')}",
        "--splunk-type=docker",
        "-v",
        "--search-interval=0",
        "--search-retry=0",
        "--splunk-data-generator=tests/addons/TA_fiction_indextime_broken/default",
        "--search-index=*,_internal",
    )

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines_random(
        constants.TA_FICTION_INDEXTIME_BROKEN_PASSED
        + constants.TA_FICTION_INDEXTIME_BROKEN_FAILED
        + constants.TA_FICTION_INDEXTIME_BROKEN_SKIPPED
    )
    result.assert_outcomes(
        passed=len(constants.TA_FICTION_INDEXTIME_BROKEN_PASSED),
        skipped=len(constants.TA_FICTION_INDEXTIME_BROKEN_SKIPPED),
        failed=len(constants.TA_FICTION_INDEXTIME_BROKEN_FAILED),
    )

    # The test suite should fail as this is a negative test
    assert result.ret != 0


@pytest.mark.docker
@pytest.mark.splunk_setup_fixture
def test_splunk_setup_fixture(testdir, request):
    testdir.makepyfile(
        """
        from pytest_splunk_addon.standard_lib.addon_basic import Basic
        class Test_App(Basic):
            def empty_method():
                pass

        """
    )
    setup_test_dir(testdir)
    SampleGenerator.clean_samples()
    Rule.clean_rules()
    with open(
        os.path.join(testdir.request.fspath.dirname, "enable_saved_search_conftest.py")
    ) as conf_test_file:
        testdir.makeconftest(conf_test_file.read())

    shutil.copytree(
        os.path.join(testdir.request.fspath.dirname, "addons/TA_SavedSearch"),
        os.path.join(testdir.tmpdir, "package"),
    )

    result = testdir.runpytest(
        f"--splunk-version={request.config.getoption('splunk_version')}",
        "--splunk-type=docker",
        "-v",
        "-k saved_search_lookup",
        "--search-interval=4",
        "--search-retry=4",
        "--search-index=*,_internal",
    )

    result.assert_outcomes(passed=2)


@pytest.mark.doc
def test_help_message(testdir):
    result = testdir.runpytest(
        "--help",
    )
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


@pytest.mark.doc
def test_docstrings(testdir):
    from sphinx.application import Sphinx

    docs_dir = os.path.join(testdir.request.config.invocation_dir, "docs")
    output_dir = os.path.join(docs_dir, "_build", "html")
    doctree_dir = os.path.join(docs_dir, "_build", "doctrees")
    all_files = 1
    app = Sphinx(
        docs_dir,
        docs_dir,
        output_dir,
        doctree_dir,
        buildername="html",
        warningiserror=True,
    )
    app.build(force_all=all_files)


@pytest.mark.docker
@pytest.mark.splunk_app_req
def test_splunk_app_req(testdir, request):
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
        os.path.join(testdir.request.fspath.dirname, "addons/TA_transition_from_req"),
        os.path.join(testdir.tmpdir, "package"),
    )

    shutil.copytree(
        os.path.join(testdir.request.fspath.dirname, "test_data_models"),
        os.path.join(testdir.tmpdir, "tests/data_models"),
    )

    setup_test_dir(testdir)
    SampleGenerator.clean_samples()
    Rule.clean_rules()

    # run pytest with the following cmd args
    result = testdir.runpytest(
        f"--splunk-version={request.config.getoption('splunk_version')}",
        "--splunk-type=docker",
        "-v",
        "--search-interval=4",
        "--search-retry=4",
        "--search-index=*",
        "--splunk-data-generator=tests/addons/TA_transition_from_req/default",
    )
    logger.info(result.outlines)

    result.stdout.fnmatch_lines_random(
        constants.TA_REQ_TRANSITION_PASSED
        + constants.TA_REQ_TRANSITION_FAILED
        + constants.TA_REQ_TRANSITION_SKIPPED
    )
    result.assert_outcomes(
        passed=len(constants.TA_REQ_TRANSITION_PASSED),
        failed=len(constants.TA_REQ_TRANSITION_FAILED),
        skipped=len(constants.TA_REQ_TRANSITION_SKIPPED),
    )

    # make sure that that we get a non '0' exit code for the testsuite as it contains failure
    assert result.ret == 0, "result not equal to 0"


@pytest.mark.docker
@pytest.mark.splunk_app_req_broken
def test_splunk_app_req_broken(testdir, request):
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
        os.path.join(testdir.request.fspath.dirname, "addons/TA_req_broken"),
        os.path.join(testdir.tmpdir, "package"),
    )

    shutil.copytree(
        os.path.join(testdir.request.fspath.dirname, "test_data_models"),
        os.path.join(testdir.tmpdir, "tests/data_models"),
    )

    setup_test_dir(testdir)
    SampleGenerator.clean_samples()
    Rule.clean_rules()

    # run pytest with the following cmd args
    result = testdir.runpytest(
        f"--splunk-version={request.config.getoption('splunk_version')}",
        "--splunk-type=docker",
        "-v",
        "--search-interval=4",
        "--search-retry=4",
        "--search-index=*",
        "--splunk-data-generator=tests/addons/TA_req_broken/default",
    )
    logger.info(result.outlines)

    result.stdout.fnmatch_lines_random(
        constants.TA_REQ_BROKEN_PASSED
        + constants.TA_REQ_BROKEN_FAILED
        + constants.TA_REQ_BROKEN_SKIPPED
    )
    result.assert_outcomes(
        passed=len(constants.TA_REQ_BROKEN_PASSED),
        failed=len(constants.TA_REQ_BROKEN_FAILED),
        skipped=len(constants.TA_REQ_BROKEN_SKIPPED),
    )

    # make sure that that we get a non '0' exit code for the testsuite as it contains failure
    assert result.ret != 0


@pytest.mark.docker
@pytest.mark.splunk_app_req
def test_splunk_app_req(testdir, request):
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
        os.path.join(testdir.request.fspath.dirname, "addons/TA_transition_from_req"),
        os.path.join(testdir.tmpdir, "package"),
    )

    shutil.copytree(
        os.path.join(testdir.request.fspath.dirname, "test_data_models"),
        os.path.join(testdir.tmpdir, "tests/data_models"),
    )

    setup_test_dir(testdir)
    SampleGenerator.clean_samples()
    Rule.clean_rules()

    # run pytest with the following cmd args
    result = testdir.runpytest(
        f"--splunk-version={request.config.getoption('splunk_version')}",
        "--splunk-type=docker",
        "-v",
        "--search-interval=2",
        "--search-retry=4",
        "--search-index=*",
        "--splunk-data-generator=tests/addons/TA_transition_from_req/default",
    )
    logger.info(result.outlines)

    result.stdout.fnmatch_lines_random(
        constants.TA_REQ_TRANSITION_PASSED
        + constants.TA_REQ_TRANSITION_FAILED
        + constants.TA_REQ_TRANSITION_SKIPPED
    )
    result.assert_outcomes(
        passed=len(constants.TA_REQ_TRANSITION_PASSED),
        failed=len(constants.TA_REQ_TRANSITION_FAILED),
        skipped=len(constants.TA_REQ_TRANSITION_SKIPPED),
    )

    # make sure that that we get a non '0' exit code for the testsuite as it contains failure
    assert result.ret == 0, "result not equal to 0"
