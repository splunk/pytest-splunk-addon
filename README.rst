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
* Validate your add-ons using Splunk + Kubernetes and this test tool


Requirements
------------

* Kubernetes or an external single instance Splunk deployment


Installation
------------

You can install "pytest-splunk-addon" via `pip`_ from `PyPI`_::

    $ pip install pytest-splunk-addon

Developing
------------

Note: Must setup kubernetes cluster, vscode or pycharm pro optional

Note2: Appinspect requires libmagic verify this has been installed correctly each time a new workstation/vm is used https://dev.splunk.com/enterprise/docs/releaseapps/appinspect/splunkappinspectclitool/installappinspect

.. code:: bash

    $ git clone --recurse-submodules -j8 git@github.com:splunk/pytest-splunk-addon.git

    $ #setup python venv must be 3.7    
    $ python3 -m venv .venv

    $ source .venv/bin/activate

    $ cd pytest-splunk-addon
    
    $ pip install poetry

    $ poetry export --without-hashes --dev -o requirements_dev.txt

    $ pip install -r requirements_dev.txt


Usage
-----

Installation for external Splunk and with built in Kubernetes orchestration

.. code:: bash

    pip install pytest-splunk-addon


Basic project structure

The tool assumes the Splunk Add-on is located in a folder "package" in the project root

Triggering the tool: 

Create a test file in the tests folder

.. code:: python3

    from pytest_splunk_addon.standard_lib.addon_basic import Basic
        class Test_App(Basic):
            def empty_method():
                pass

Run pytest with the add-on and SA-eventgen installed and enabled in an external Splunk deployment

.. code::: bash

        pytest \
        --splunk-type=external \
        --splunk-host=splunk \
        --splunk-port=8089 \
        --splunk-password=Changed@11 \
        -v

Run pytest with the add-on and SA-eventgen installed and enabled in kubernetes

.. code::: bash

        pytest \
        --splunk-type=kubernetes \
        -v

For full usage instructions, please visit the `pytest-splunk-addon documentation pages over at readthedocs`_.

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
