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

Note: Must install docker desktop, vscode or pycharm pro optional

Note2: Appinspect requires libmagic verify this has been installed correctly each time a new workstation/vm is used https://dev.splunk.com/enterprise/docs/releaseapps/appinspect/splunkappinspectclitool/installappinspect

    $ #setup python venv must be 3.7

    $ /Library/Frameworks/Python.framework/Versions/3.7/bin/python3 -m venv .venv

    $ source .venv/bin/activate

    $ pip3 install -r requirements_dev.txt

    $ pip3 install https://download.splunk.com/misc/appinspect/splunk-appinspect-latest.tar.gz

    $ python setup.py develop
    


Usage
-----

* TODO

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

.. _`Apache Software License 2.0`: http://www.apache.org/licenses/LICENSE-2.0
.. _`file an issue`: https://github.com/splunk/pytest-splunk-addon/issues
.. _`pytest`: https://github.com/pytest-dev/pytest
.. _`pip`: https://pypi.org/project/pip/
.. _`PyPI`: https://pypi.org/project
