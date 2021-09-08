import logging
import os
import shutil

import pytest

from pytest_splunk_addon.standard_lib.sample_generation.rule import Rule
from pytest_splunk_addon.standard_lib.sample_generation.sample_generator import (
    SampleGenerator,
)
from tests import constants

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
        os.path.join(testdir.request.config.invocation_dir, "tests/addons"),
        os.path.join(testdir.tmpdir, "tests/addons"),
    )

    shutil.copy(
        os.path.join(testdir.request.config.invocation_dir, "tests/conftest.py"),
        os.path.join(testdir.tmpdir, ""),
    )

    shutil.copytree(
        os.path.join(testdir.request.config.invocation_dir, "tests/requirement_test"),
        os.path.join(testdir.tmpdir, "tests/requirement_test"),
    )

    shutil.copytree(
        os.path.join(
            testdir.request.config.invocation_dir, "tests/requirement_test_modinput"
        ),
        os.path.join(testdir.tmpdir, "tests/requirement_test_modinput"),
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
def test_splunk_connection_external(testdir):
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
def test_splunk_connection_docker(testdir):
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
        "--splunk-type=docker",
        "-v",
    )

    # fnmatch_lines does an assertion internally
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
        os.path.join(testdir.tmpdir, "package"),
    )

    setup_test_dir(testdir)
    SampleGenerator.clean_samples()
    Rule.clean_rules()

    # run pytest with the following cmd args
    result = testdir.runpytest(
        "--splunk-type=docker",
        "-v",
        "-m splunk_searchtime_fields",
        "--search-interval=4",
        "--search-retry=4",
        "--search-index=*,_internal",
    )

    result.stdout.fnmatch_lines_random(constants.TA_FICTION_PASSED)
    result.assert_outcomes(passed=len(constants.TA_FICTION_PASSED), failed=0)

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


@pytest.mark.docker
def test_splunk_app_broken(testdir):
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
        constants.TA_BROKEN_PASSED + constants.TA_BROKEN_FAILED
    )
    result.assert_outcomes(
        passed=len(constants.TA_BROKEN_PASSED),
        failed=len(constants.TA_BROKEN_FAILED),
    )

    # The test suite should fail as this is a negative test
    assert result.ret != 0


@pytest.mark.docker
def test_splunk_app_cim_fiction(testdir):
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
        "--splunk-type=docker",
        "--splunk-dm-path=tests/data_models",
        "-v",
        "-m splunk_searchtime_cim",
        "--search-interval=4",
        "--search-retry=4",
        "--search-index=*,_internal",
    )

    result.stdout.fnmatch_lines_random(constants.TA_CIM_FICTION_PASSED)
    result.assert_outcomes(passed=len(constants.TA_CIM_FICTION_PASSED), failed=0)

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


@pytest.mark.docker
def test_splunk_app_cim_broken(testdir):
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
        constants.TA_CIM_BROKEN_PASSED + constants.TA_CIM_BROKEN_FAILED
    )
    result.assert_outcomes(
        passed=len(constants.TA_CIM_BROKEN_PASSED),
        failed=len(constants.TA_CIM_BROKEN_FAILED),
    )

    # The test suite should fail as this is a negative test
    assert result.ret != 0


@pytest.mark.docker
def test_splunk_fiction_indextime(testdir):
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
def test_splunk_fiction_indextime_broken(testdir):
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
def test_splunk_setup_fixture(testdir):
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
def test_splunk_app_requirements(testdir):
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
        os.path.join(testdir.request.fspath.dirname, "addons/TA_requirement_test"),
        os.path.join(testdir.tmpdir, "package"),
    )

    setup_test_dir(testdir)
    SampleGenerator.clean_samples()
    Rule.clean_rules()

    # run pytest with the following cmd args
    result = testdir.runpytest(
        "--splunk-type=docker",
        "-v",
        "-m splunk_searchtime_requirements",
        "--search-interval=4",
        "--search-retry=4",
        "--search-index=*,_internal",
        "--requirement-test=tests/requirement_test",
    )
    logger.info(result.outlines)
    logger.info(len(constants.TA_REQUIREMENTS_PASSED))
    result.stdout.fnmatch_lines_random(
        constants.TA_REQUIREMENTS_PASSED + constants.TA_REQUIREMENTS_FAILED
    )
    result.assert_outcomes(passed=len(constants.TA_REQUIREMENTS_PASSED), failed=1)

    # make sure that that we get a non '0' exit code for the testsuite as it contains failure
    assert result.ret != 0


@pytest.mark.docker
def test_splunk_app_requirements_modinput(testdir):
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
            testdir.request.fspath.dirname, "addons/TA_requirement_test_modinput"
        ),
        os.path.join(testdir.tmpdir, "package"),
    )

    setup_test_dir(testdir)
    SampleGenerator.clean_samples()
    Rule.clean_rules()

    # run pytest with the following cmd args
    result = testdir.runpytest(
        "--splunk-type=docker",
        "-v",
        "-m splunk_searchtime_requirements",
        "--search-interval=4",
        "--search-retry=4",
        "--search-index=*,_internal",
        "--requirement-test=tests/requirement_test_modinput",
    )
    logger.info(result.outlines)
    logger.info(len(constants.TA_REQUIREMENTS_MODINPUT_PASSED))
    result.stdout.fnmatch_lines_random(
        constants.TA_REQUIREMENTS_MODINPUT_PASSED
        + constants.TA_REQUIREMENTS_MODINPUT_FAILED
    )
    result.assert_outcomes(
        passed=len(constants.TA_REQUIREMENTS_MODINPUT_PASSED), failed=1
    )

    # make sure that that we get a non '0' exit code for the testsuite as it contains failure
    assert result.ret != 0
