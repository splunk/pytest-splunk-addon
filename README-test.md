
# Run Addon tests in local environment
## With Kubernetes
### Prerequisitory
- Git
- Python3 (>=3.7)
- Kubernetes Cluster (Reference: [minikube](https://minikube.sigs.k8s.io/docs/start/), [microk8s](https://microk8s.io/), [k3s](https://k3s.io/))
- kubectl
- jq
- [splunk-operator at cluster-scope](https://splunk.github.io/splunk-operator/Install.html#admin-installation-for-all-namespaces)
```bash
kubectl apply -f ./splunk-operator.yaml
```
### Steps
#### 1. Clone the repository

```bash
git clone git@github.com:splunk/<repo name>.git
cd <repo dir>
```
#### 2. Run Tests

1. Install Requirements
```bash
poetry export --without-hashes --dev -o requirements_dev.txt
pip install -r requirements_dev.txt
```

2. Generate addon SPL
- For UCC based addons generate addon SPL with [ucc-gen --ta-version=<package/default/app.conf/id.version>](https://splunk.github.io/addonfactory-ucc-generator/).
- For Non-UCC based addons generate addon SPL of format `<package/default/app.conf/id.name>-<package/default/app.conf/id.version>.spl`

##### Knowledge

3. Create `src` directory in `tests` of the addon repository and put the SPL generated in step-2 in `tests/src`.

4. Execute Tests
- Default value of `--splunk-version=latest`
```bash
python -m pytest -vv tests/knowledge --splunk-data-generator=<path to pytest-splunk-addon-data.conf file> --splunk-type=kubernetes --splunk-version=<SPLUNK_VERSION> --xfail-file=.pytest.expect
```
**Note:** For debugging purposes if resources need to be kept then pass `--keep-alive` while executing above pytest command, after troubleshooting user will have to manually delete the kubernetes resources using following commands.
```bash
export NAMESPACE_NAME="<namespace_name>"  # namespace_name is of format splunk-ta-juniper (package/default/app.conf/id.name = Splunk_TA_juniper)
kubectl delete deploy sc4s -n $NAMESPACE_NAME
kubectl delete deploy splunk-uf -n $NAMESPACE_NAME
kubectl delete secret splunk-$NAMESPACE_NAME-secret -n $NAMESPACE_NAME
kubectl delete Standalone s1 -n $NAMESPACE_NAME
kubectl delete ns $NAMESPACE_NAME
```


## With External
### Prerequisitory

- Git
- Python3 (>=3.7)
- Splunk along with addon installed and HEC token created
- If Addon support the syslog data ingestion(sc4s)
  - Kubernetes Cluster
  - kubectl

### Steps

1. Clone the repository
```bash
git clone git@github.com:splunk/<repo name>.git
cd <repo dir>
```

2. Install Requirements
```bash
pip install poetry
poetry export --without-hashes --dev -o requirements_dev.txt
pip install -r requirements_dev.txt
```

3. Setup SC4S (for SC4S based addons)
- Create required SC4S indexes in splunk-instance using the following SPL
```
wget $( curl -s https://api.github.com/repos/splunk/splunk-configurations-base-indexes/releases/latest \ | jq -r '.assets[] | select((.name | contains("spl")) and (.name | contains("search_head") | not) and (.name | contains("indexers") | not ) and (.name | contains("forwarders") | not)) | .browser_download_url ')
```
- Get `sc4s_deployment.yaml`, `sc4s_service.yaml` which will be found at `pytest-splunk-addon/k8s_manifests/sc4s` and put into the root directory of addon repository, also update the `SPLUNK_URL` and `SPLUNK_HEC_TOKEN` in `sc4s_deployment.yaml` for which SC4S deployment and service will be created in separate namespace.
```bash
export NAMESPACE_NAME="splunk-ta-<ADDON_NAME>"
export SPLUNK_URL=<splunk_url>
export SPLUNK_HEC_TOKEN=<splunk_hec_token>
kubectl create ns $NAMESPACE_NAME
kubectl apply -f ./sc4s_service.yaml -n $NAMESPACE_NAME
envsubst < ./sc4s_deployment.yaml > ./sc4s_deployment.yaml
kubectl apply -f ./sc4s_deployment.yaml -n $NAMESPACE_NAME
kubectl wait pod -n $NAMESPACE_NAME --for=condition=ready --timeout=900s -l='app=sc4s'
kubectl port-forward svc/sc4s-service -n $NAMESPACE_NAME :514 > ./exposed_sc4s_ports.log 2>&1 &
```
- Get the mapped port of 514 and update the pytest.ini accordingly for --sc4s-port=<sc4s_port> and --sc4s-host=<sc4s_host>(`localhost`)
- Once test execution is completed then make sure to delete kubernetes resources
```bash
kubectl delete ns $NAMESPACE_NAME
```

4. Run Tests
#### Knowledge

```bash
python -m pytest -vv --splunk-type=external --splunk-app=<path-to-addon-package> --splunk-data-generator=<path to pytest-splunk-addon-data.conf file> --splunk-host=<splunk_host> --splunk-port=<splunk_management_port> --splunk-user=<splunk_username> --splunk-password=<splunk_password> --splunk-hec-token=<splunk_hec_token> --sc4s-host=<sc4s_host> --sc4s-port=<sc4s_port>
```

#### UI
1. Set all variables in environment mentioned at [test_credentials.env](test_credentials.env) file with appropriate values encoded with base64.
2. Download Browser's specific driver
    - For Chrome: download chromedriver
    - For Firefox: download geckodriver
3. Put the downloaded driver into `test/ui/` directory, make sure that it is within the environment's PATH variable, and that it is executable
4. Execute the test cases

- To execute the tests on saucelabs set the required env variable for saucelabs

```
export SAUCE_USERNAME=<username>
export SAUCE_PASSWORD=<password>
export JOB_NAME="Local::<addon-name>-browser-<unique-string>"
```
>- Best practice is to keep the JOB_NAME unique for each test execution
- Remove --local param from the below pytest command and tests will be executed on saucelabs
```bash
python -m pytest -vv --browser=<browser> --local --splunk-host=<splunk_host> --splunk-port=<splunk_mgmt_port> --splunk-user=<splunk_username> --splunk-password=<splunk_password> --splunk-hec-token=<splunk_hec_token>
```

#### Modinput
  - Install [splunk-add-on-for-modinput-test](https://github.com/splunk/splunk-add-on-for-modinput-test/releases/latest/) addon in splunk and set all variables in environment mentioned at [test_credentials.env](test_credentials.env) file with appropriate values encoded with base64 or add variables in pytest command mentioned in conftest file.
  - Update the pytest command with additional params if required for the addon.

```bash
python -m pytest -vv --username=<splunk_username> --password=<splunk_password> --splunk-url=<splunk_url> --remote
```