#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import os

from setuptools import setup, find_packages


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding='utf-8').read()



setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest>=5', ]

setup(
    name='pytest-splunk-addon',
    version='0.1.0',
    author='Splunk, Inc.',
    author_email='appinspect@splunk.com',
    include_package_data=True,
    maintainer='Splunk, Inc.',
    maintainer_email='appinspect@splunk.com',
    license='Apache Software License 2.0',
    url='https://github.com/splunk/pytest-splunk-addon',
    description='A Dynamic test tool for Splunk Apps and Add-ons',
    long_description=read('README.rst'),
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
    install_requires=[
        'pytest',

    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: Apache Software License',
    ],
    packages=find_packages(include=['pytest_splunk_addon', 'pytest_splunk_addon.*']),

    test_suite='tests',

    zip_safe=False,
    entry_points={'pytest11': ['splunk_addon = pytest_splunk_addon.plugin']}
)
