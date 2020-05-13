
How To Use
----------

Create a test file in the tests folder

.. code:: python3

    from pytest_splunk_addon.standard_lib.addon_basic import Basic
        class Test_App(Basic):
            def empty_method():
                pass

The tool assumes the Splunk Add-on is located in a folder "package" in the project root if not

**Running tests with external splunk**

.. code:: python3

    pip install pytest-splunk-addon

Run pytest with the add-on and SA-eventgen installed and enabled in an external Splunk deployment

.. code:: bash

    pytest -v --splunk-type=external --splunk-host=<hostname> --splunk-port=<splunk-management-port> --splunk-user=<username> --splunk-password=<password>

**Running tests with docker splunk**

.. code:: bash

    pip install pytest-splunk-addon[docker]

Create a Dockerfile-splunk file 

.. literalinclude:: ../Dockerfile.splunk

Create a docker-compose.yml

.. literalinclude:: ../docker-compose.yml

Run pytest with the add-on and SA-eventgen installed and enabled in docker

.. code:: bash

    pytest --splunk-password=Changed@11 -v
