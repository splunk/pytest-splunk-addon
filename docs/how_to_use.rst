
How To Use
----------

.. _test_file:

Create a test file in the tests folder

.. code:: python3

    from pytest_splunk_addon.standard_lib.addon_basic import Basic
        class Test_App(Basic):
            def empty_method():
                pass


.. _test_execution:

There are two ways to execute the tests:

**1. Running tests with an external Splunk instance**

    .. code:: python3

        pip3 install pytest-splunk-addon

    Run pytest with the add-on, in an external Splunk deployment

    .. code:: bash

        pytest --splunk-type=external --splunk-app=<path-to-addon-package> --splunk-host=<hostname> --splunk-port=<splunk-management-port> --splunk-user=<username> --splunk-password=<password> --splunk-hec-token=<splunk_hec_token>


**2. Running tests with docker splunk**

    .. code:: bash

        pip install pytest-splunk-addon[docker]

    Create a Dockerfile-splunk file 

    .. literalinclude:: ../Dockerfile.splunk
       :language: Dockerfile

    Create docker-compose.yml

    .. literalinclude:: ../docker-compose.yml
       :language: YAML
       :lines: 9-

.. _conftest_file:

    Create conftest.py in the test folder along with :ref:`the test file <test_file>`

    .. literalinclude:: ../tests/conftest.py
       :language: python
       :lines: 2,12-

    Run pytest with the add-on, SA-Eventgen and Splunk Common Information Model installed and enabled in docker

    .. code:: bash

        pytest --splunk-type=docker --splunk-password=Changed@11

The tool assumes the Splunk Add-on is located in a folder "package" in the project root.

.. note::
   If live events are available in external Splunk instance or docker splunk, then SA-Eventgen is not required.

----------------------

There are 3 types of tests included in pytest-splunk-addon.

    1. To generate test cases only for knowledge objects, append the following marker to pytest command:

        .. code-block:: console

            -m  splunk_searchtime_fields

    2. To generate test cases only for CIM compatibility, append the following marker to pytest command:

        .. code-block:: console

            -m  splunk_searchtime_cim

    3. To generate test cases only for index time properties, append the following marker to pytest command:

        .. code-block:: console

            -m  splunk_indextime --splunk-data-generator=<Path to the conf file>

        For detailed information on index time test execution, please refer :ref:`here <index_time_tests>`.

----------------------

The following optional arguments are available to modify the default settings in the test cases.

    1. To search for events in a specific index, user can provide following additional arguments:

        .. code-block:: console

            --search-index=<index>

                Splunk index of which the events will be searched while testing. Default value: "*, _internal".


    2. To increase/decrease time interval and retries for flaky tests, user can provide following additional arguments:

        .. code-block:: console

            --search-retry=<retry>

                Number of retries to make if there are no events found while searching in the Splunk instance. Default value: 3.

            --search-interval=<interval>

                Time interval to wait before retrying the search query.Default value: 3.


Extending pytest-splunk-addon
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**1. Test cases taking too long to execute**

    Use `pytest-xdist <https://pypi.org/project/pytest-xdist/>`_ to execute test cases across multiple processes.

    How to use pytest-xdist :

        - pip install pytest-xdist
        - add ``-n {number-of-processes}`` to the pytest command

    This will create the mentioned amount of processes and divide the test cases amongst them.

    .. Note ::
        Make sure there is enough data on the Splunk instance before running tests with pytest-xdist because faster the execution, lesser the time to generate enough data.

**2. Want flaky/known failures to not fail the execution**

    Use `pytest-expect <https://pypi.org/project/pytest-expect/>`_ to mark a list of test cases as flaky/known failures which will not affect the final result of testing.

    How to use pytest-expect:

        - pip install pytest-expect
        - Add ``--update-xfail`` to the pytest command to generate a `.pytest.expect` file, which is a list of failures while execution.
        - Make sure that the `.pytest.expect` file is in the root directory from where the test cases are executed.
        - When the test cases are executed the next time, all the tests in the `.pytest.expect` file will be marked as `xfail` [#]_
        - If there is a custom file containing the list of failed test cases, it can be used by adding ``--xfail-file custom_file`` to the pytest command.
        
        .. Note ::
            Test cases should be added to .pytest.expect only after proper validation.

**3. Setup test environment before executing the test cases**

    If any setup is required in the Splunk/test environment before executing the test cases, implement a fixture in :ref:`conftest.py <conftest_file>`.

    .. code-block:: python

        @pytest.fixture(scope="session")
        def splunk_setup(splunk):
            # Will be executed before test execution starts
            . . .

    The setup fixture opens many possibilities to setup the testing environment / to configure Splunk. For example,

        - Enable Saved-searches
        - Configure the inputs of an Add-on.
        - Wait for an lookup to be populated.
        - Restart Splunk.

    The following snippet shows an example in which the setup fixture is used to enable a saved search.

    .. literalinclude:: ../tests/enable_saved_search_conftest.py
       :language: python
       :lines: 2,31-


**4. Check mapping of an add-on with custom data models**

    pytest-splunk-addon is capable of testing mapping of an add-on with custom data models.

    How can this be achieved :

        - Make json representation of the data models, which satisfies this `DataModelSchema <https://github.com/splunk/pytest-splunk-addon/blob/master/pytest_splunk_addon/standard_lib/cim_tests/DatamodelSchema.json>`_.
        - Provide the path to the directory having all the data models by adding ``--splunk_dm_path path_to_dir`` to the pytest command
        - The test cases will now be generated for the data models provided to the plugin and not for the `default data models <https://github.com/splunk/pytest-splunk-addon/tree/master/pytest_splunk_addon/standard_lib/data_models>`_.

.. raw:: html

   <hr width=100%>
   
.. [#] xfail indicates that you expect a test to fail for some reason. A common example is a test for a feature not yet implemented, or a bug not yet fixed. When a test passes despite being expected to fail, it's an xpass and will be reported in the test summary.
