# Contributing Guidelines


# Prerequisites:

- Poetry 1.5.1. [Installation guide](https://python-poetry.org/docs/#installing-with-the-official-installer)

# Installation

You can install "pytest-splunk-addon" via [pip] from [PyPI]:

```
$ pip install pytest-splunk-addon
```

To install currently checked out version of pytest-splunk-addon use:
```
$ poetry install
```


### Unit tests

```bash
poetry run pytest -v tests/unit
```

### e2e tests

- For e2e tests we are using a functionality of pytest which creates a temp dir and copies all the required file to that dir and then runs the pytest cmd from the tests.
- e2e tests can be found under /tests/e2e

Prerequisites:

- Docker version: 25.0.3
- Docker Compose version: v2.24.6-desktop.1

Steps to run e2e tests locally:

```
git clone --recurse-submodules -j8 git@github.com:splunk/pytest-splunk-addon.git
cd pytest-splunk-addon 
poetry install 
poetry run pytest -v --splunk-version=${splunk-version} -m docker -m ${test-marker} tests/e2e
```

### Troubleshooting:

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


## Linting and Type-checking

`Pytest-splunk-addon` uses the [`pre-commit`](https://pre-commit.com) framework for linting and type-checking.
Consult with `pre-commit` documentation about what is the best way to install the software.

To run it locally:

```bash
pre-commit run --all-files
```

## Documentation changes

Documentation changes are also welcome!

To verify changes locally:

```bash
poetry run mkdocs serve -a localhost:8001
```

## Issues and bug reports

You can create an [issue](https://github.com/splunk/pytest-splunk-addon/issues) on GitHub.

## Pull requests

We love to see pull requests!

We are using [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/).
The two most important types: "fix" and "feat", would result in the new version of the `Pytest-splunk-addon` once merged.

To do the changes you think are needed, run the previous steps (build / test / linting / documentation).
Create a PR to develop and once reviewed by code-owners make sure to use squash-merge option.

Note: The `semgrep` and `fossa` steps might fail if you are an external contributor. This is expected for now.
