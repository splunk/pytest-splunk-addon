===================
pytest-splunk-addon
===================

.. image:: https://img.shields.io/pypi/v/pytest-splunk-addon.svg
    :target: https://pypi.org/project/pytest-splunk-addon
    :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/pytest-splunk-addon.svg
    :target: https://pypi.org/project/pytest-splunk-addon
    :alt: Python versions

.. image:: https://travis-ci.org/splunk/pytest-splunk-addon.svg?branch=master
    :target: https://travis-ci.org/splunk/pytest-splunk-addon
    :alt: See Build Status on Travis CI

.. image:: https://ci.appveyor.com/api/projects/status/github/splunk/pytest-splunk-addon?branch=master
    :target: https://ci.appveyor.com/project/splunk/pytest-splunk-addon/branch/master
    :alt: See Build Status on AppVeyor

A Dynamic test tool for Splunk Apps and Add-ons

----

This `pytest`_ plugin was generated with `Cookiecutter`_ along with `@hackebrot`_'s `cookiecutter-pytest-plugin`_ template.


Features
--------

* TODO


Requirements
------------

* TODO


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
Contributions are very welcome. Tests can be run with `tox`_, please ensure
the coverage at least stays the same before you submit a pull request.

License
-------

Distributed under the terms of the `Apache Software License 2.0`_ license, "pytest-splunk-addon" is free and open source software


Issues
------

If you encounter any problems, please `file an issue`_ along with a detailed description.

.. _`Cookiecutter`: https://github.com/audreyr/cookiecutter
.. _`@hackebrot`: https://github.com/hackebrot
.. _`MIT`: http://opensource.org/licenses/MIT
.. _`BSD-3`: http://opensource.org/licenses/BSD-3-Clause
.. _`GNU GPL v3.0`: http://www.gnu.org/licenses/gpl-3.0.txt
.. _`Apache Software License 2.0`: http://www.apache.org/licenses/LICENSE-2.0
.. _`cookiecutter-pytest-plugin`: https://github.com/pytest-dev/cookiecutter-pytest-plugin
.. _`file an issue`: https://github.com/splunk/pytest-splunk-addon/issues
.. _`pytest`: https://github.com/pytest-dev/pytest
.. _`tox`: https://tox.readthedocs.io/en/latest/
.. _`pip`: https://pypi.org/project/pip/
.. _`PyPI`: https://pypi.org/project
