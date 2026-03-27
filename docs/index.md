# Overview

pytest-splunk-addon is an open-source dynamic test plugin for Splunk [Apps](https://docs.splunk.com/Splexicon:App) and [Add-ons](https://docs.splunk.com/Splexicon:Addon)
which allows the user to test [knowledge objects](https://docs.splunk.com/Splexicon:Knowledgeobject), [CIM](https://docs.splunk.com/Splexicon:CommonInformationModel) compatibility and [index time properties](https://docs.splunk.com/Splexicon:Indexedfield).

## Prerequisites

- Splunk App or Add-on package
- Splunk instance with App or Add-on installed (Not required if using Docker)
- Docker (Not required if using external Splunk instance)

## Support

- **Python**: 3.7
- **Platforms**: Linux, Windows and MacOS

## Installation

pytest-splunk-addon can be installed via pip from PyPI:

```console
pip3 install pytest-splunk-addon
```

## Features

The pytest-splunk-addon works by dynamically generating different types of tests for Splunk apps and add-ons by parsing their configuration files. Specifically, it looks at the .conf files in the provided Splunk app/add-on to create:

1. [Knowledge Object Tests](./field_tests.md)

2. [CIM Compatibility Tests](./cim_tests.md)

3. [Index-Time Field Tests](./index_time_tests.md)

4. [Requirement Tests](./requirement_tests.md)

Refer to the [How to use](./how_to_use.md) section for detailed instructions on running the tests.

## Release notes

Find details about all the releases [here](https://github.com/splunk/pytest-splunk-addon/releases).
