===================
pytest-splunk-addon
===================

.. image:: https://img.shields.io/pypi/v/pytest-splunk-addon.svg
    :target: https://pypi.org/project/pytest-splunk-addon
    :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/pytest-splunk-addon.svg
    :target: https://pypi.org/project/pytest-splunk-addon
    :alt: Python versions


A Dynamic test tool for Splunk Apps and Add-ons

Documentation
---------------
The detailed documentation for pytest-splunk-addon can be found here : `<https://pytest-splunk-addon.readthedocs.io/>`_

Features
--------

* Generate tests for Splunk Knowledge objects in your Splunk Technology Add-ons
* Validate your add-ons using Splunk + Docker and this test tool


Requirements
------------

* Docker or an external single instance Splunk deployment


Installation
------------

You can install "pytest-splunk-addon" via `pip`_ from `PyPI`_::

    $ pip install pytest-splunk-addon

Developing
------------

Note: Must install docker desktop.

.. code:: bash

    $ git clone --recurse-submodules -j8 git@github.com:splunk/pytest-splunk-addon.git
    $ cd pytest-splunk-addon
    $ poetry install
    $ ... (change something)
    # run unit tests
    $ poetry run pytest tests/unit
    # run some of the docker-based tests to verify end-to-end behaviour, example:
    $ poetry run pytest -v --splunk-version=8.2 -m docker tests/test_splunk_addon.py::test_splunk_app_requirements_modinput


Usage
-----

Installation for external Splunk

.. code:: bash

    pip install pytest-splunk-addon

Installation with built in docker orchestration

.. code:: bash

    pip install pytest-splunk-addon[docker]


Basic project structure

The tool assumes the Splunk Add-on is located in a folder "package" in the project root

Triggering the tool: 

Create a test file in the tests folder

.. code:: python3

    from pytest_splunk_addon.standard_lib.addon_basic import Basic


    class Test_App(Basic):
        def empty_method():
            pass

Create a Dockerfile-splunk file

.. code:: Dockerfile

    ARG SPLUNK_VERSION=latest
    FROM splunk/splunk:$SPLUNK_VERSION
    ARG SPLUNK_APP=TA_UNKNOWN
    ARG SPLUNK_APP_PACKAGE=package
    COPY deps/apps /opt/splunk/etc/apps/

    COPY $SPLUNK_APP_PACKAGE /opt/splunk/etc/apps/$SPLUNK_APP


Create a docker-compose.yml update the value of SPLUNK_APP

.. code:: yaml

    version: "3.7"
    services:
    splunk:
        build:
        context: .
        dockerfile: Dockerfile-splunk
        args:
            - SPLUNK_APP=xxxxxxx
        ports:
        - "8000"
        - "8089"
        environment:
        - SPLUNK_PASSWORD=Changed@11
        - SPLUNK_START_ARGS=--accept-license

Run pytest with the add-on and SA-eventgen installed and enabled in an external Splunk deployment

.. code::: bash

        pytest \
        --splunk-type=external \
        --splunk-type=external \
        --splunk-host=splunk \
        --splunk-port=8089 \
        --splunk-password=Changed@11 \
        -v

Run pytest with the add-on and SA-eventgen installed and enabled in docker

.. code::: bash

        pytest \
        --splunk-password=Changed@11 \
        -v

For full usage instructions, please visit the `pytest-splunk-addon documentation pages over at readthedocs`_.

Run e2e tests locally
---------------------

* For e2e tests we are using a functionality of pytest which creates a temp dir and copies all the required file to that dir and then runs the pytest cmd from the tests.
* e2e tests can be found under /tests/e2e

Note: Must install docker desktop.

.. code:: bash

    $ git clone --recurse-submodules -j8 git@github.com:splunk/pytest-splunk-addon.git
    $ cd pytest-splunk-addon
    $ poetry install
    $ poetry run pytest -v --splunk-version=${splunk-version} -m docker -m ${test-marker} tests/e2e


Contributing
------------
Contributions are very welcome. Tests can be run with `pytest`_, please ensure
the coverage at least stays the same before you submit a pull request.

License
-------

Distributed under the terms of the `Apache Software License 2.0`_ license, "pytest-splunk-addon" is free and open source software


Issues
------

If you encounter any problems, please `file an issue`_ along with a detailed description.

.. _`pytest-splunk-addon documentation pages over at readthedocs`: https://pytest-splunk-addon.readthedocs.io/en/latest/
.. _`Apache Software License 2.0`: http://www.apache.org/licenses/LICENSE-2.0
.. _`file an issue`: https://github.com/splunk/pytest-splunk-addon/issues
.. _`pytest`: https://github.com/pytest-dev/pytest
.. _`pip`: https://pypi.org/project/pip/
.. _`PyPI`: https://pypi.org/project
