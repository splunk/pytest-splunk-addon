# -*- coding: utf-8 -*-
import os
import shutil
import logging
import pytest
from tests.psa_tests import constants
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


def pytest_addoption(parser):
    """Add options for interaction with Splunk this allows the tool to work in two modes
    1) kubernetes mode which is typically used by developers on their workstation
        manages a single instance of splunk
    2) external interacts with a single instance of splunk that is lifecycle managed
        by another process such as a ci/cd pipeline
    """
    group = parser.getgroup("splunk-addon")

    group.addoption(
        "--splunk-version",
        action="store",
        dest="splunk_version",
        default="latest",
        help=(
            "Splunk version to spin up with docker while splunk-type "
            " is set to kubernetes. Examples, "
            " 1) latest: latest Splunk Enterprise tagged by the https://github.com/splunk/docker-splunk"
            " 2) 8.0.0: GA release of 8.0.0."
        ),
    )
    group.addoption(
        "--splunk-password",
        action="store",
        dest="splunk_password",
        default="Chang3d!",
        help="Password of the Splunk user",
    )
    group.addoption(
        "--splunk-hec-token",
        action="store",
        dest="splunk_hec_token",
        default="9b741d03-43e9-4164-908b-e09102327d22",
        help='Splunk HTTP event collector token. default is "9b741d03-43e9-4164-908b-e09102327d22" If an external forwarder is used provide HEC token of forwarder.',
    )


def setup_test_dir(testdir):
    shutil.copytree(
        os.path.join(testdir.request.config.invocation_dir, "deps"),
        os.path.join(testdir.tmpdir, "deps"),
    )

    shutil.copytree(
        os.path.join(testdir.request.config.invocation_dir, "tests/psa_tests/addons"),
        os.path.join(testdir.tmpdir, "tests/addons"),
    )

    shutil.copy(
        os.path.join(
            testdir.request.config.invocation_dir, "tests/psa_tests/conftest.py"
        ),
        os.path.join(testdir.tmpdir, ""),
    )

    shutil.copytree(
        os.path.join(
            testdir.request.config.invocation_dir, "tests/psa_tests/requirement_test"
        ),
        os.path.join(testdir.tmpdir, "tests/requirement_test"),
    )

    shutil.copytree(
        os.path.join(
            testdir.request.config.invocation_dir,
            "tests/psa_tests/requirement_test_modinput",
        ),
        os.path.join(testdir.tmpdir, "tests/requirement_test_modinput"),
    )

    shutil.copytree(
        os.path.join(
            testdir.request.config.invocation_dir, "tests/psa_tests/requirement_test_uf"
        ),
        os.path.join(testdir.tmpdir, "tests/requirement_test_uf"),
    )
    shutil.copytree(
        os.path.join(
            testdir.request.config.invocation_dir,
            "tests/psa_tests/requirement_test_scripted",
        ),
        os.path.join(testdir.tmpdir, "tests/requirement_test_scripted"),
    )
    shutil.copytree(
        os.path.join(testdir.request.config.invocation_dir, "tests/src"),
        os.path.join(testdir.tmpdir, "tests/src"),
    )


@pytest.mark.external
def test_splunk_connection_external(request, testdir):
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
        "--splunk-host=localhost",
        "--splunk-port=8089",
        "--splunk-forwarder-host=localhost",
        "--splunk-password={0}".format(request.config.getoption("splunk_password")),
        "--splunk-hec-token={0}".format(request.config.getoption("splunk_hec_token")),
        "-v",
    )

    # fnmatch_lines does an assertion internally
    result.assert_outcomes(passed=1, failed=0)

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


@pytest.mark.kubernetes
@pytest.mark.splunk_connection_kubernetes
def test_splunk_connection_kubernetes(request, testdir):
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
        "--splunk-type=kubernetes",
        "--splunk-web-scheme=http",
        "--splunk-version={0}".format(request.config.getoption("splunk_version")),
        "-v",
    )

    # fnmatch_lines does an assertion internally
    result.assert_outcomes(passed=1, failed=0)

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


@pytest.mark.kubernetes
@pytest.mark.splunk_app_fiction
def test_splunk_app_fiction(request, testdir):
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
        "--splunk-type=kubernetes",
        "--splunk-web-scheme=http",
        "--splunk-version={0}".format(request.config.getoption("splunk_version")),
        "-v",
        "-m splunk_searchtime_fields",
        "--search-interval=4",
        "--search-retry=10",
        "--search-index=*,_internal",
    )

    result.stdout.fnmatch_lines_random(constants.TA_FICTION_PASSED)
    result.assert_outcomes(passed=len(constants.TA_FICTION_PASSED), failed=0)

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


@pytest.mark.kubernetes
@pytest.mark.splunk_app_broken
def test_splunk_app_broken(request, testdir):
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
        "--splunk-type=kubernetes",
        "--splunk-web-scheme=http",
        "--splunk-version={0}".format(request.config.getoption("splunk_version")),
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


@pytest.mark.kubernetes
@pytest.mark.splunk_app_cim_fiction
def test_splunk_app_cim_fiction(request, testdir):
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
        "--splunk-type=kubernetes",
        "--splunk-web-scheme=http",
        "--splunk-dm-path=tests/data_models",
        "--splunk-version={0}".format(request.config.getoption("splunk_version")),
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


@pytest.mark.kubernetes
@pytest.mark.splunk_app_cim_broken
def test_splunk_app_cim_broken(request, testdir):
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
        "--splunk-type=kubernetes",
        "--splunk-web-scheme=http",
        "--splunk-dm-path=tests/data_models",
        "--splunk-version={0}".format(request.config.getoption("splunk_version")),
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


@pytest.mark.kubernetes
@pytest.mark.splunk_fiction_indextime
def test_splunk_fiction_indextime(request, testdir):
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
        "--splunk-type=kubernetes",
        "--splunk-web-scheme=http",
        "--splunk-version={0}".format(request.config.getoption("splunk_version")),
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


@pytest.mark.kubernetes
@pytest.mark.splunk_fiction_indextime_broken
def test_splunk_fiction_indextime_broken(request, testdir):
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
        "--splunk-type=kubernetes",
        "--splunk-web-scheme=http",
        "--splunk-version={0}".format(request.config.getoption("splunk_version")),
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


@pytest.mark.kubernetes
@pytest.mark.splunk_setup_fixture
def test_splunk_setup_fixture(request, testdir):
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
        "--splunk-type=kubernetes",
        "--splunk-web-scheme=http",
        "--splunk-version={0}".format(request.config.getoption("splunk_version")),
        "-v",
        "-k saved_search_lookup",
        "--search-interval=4",
        "--search-retry=10",
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


@pytest.mark.kubernetes
@pytest.mark.splunk_app_requirements
def test_splunk_app_requirements(request, testdir):
    """Make sure that pytest accepts our fixture."""

    testdir.makepyfile(
        """
        from pytest_splunk_addon.standard_lib.addon_requirements_basic import RequirementBasic
        class Test_App(RequirementBasic):
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
        "--splunk-type=kubernetes",
        "--splunk-web-scheme=http",
        "--splunk-version={0}".format(request.config.getoption("splunk_version")),
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
    result.assert_outcomes(passed=2, failed=1)
    #   passed=2 as the successful data comes from 2 sources (log & xml)

    # make sure that that we get a non '0' exit code for the testsuite as it contains failure
    assert result.ret != 0


@pytest.mark.kubernetes
@pytest.mark.splunk_app_requirements_modinput
def test_splunk_app_requirements_modinput(request, testdir):
    """Make sure that pytest accepts our fixture."""

    testdir.makepyfile(
        """
        from pytest_splunk_addon.standard_lib.addon_requirements_basic import RequirementBasic
        class Test_App(RequirementBasic):
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
        "--splunk-type=kubernetes",
        "--splunk-web-scheme=http",
        "--splunk-version={0}".format(request.config.getoption("splunk_version")),
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


@pytest.mark.kubernetes
@pytest.mark.splunk_app_requirements_uf
def test_splunk_app_requirements_uf(request, testdir):
    """Make sure that pytest accepts our fixture."""

    testdir.makepyfile(
        """
        from pytest_splunk_addon.standard_lib.addon_requirements_basic import RequirementBasic
        class Test_App(RequirementBasic):
            def empty_method():
                pass
    """
    )

    shutil.copytree(
        os.path.join(testdir.request.fspath.dirname, "addons/TA_requirement_test_uf"),
        os.path.join(testdir.tmpdir, "package"),
    )

    setup_test_dir(testdir)
    SampleGenerator.clean_samples()
    Rule.clean_rules()

    # run pytest with the following cmd args
    result = testdir.runpytest(
        "--splunk-type=kubernetes",
        "--splunk-web-scheme=http",
        "--splunk-version={0}".format(request.config.getoption("splunk_version")),
        "-v",
        "-m splunk_searchtime_requirements",
        "--search-interval=4",
        "--search-retry=4",
        "--search-index=*,_internal",
        "--requirement-test=tests/requirement_test_uf",
    )
    logger.info(result.outlines)
    logger.info(len(constants.TA_REQUIREMENTS_UF_PASSED))
    result.stdout.fnmatch_lines_random(
        constants.TA_REQUIREMENTS_UF_PASSED + constants.TA_REQUIREMENTS_UF_FAILED
    )
    result.assert_outcomes(passed=len(constants.TA_REQUIREMENTS_UF_PASSED), failed=1)

    # make sure that that we get a non '0' exit code for the testsuite as it contains failure
    assert result.ret != 0


@pytest.mark.kubernetes
@pytest.mark.splunk_app_requirements_scripted
def test_splunk_app_requirements_scripted(request, testdir):
    """Make sure that pytest accepts our fixture."""

    testdir.makepyfile(
        """
        from pytest_splunk_addon.standard_lib.addon_requirements_basic import RequirementBasic
        class Test_App(RequirementBasic):
            def empty_method():
                pass
    """
    )

    shutil.copytree(
        os.path.join(testdir.request.fspath.dirname, "addons/TA_requirement_test_uf"),
        os.path.join(testdir.tmpdir, "package"),
    )

    setup_test_dir(testdir)
    SampleGenerator.clean_samples()
    Rule.clean_rules()

    # run pytest with the following cmd args
    result = testdir.runpytest(
        "--splunk-type=kubernetes",
        "--splunk-web-scheme=http",
        "--splunk-version={0}".format(request.config.getoption("splunk_version")),
        "-v",
        "-m splunk_searchtime_requirements",
        "--search-interval=4",
        "--search-retry=4",
        "--search-index=*,_internal",
        "--requirement-test=tests/requirement_test_scripted",
    )
    logger.info(result.outlines)
    logger.info(len(constants.TA_REQUIREMENTS_SCRIPTED_PASSED))
    logger.info(len(constants.TA_REQUIREMENTS_SCRIPTED_FAILED))
    result.stdout.fnmatch_lines_random(
        constants.TA_REQUIREMENTS_SCRIPTED_PASSED
        + constants.TA_REQUIREMENTS_SCRIPTED_FAILED
    )
    result.assert_outcomes(
        passed=len(constants.TA_REQUIREMENTS_SCRIPTED_PASSED), failed=1
    )

    # make sure that that we get a non '0' exit code for the testsuite as it contains failure
    assert result.ret != 0
