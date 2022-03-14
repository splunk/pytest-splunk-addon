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

Note: Must setup kubernetes cluster [ Reference: `minikube`_ , `microk8s`_, `k3s`_ ]

.. code:: bash

    $ git clone --recurse-submodules -j8 git@github.com:splunk/pytest-splunk-addon.git
    $ cd pytest-splunk-addon
    $ poetry install
    $ export KUBECONFIG="PATH of Kubernetes Config File" [For example, minikube($HOME/kube/config), k3s(/etc/rancher/k3s/k3s.yaml)]

Generate addons spl (tests/e2e/addons/<ADDON_NAME>) with format ``<ADDON_NAME>-<ADDON_VERSION>.spl``

.. code:: bash

    # run unit tests
    $ poetry run pytest tests/unit
    # run some of the kubernetes-based tests to verify end-to-end behaviour, example:
    $ poetry run pytest -v --splunk-version=8.2 -m kubernetes tests/e2e/test_splunk_addon.py::test_splunk_app_requirements_modinput

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

.. code:: python3

        pytest \
        --splunk-type=external \
        --splunk-host=splunk \
        --splunk-port=8089 \
        --splunk-password=Changed@11 \
        -v

Run pytest with the add-on and SA-eventgen installed and enabled in kubernetes

Deploy `splunk-operator at cluster-scope in kubernetes cluster`_.

Generate addon SPL with `ucc-gen`_.

For third-party addons generate addon SPL.

Place the generated addon spl in tests/src/<addon>.spl

.. code:: python3

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
.. _`minikube`: https://minikube.sigs.k8s.io/docs/start/
.. _`microk8s`: https://microk8s.io/
.. _`k3s`: https://k3s.io/
.. _`ucc-gen` : https://splunk.github.io/addonfactory-ucc-generator/
.. _`splunk-operator at cluster-scope in kubernetes cluster` : https://splunk.github.io/splunk-operator/Install.html#admin-installation-for-all-namespaces