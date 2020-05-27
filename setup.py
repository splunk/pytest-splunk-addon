#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import os
from setuptools import setup, find_packages
import versioneer


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding="utf-8").read()


test_requirements = [
    "pytest>=5",
]

setup(
    name="pytest-splunk-addon",
    author="Splunk, Inc.",
    author_email="appinspect@splunk.com",
    include_package_data=True,
    maintainer="Splunk, Inc.",
    maintainer_email="appinspect@splunk.com",
    license="Apache Software License 2.0",
    url="https://github.com/splunk/pytest-splunk-addon",
    description="A Dynamic test tool for Splunk Apps and Add-ons",
    long_description=read("README.rst"),
    python_requires=">=3.0, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
    install_requires=[
        "pytest~=5.3",
        "splunk-sdk~=1.6",
        "future~=0.17.1",
        "httplib2~=0.17",
        "logutils",
        "junitparser==1.4.1",
        "requests2~=2.16",
        "splunk_appinspect>=2.0.1",
        "six",
        "jsonschema~=3.2.0",
    ],
    extras_require={"docker": ["lovely-pytest-docker>=0.1.0"]},
    setup_requires=["pytest-runner"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Pytest",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: Apache Software License",
    ],
    packages=find_packages(include=["pytest_splunk_addon", "pytest_splunk_addon.*"]),
    test_suite="tests",
    zip_safe=False,
    entry_points={
        "pytest11": [
            "plugin = pytest_splunk_addon.plugin",
            "splunk = pytest_splunk_addon.splunk",
        ],
        "console_scripts": ["cim-report=pytest_splunk_addon.standard_lib.cim_compliance.junit_parser:main"]
    },
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
)
