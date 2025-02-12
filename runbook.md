# Runbook: Adding or Updating Data Model Support in pytest-splunk-addon

## Step 1: Obtain the Latest Data Model JSON
- Download the latest version of the required data model JSON file from Splunk’s Common Information Model (CIM).

## Step 2: Compare with Existing Supported Data Model
- Identify the current version of the data model supported in `pytest-splunk-addon`.
- Prepare a comparison sheet outlining the differences between the latest version and the existing supported version.
  - Highlight new fields.
  - Identify removed fields.
  - Note changes in field properties (e.g., required status, description, expected values).

## Step 3: Handling a New Data Model (If Not Previously Supported)
- If the data model is new and not already supported in `pytest-splunk-addon`, document all its fields in the sheet.
  - **Field name**
  - **Required or optional**
  - **Field description**
  - **Expected values and constraints**

## Step 4: Review with Subject Matter Experts (SMEs)
- Share the prepared sheet with SMEs for validation.
- Incorporate feedback and make necessary adjustments.

## Step 5: Implement Changes in pytest-splunk-addon
- Modify the necessary code and configurations to support the updated/new data model.
- Ensure proper integration with the existing framework.
  - **Update Data Model JSON File**: Add or update the JSON file inside `pytest_splunk_addon/data_models/`.
  - **Update Data Model Definitions**: Modify `pytest_splunk_addon/CIM_Models/datamodel_definition.py` to reflect changes:
    - Add/update the recommended fields.
    - Ensure consistency with the updated data model.
  - **Update End-to-End (E2E) Tests**: Modify existing tests or add new tests to validate the new/updated data model support.
    - Run the test suite to verify successful integration.

## Step 6: Final Validation
- Tests the build with few tier 1 TAs and few TAs that are using SC4S.
    - Test using beta build:
        - If the beta build is already published in the pypi, you can update the version in the pyproject.toml file to point to the beta release and draft a PR to trigger a GitHub pipeline to execute knowledge tests
    - Test using local build:
        - If the beta build is not published in pypi, you can create build in local using `poetry build` command and then copy the build file into the TAs repo.
        - Update the pyproject.toml of the TA repo to point to local build of pytest-splunk-addon and run the `poetry lock` to reflect the changes in the lock file.
        For ex. `pytest-splunk-addon = {path = "./pytest_splunk_addon-5.4.1.tar.gz"}`
- Analyse the failures and validate that all the new failures are related to the changes in the data model.

---

This runbook ensures a structured approach to integrating new or updated data model support in `pytest-splunk-addon`, maintaining accuracy and consistency.
