# -*- coding: utf-8 -*-
import os
import shutil
import logging
import pytest
from tests.e2e import constants
from pytest_splunk_addon.sample_generation import SampleGenerator, Rule

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

    # make sure that we get a '0' exit code for the testsuite
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

    # make sure that we get a '0' exit code for the testsuite
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

    # make sure that we get a '0' exit code for the testsuite
    assert result.ret == 0


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
        "--splunk-type=external",
        "-v",
        "--search-interval=0",
        "--search-retry=0",
        "--splunk-data-generator=tests/addons/TA_fiction_indextime/default",
        "--search-index=*,_internal",
    )

    result.stdout.fnmatch_lines("*Exiting pytest due to invalid HEC token value.")

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

    # make sure that we get a '0' exit code for the testsuite
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

    # make sure that we get a '0' exit code for the testsuite
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

    # make sure that we get a non '0' exit code for the testsuite as it contains failure
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

    # make sure that we get a non '0' exit code for the testsuite as it contains failure
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

    # make sure that we get a non '0' exit code for the testsuite as it contains failure
    assert result.ret == 0, "result not equal to 0"


@pytest.mark.docker
@pytest.mark.splunk_cim_model_ipv6_regex
def test_splunk_cim_model_ipv6_regex(testdir, request):
    """
    In this test we are only checking if src_ip and dest_ip are extracted and are valid and tests are passing
    scr_ip contains ~35 diff advanced form of ipv6 combinations that are tested in this case.
    """
    testdir.makepyfile(
        """
        from pytest_splunk_addon.standard_lib.addon_basic import Basic
        class Test_App(Basic):
            def empty_method():
                pass
    """
    )

    shutil.copytree(
        os.path.join(testdir.request.fspath.dirname, "addons/TA_cim_addon"),
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
        "--splunk-data-generator=tests/addons/TA_cim_addon/default",
        "-k test_cim_required_fields",
    )
    logger.info(result.outlines)

    result.stdout.fnmatch_lines_random(constants.TA_CIM_MODEL_RESULT)

    # make sure that we get a non '0' exit code for the testsuite as it contains failure
    assert result.ret != 0, "result not equal to 0"


@pytest.mark.test_infinite_loop_fixture
@pytest.mark.external
def test_infinite_loop_in_ingest_data_fixture(testdir, request):
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
    # we are providing wrong sc4s service details here so that we can recreate scenario where first worked raises exception and other workers get stuck
    result = testdir.runpytest(
        "--splunk-app=addons/TA_fiction_indextime",
        "--splunk-type=external",
        "--splunk-host=splunk",
        "--splunk-data-generator=tests/addons/TA_fiction_indextime/default",
        "--sc4s-host=splunk",
        "--sc4s-port=100",
        "-n 2",
    )

    # Here we are not interested in the failures or errors,
    # we are basically checking that we get results and test execution does not get stuck
    assert result.parseoutcomes().get("passed") > 0
