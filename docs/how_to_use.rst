
How To Use
----------

Create a test file in the tests folder

.. code:: python3

    from pytest_splunk_addon.standard_lib.addon_basic import Basic
        class Test_App(Basic):
            def empty_method():
                pass

There are two ways one can execute the tests

**1. Running tests with external splunk**

    .. code:: python3

        pip install pytest-splunk-addon

    Run pytest with the add-on and SA-eventgen installed and enabled in an external Splunk deployment

    .. code:: bash

        pytest -v --splunk-type=external --splunk-app=<path-to-addon-package> --splunk-host=<hostname> --splunk-port=<splunk-management-port> --splunk-user=<username> --splunk-password=<password>

The tool assumes the Splunk Add-on is located in a folder "package" in the project root.

**2. Running tests with docker splunk**

    .. code:: bash

        pip install pytest-splunk-addon[docker]

    Create a Dockerfile-splunk file 

    .. literalinclude:: ../Dockerfile.splunk

    Create a docker-compose.yml

    .. literalinclude:: ../docker-compose.yml

    Run pytest with the add-on and SA-eventgen installed and enabled in docker

    .. code:: bash

        pytest --splunk-password=Changed@11 -v

Extending pytest-splunk-addon
-----------------------------

**1. Test cases taking too long to execute**

    Use pytest-xdist to have test cases executed across multiple processes.

    How to use pytest-xdist :

        - pip install pytest-xdist
        - add `-n {number-of-processes}` to the pytest command

    This will create mentioned amount of processes and divide the test cases amongst them.

    .. Note ::
        Make sure there is enough data on splunk before running tests with pytest-xdist as faster the execution lesser the time to generate more data.

**2. Want flaky/known failures to not fail the execution**

    use pytest-expect to mark a list of test cases as flaky/known failures which will not affect the final result of testing.

    How to use pytest-expect:

        - pip install pytest-expect
        - adding `--update-xfail` to the pytest command will make you a `.pytest.expect`, which is a list of failures while execution.
        - now on second run just have the `.pytest.expect` in the folder where tests are executed, and all the tests in the file will be marked `xfail` [#]_
        - if there is a custom file with failing test case list, that can be used by adding `--xfail-file custom_file` to the pytest command.
        
        .. Note ::
            Test cases should me added to .pytest.expect only after proper validation.

**3. Check mapping of an addon with custom data models**

    pytest-splunk-addon is capable of testing mapping of an addon with custom data models.

    How this can be achieved :
        - Make json representation of the data models, which satisfies the schema located at ``pytest-splunk-addon/pytest_splunk_addon/standard_lib/cim_tests/DatamodelSchema.json``
        - provide the path to directory having all the data models by adding `--splunk_dm_path path_to_dir` to the pytest command
        - Now the test cases will be generated for the data models provided to teh plugin and not for the default data models.

.. raw:: html

   <hr width=100%>
   
.. [#] A xfail means that you expect a test to fail for some reason. A common example is a test for a feature not yet implemented, or a bug not yet fixed. When a test passes despite being expected to fail, it's an xpass and will be reported in the test summary.