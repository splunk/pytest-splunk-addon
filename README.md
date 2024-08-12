# pytest-splunk-addon

![PyPI](<https://img.shields.io/pypi/v/pytest-splunk-addon>)
![Python](<https://img.shields.io/pypi/pyversions/pytest-splunk-addon.svg>)

## What is PSA

A Dynamic test tool for Splunk Apps and Add-ons.

## Usage

For full usage instructions, please visit the \[documentation\](<https://splunk.github.io/pytest-splunk-addon>).

# Requirements

- Docker or an external single instance Splunk deployment

# Installation

You can install "pytest-splunk-addon" via [pip] from [PyPI]:

```
$ pip install pytest-splunk-addon
```

# Run e2e tests locally

- For e2e tests we are using a functionality of pytest which creates a temp dir and copies all the required file to that dir and then runs the pytest cmd from the tests.
- e2e tests can be found under /tests/e2e

Prerequisites:

- Docker version: 25.0.3
- Docker Compose version: v2.24.6-desktop.1

```
git clone --recurse-submodules -j8 git@github.com:splunk/pytest-splunk-addon.git $ cd pytest-splunk-addon $ poetry install $ poetry run pytest -v --splunk-version=${splunk-version} -m docker -m ${test-marker} tests/e2e
```

Troubleshooting:

1. If you face an error like this:

    > argparse.ArgumentError: argument -K/--keepalive: conflicting option strings: -K, --keepalive
   
    - This is likely to happen if you have older version of PSA requirements installed, to solve this try to uninstall lovely-pytest-docker and pull the latest main branch and then do `poetry install`

2. If while running the tests you face an exception like this:

    > Exception: Command ['docker', 'compose', '-f', '<path>/docker-compose.yml', '-p', '<projectname>', 'down', '-v'] returned 125: """unknown shorthand flag: 'f' in -f
   
    - This happens due to misconfigurations in docker, try to follow below steps:
       - sudo mkdir -p /usr/local/lib/docker
        - sudo ln -s /Applications/Docker.app/Contents/Resources/cli-plugins /usr/local/lib/docker/cli-plugins

3. If you face error like this:

    > ERROR: no match for platform in manifest: not found
   
    - Try adding platform: `linux/amd64` to docker-compose.yml file

# Contributing

Contributions are very welcome. Tests can be run with [pytest], please ensure
the coverage at least stays the same before you submit a pull request.

# License

Distributed under the terms of the [Apache Software License 2.0] license, "pytest-splunk-addon" is free and open source software
