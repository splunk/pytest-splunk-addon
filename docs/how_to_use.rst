
How To Use
----------

.. _test_file:

Create a test file in the tests folder

.. dropdown:: Example Test File

    .. code:: python3

        from pytest_splunk_addon.standard_lib.addon_basic import Basic
        class Test_App(Basic):
            def empty_method():
                pass


.. _test_execution:

There are three ways to execute the tests:

**1. Running tests with an external Splunk instance**

    .. code:: python3

        pip3 install pytest-splunk-addon

    Run pytest with the add-on, in an external Splunk deployment

    .. code:: bash

        pytest --splunk-type=external --splunk-app=<path-to-addon-package> --splunk-data-generator=<path to pytest-splunk-addon-data.conf file> --splunk-host=<hostname> --splunk-port=<splunk-management-port> --splunk-user=<username> --splunk-password=<password> --splunk-hec-token=<splunk_hec_token>


**2. Running tests with docker splunk**

    .. code:: bash

        git clone git@github.com:splunk/pytest-splunk-addon.git
        cd pytest-splunk-addon
        pip install poetry
        poetry install

    Create a Dockerfile.splunk file

    .. dropdown:: Example Dockerfile

        .. code:: Dockerfile

            ARG SPLUNK_VERSION=latest
            FROM splunk/splunk:$SPLUNK_VERSION
            ARG SPLUNK_VERSION=latest
            ARG SPLUNK_APP_ID=TA_UNKNOWN
            ARG SPLUNK_APP_PACKAGE=$SPLUNK_APP_PACKAGE
            RUN echo Splunk VERSION=$SPLUNK_VERSION
            COPY deps/apps /opt/splunk/etc/apps/
            COPY $SPLUNK_APP_PACKAGE /opt/splunk/etc/apps/$SPLUNK_APP_ID

    Create a Dockerfile.uf file

    .. dropdown:: Example Dockerfile

        .. code:: Dockerfile

            ARG SPLUNK_VERSION=latest
            FROM splunk/universalforwarder:$SPLUNK_VERSION
            ARG SPLUNK_VERSION=latest
            ARG SPLUNK_APP_ID=TA_UNKNOWN
            ARG SPLUNK_APP_PACKAGE=$SPLUNK_APP_PACKAGE
            COPY $SPLUNK_APP_PACKAGE /opt/splunkforwarder/etc/apps/$SPLUNK_APP_ID

    Create docker-compose.yml

    .. dropdown:: Example docker-compose file

        .. literalinclude:: ../docker-compose.yml
            :language: YAML
            :lines: 9-

.. _conftest_file:

    Create conftest.py in the test folder along with :ref:`the test file <test_file>`

    .. dropdown:: Example conftest file

        .. literalinclude:: ../tests/conftest.py
            :language: python
            :lines: 1-2,12-

    Run pytest with the add-on, using the following command:

    .. code:: bash

        pytest --splunk-type=docker --splunk-data-generator=<path to pytest-splunk-addon-data.conf file>

The tool assumes the Splunk Add-on is located in a folder "package" in the project root.

.. note::
   * If live events are available in external Splunk instance or docker splunk, then SA-Eventgen is not required. This is applicable only till v1.2.0 of pytest-splunk-addon.
   * From v1.3.0 pytest-splunk-addon ingests data independently which is used for execution of all the test cases.



**3. Running tests with an external forwarder and Splunk instance**

    * Run pytest with the add-on, using an external forwarder sending events to another Splunk deployment where a user can search for received events.
    * Forwarding & receiving configuration in --splunk-forwarder-host and --splunk-host must be done before executing the tests.
    * User can validate the forwarding using makeresults command.

    .. code:: bash

        | makeresults | eval _raw="sample event" | collect index=main, source=test_source, sourcetype=test_src_type

    * Sample pytest command with the required params
    
    .. code:: bash

        pytest --splunk-type=external                                   # Whether you want to run the addon with docker or an external Splunk instance
            --splunk-app=<path-to-addon-package>                        # Path to Splunk app package. The package should have the configuration files in the default folder.
            --splunk-host=<hostname>                                    # Receiver Splunk instance where events are searchable.
            --splunk-port=<splunk_management_port>                      # default 8089
            --splunk-user=<username>                                    # default admin     
            --splunk-password=<password>                                # default Chang3d!
            --splunk-forwarder-host=<splunk_forwarder_host>             # Splunk instance where forwarding to receiver instance is configured.                
            --splunk-hec-port=<splunk_forwarder_hec_port>               # HEC port of the forwarder instance.
            --splunk-hec-token=<splunk_forwarder_hec_token>             # HEC token configured in forwarder instance.
            --splunk-data-generator=<pytest_splunk_addon_conf_path>     # Path to pytest-splunk-addon-data.conf

.. note::
   * Forwarder params are supported only for external splunk-type.
   * If Forwarder params are not provided It will ingest and search in the same Splunk deployment provided in --splunk-host param.


----------------------

There are 3 types of tests included in pytest-splunk-addon are:

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

    * To execute all the searchtime tests together, i.e both Knowledge objects and CIM compatibility tests, 
      append the following marker to the pytest command:

        .. code-block:: console

            -m  "splunk_searchtime_fields or splunk_searchtime_cim"     

----------------------

The following optional arguments are available to modify the default settings in the test cases:

    1. To search for events in a specific index, user can provide following additional arguments:

        .. code-block:: console

            --search-index=<index>

                Splunk index of which the events will be searched while testing. Default value: "*, _internal".


    2. To increase/decrease time interval and retries for flaky tests, user can provide following additional arguments:

        .. code-block:: console

            --search-retry=<retry>

                Number of retries to make if there are no events found while searching in the Splunk instance. Default value: 0.

            --search-interval=<interval>

                Time interval to wait before retrying the search query.Default value: 0.

    3. To discard the eventlog generation in the working directory, user can provide following additional argument along with pytest command:

        .. code-block:: console

            --discard-eventlogs

    4. To enable the Splunk Index cleanup performed before the test run, user can provide argument along with pytest command:

        .. code-block:: console

            --splunk-cleanup
    
    5. A new functionality is introduced in pytest-splunk-addon to suppress unwanted errors in **test_splunk_internal_errors**.

            - **Splunk related errors**: There is a file maintained in pytest-splunk-addon `".ignore_splunk_internal_errors" <https://github.com/splunk/pytest-splunk-addon/blob/develop/pytest_splunk_addon/.ignore_splunk_internal_errors>`_ , user can add the string in the file and events containing these strings will be suppressed by the search query.
            - **Addon related errors:** To suppress these user can create a file with the list of strings and provide the file in the **--ignore-addon-errors** param while test execution.

        .. code-block:: console

            --ignore-addon-errors=<path_to_file>
                
        - Sample strings in the file.

        .. code-block:: console

            SearchMessages - orig_component="SearchStatusEnforcer"
            message_key="" message=NOT requires an argument

        .. Note ::
            *Each line in the file will be considered a separate string to be ignored in the events.*
        
        - Sample Event which will be ignored by the search query.
        
        .. code-block:: console

            11-04-2020 13:26:01.026 +0000 ERROR SearchMessages - orig_component="SearchStatusEnforcer" app="search" sid="ta_1604496283.232" peer_name="" message_key="" message=NOT requires an argument
        
    

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

    .. dropdown:: enable_saved_search_conftest.py

        .. literalinclude:: ../tests/enable_saved_search_conftest.py
            :language: python
            :lines: 2,31-


**4. Check mapping of an add-on with custom data models**

    pytest-splunk-addon is capable of testing mapping of an add-on with custom data models.

    How can this be achieved :

        - Make json representation of the data models, which satisfies this `DataModelSchema <https://github.com/splunk/pytest-splunk-addon/blob/main/pytest_splunk_addon/standard_lib/cim_tests/DatamodelSchema.json>`_.
        - Provide the path to the directory having all the data models by adding ``--splunk_dm_path path_to_dir`` to the pytest command
        - The test cases will now be generated for the data models provided to the plugin and not for the `default data models <https://github.com/splunk/pytest-splunk-addon/tree/main/pytest_splunk_addon/standard_lib/data_models>`_.

.. raw:: html

   <hr width=100%>
   
.. [#] xfail indicates that you expect a test to fail for some reason. A common example is a test for a feature not yet implemented, or a bug not yet fixed. When a test passes despite being expected to fail, it's an xpass and will be reported in the test summary.