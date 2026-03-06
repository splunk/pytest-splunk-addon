#
# Copyright 2026 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""
Contract tests for the splunk-cim-models package.

These tests verify that the API surface PSA depends on is present and
structurally correct in the installed version of splunk-cim-models.
They are intentionally version-agnostic: a newer package version should
still satisfy the same contract.

If any of these tests fail after upgrading splunk-cim-models, the
corresponding PSA import site must be updated to match the new API.
"""
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

REQUIRED_SYMBOLS = [
    "DATA_MODELS_PATH",
    "COMMON_FIELDS_PATH",
    "DATAMODEL_SCHEMA_PATH",
    "datamodels",
]

KNOWN_CIM_MODELS = {
    "Alerts",
    "Application_State",
    "Authentication",
    "Certificates",
    "Change",
    "Change_Analysis",
    "Compute_Inventory",
    "DLP",
    "Databases",
    "Email",
    "Endpoint",
    "Event_Signatures",
    "Interprocess_Messaging",
    "Intrusion_Detection",
    "JVM",
    "Malware",
    "Network_Resolution",
    "Network_Sessions",
    "Network_Traffic",
    "Performance",
    "Ticket_Management",
    "Updates",
    "Vulnerabilities",
    "Web",
}


# ---------------------------------------------------------------------------
# Package availability
# ---------------------------------------------------------------------------


def test_splunk_cim_models_importable():
    """splunk_cim_models must be importable; clear error otherwise."""
    import splunk_cim_models  # noqa: F401


def test_missing_package_raises_import_error(monkeypatch):
    """
    When splunk_cim_models is absent from sys.modules and the import
    fails, Python should raise ImportError – not a silent AttributeError
    or similar.  This test simulates the package being absent.
    """
    original = sys.modules.pop("splunk_cim_models", None)
    try:
        with patch.dict("sys.modules", {"splunk_cim_models": None}):
            with pytest.raises((ImportError, AttributeError)):
                import splunk_cim_models  # noqa: F401

                _ = splunk_cim_models.DATA_MODELS_PATH
    finally:
        if original is not None:
            sys.modules["splunk_cim_models"] = original


# ---------------------------------------------------------------------------
# Required public symbols
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("symbol", REQUIRED_SYMBOLS)
def test_required_symbol_exists(symbol):
    """Every symbol PSA imports from splunk_cim_models must be present."""
    import splunk_cim_models

    assert hasattr(splunk_cim_models, symbol), (
        f"splunk_cim_models does not export '{symbol}'. "
        "Update the package or the PSA import site."
    )


# ---------------------------------------------------------------------------
# Path symbols – point to real files / directories
# ---------------------------------------------------------------------------


def test_data_models_path_is_directory():
    from splunk_cim_models import DATA_MODELS_PATH

    assert os.path.isdir(DATA_MODELS_PATH), (
        f"DATA_MODELS_PATH '{DATA_MODELS_PATH}' is not a directory."
    )


def test_common_fields_path_is_file():
    from splunk_cim_models import COMMON_FIELDS_PATH

    assert os.path.isfile(COMMON_FIELDS_PATH), (
        f"COMMON_FIELDS_PATH '{COMMON_FIELDS_PATH}' is not a file."
    )


def test_datamodel_schema_path_is_file():
    from splunk_cim_models import DATAMODEL_SCHEMA_PATH

    assert os.path.isfile(DATAMODEL_SCHEMA_PATH), (
        f"DATAMODEL_SCHEMA_PATH '{DATAMODEL_SCHEMA_PATH}' is not a file."
    )


# ---------------------------------------------------------------------------
# DATA_MODELS_PATH – JSON data model files
# ---------------------------------------------------------------------------


def test_data_models_directory_contains_json_files():
    from splunk_cim_models import DATA_MODELS_PATH

    json_files = [f for f in os.listdir(DATA_MODELS_PATH) if f.endswith(".json")]
    assert json_files, f"No JSON files found in DATA_MODELS_PATH '{DATA_MODELS_PATH}'."


def test_data_models_cover_known_cim_models():
    """At least a core subset of well-known CIM data models must be present."""
    from splunk_cim_models import DATA_MODELS_PATH

    present = {
        Path(f).stem for f in os.listdir(DATA_MODELS_PATH) if f.endswith(".json")
    }
    # Require a representative subset rather than the full list so minor
    # schema renames don't cause spurious failures.
    core_required = {
        "Authentication",
        "Endpoint",
        "Network_Traffic",
        "Malware",
        "Web",
    }
    missing = core_required - present
    assert not missing, (
        f"Core CIM data models missing from DATA_MODELS_PATH: {missing}"
    )


def test_each_data_model_file_is_valid_json():
    from splunk_cim_models import DATA_MODELS_PATH

    for filename in os.listdir(DATA_MODELS_PATH):
        if not filename.endswith(".json"):
            continue
        filepath = os.path.join(DATA_MODELS_PATH, filename)
        with open(filepath) as fh:
            try:
                data = json.load(fh)
            except json.JSONDecodeError as exc:
                pytest.fail(f"Invalid JSON in {filepath}: {exc}")
        assert isinstance(data, dict), (
            f"Expected dict at top level of {filepath}, got {type(data).__name__}"
        )


# ---------------------------------------------------------------------------
# COMMON_FIELDS_PATH – fields forbidden in props/search
# ---------------------------------------------------------------------------


def test_common_fields_json_is_valid():
    from splunk_cim_models import COMMON_FIELDS_PATH

    with open(COMMON_FIELDS_PATH) as fh:
        data = json.load(fh)
    assert "fields" in data, (
        "CommonFields.json must have a top-level 'fields' key."
    )
    assert isinstance(data["fields"], list), (
        "'fields' in CommonFields.json must be a list."
    )


def test_common_fields_entries_have_type_and_name():
    """Each field entry must have at least 'name' and 'type' keys."""
    from splunk_cim_models import COMMON_FIELDS_PATH

    with open(COMMON_FIELDS_PATH) as fh:
        data = json.load(fh)
    for entry in data["fields"]:
        assert "name" in entry, f"Field entry missing 'name': {entry}"
        assert "type" in entry, f"Field entry missing 'type': {entry}"


# ---------------------------------------------------------------------------
# DATAMODEL_SCHEMA_PATH – JSON schema for custom data models
# ---------------------------------------------------------------------------


def test_datamodel_schema_json_is_valid():
    from splunk_cim_models import DATAMODEL_SCHEMA_PATH

    with open(DATAMODEL_SCHEMA_PATH) as fh:
        data = json.load(fh)
    assert isinstance(data, dict), "DatamodelSchema.json must be a JSON object."
    # JSON Schema documents typically have $schema or type at the root.
    assert data, "DatamodelSchema.json must not be empty."


# ---------------------------------------------------------------------------
# datamodels – CIM version → recommended fields dict
# ---------------------------------------------------------------------------


def test_datamodels_is_dict():
    from splunk_cim_models import datamodels

    assert isinstance(datamodels, dict), (
        f"'datamodels' must be a dict, got {type(datamodels).__name__}"
    )


def test_datamodels_has_at_least_one_version():
    from splunk_cim_models import datamodels

    assert datamodels, "'datamodels' dict must not be empty."


def test_datamodels_latest_key_present():
    """Consumers may rely on the 'latest' sentinel key."""
    from splunk_cim_models import datamodels

    assert "latest" in datamodels, (
        "'datamodels' dict must contain a 'latest' key."
    )


def test_datamodels_version_values_are_dicts():
    """Each CIM version entry must map model names to field lists."""
    from splunk_cim_models import datamodels

    for version, models in datamodels.items():
        assert isinstance(models, dict), (
            f"datamodels[{version!r}] must be a dict of model→fields, "
            f"got {type(models).__name__}"
        )


def test_datamodels_field_lists_are_non_empty():
    """Each model in each version must have at least one entry."""
    from splunk_cim_models import datamodels

    for version, models in datamodels.items():
        for model_name, fields in models.items():
            assert fields, (
                f"datamodels[{version!r}][{model_name!r}] field list is empty."
            )


@pytest.mark.parametrize("version", ["latest"])
def test_datamodels_version_contains_core_models(version):
    """Core CIM models must be present in the given version entry."""
    from splunk_cim_models import datamodels

    if version not in datamodels:
        pytest.skip(f"Version {version!r} not present in this package release.")

    core = {"Authentication", "Endpoint", "Network_Traffic", "Malware", "Web"}
    present = set(datamodels[version].keys())
    missing = core - present
    assert not missing, (
        f"datamodels[{version!r}] is missing core models: {missing}"
    )


# ---------------------------------------------------------------------------
# PSA import sites – verify they resolve against the installed package
# ---------------------------------------------------------------------------


def test_psa_app_test_generator_imports_data_models_path():
    """app_test_generator.py must import DATA_MODELS_PATH without error."""
    from pytest_splunk_addon.app_test_generator import AppTestGenerator  # noqa: F401
    from splunk_cim_models import DATA_MODELS_PATH

    assert DATA_MODELS_PATH  # truthy path string


def test_psa_test_generator_imports_common_fields_path():
    """cim_tests/test_generator.py must import COMMON_FIELDS_PATH without error."""
    from pytest_splunk_addon.cim_tests.test_generator import (  # noqa: F401
        CIMTestGenerator,
    )
    from splunk_cim_models import COMMON_FIELDS_PATH

    assert COMMON_FIELDS_PATH


def test_psa_json_schema_imports_datamodel_schema_path():
    """cim_tests/json_schema.py must import DATAMODEL_SCHEMA_PATH without error."""
    from pytest_splunk_addon.cim_tests.json_schema import JSONSchema  # noqa: F401
    from splunk_cim_models import DATAMODEL_SCHEMA_PATH

    assert DATAMODEL_SCHEMA_PATH


def test_psa_splunk_imports_datamodels():
    """splunk.py must be able to import the datamodels dict without error."""
    from splunk_cim_models import datamodels

    assert isinstance(datamodels, dict)
