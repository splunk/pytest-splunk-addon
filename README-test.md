
# Run Addon tests in local environment



## - With Kubernetes

### Prerequisitory - Kubernetes
- Git
- Python3 (>=3.7)
- kubectl
- jq
- [splunk-operator at cluster-scope](https://splunk.github.io/splunk-operator/Install.html#admin-installation-for-all-namespaces)
```bash
kubectl apply -f ./splunk-operator.yaml
```

### Steps - Kubernetes

1. Clone the repository
```bash
git clone git@github.com:splunk/<repo name>.git
cd <repo dir>
```

2. Run Tests

- Modinput_Functional / UI

1. Install Requirements and Generate Addon
```bash
poetry export --without-hashes --dev -o requirements_dev.txt
pip install -r requirements_dev.txt
ucc-gen

# Download only if TEST_TYPE is modinput_functional
curl -s https://api.github.com/repos/splunk/splunk-add-on-for-modinput-test/releases/latest | grep "Splunk_TA.*spl" | grep -v search_head | grep -v indexer | grep -v forwarder | cut -d : -f 2,3 | tr -d \" | wget -qi -;
```

2. Set Variables
```bash
export KUBECONFIG="PATH of Kubernetes Config File"
export NAMESPACE_NAME="splunk-ta-<ADDON_NAME>"

# If TEST_TYPE is ui also set the following variables
export TEST_BROWSER=<browser_name> [i.e. chrome, firefox]
export JOB_NAME=<LocalRun::[addon_name]-[browser]>
export SAUCE_USERNAME=<sauce_username>
export SAUCE_PASSWORD=<sauce_password>
export SAUCE_IDENTIFIER=$SAUCE_IDENTIFIER-$(cat /proc/sys/kernel/random/uuid)
export UI_TEST_HEADLESS="true"
```
**Note:** If TEST_TYPE is `modinput_functional` or `ui`, also set all variables in [test_credentials.env](test_credentials.env) file with appropriate values encoded with base64.

3. Update the value of NAMESPACE_NAME in [namespace.yaml](https://github.com/splunk/pytest-splunk-addon/blob/test/migrate-k8s-poc/pytest_splunk_addon/k8s_manifests/splunk_standalone/namespace.yaml) file and apply
```bash
eval "echo \"$(cat ./namespace.yaml)\"" >> ./namespace.yaml
kubectl apply -f ./namespace.yaml
```
4. Create secret (this will be used while spinning up the splunk standalone)
```bash
kubectl create secret generic splunk-$NAMESPACE_NAME-secret --from-literal='password=Chang3d!' --from-literal='hec_token=9b741d03-43e9-4164-908b-e09102327d22' -n $NAMESPACE_NAME
```

5. Update the SPLUNK_VERSION in [splunk_standalone.yaml](https://github.com/splunk/pytest-splunk-addon/blob/test/migrate-k8s-poc/pytest_splunk_addon/k8s_manifests/splunk_standalone/splunk_standalone.yaml) file for which Standalone machine will be created
```bash
eval "echo \"$(cat ./splunk_standalone.yaml)\"" >> ./splunk_standalone.yaml
kubectl apply -f ./splunk_standalone.yaml -n $NAMESPACE_NAME
```

6. Wait till Splunk Standalone is created
```bash
kubectl wait pod splunk-s1-standalone-0 --for=condition=ready --timeout=900s -n $NAMESPACE_NAME
```

7. Expose service of splunk standalone to access locally, all the ports will be mapped with freely available ports of local machine
```bash
kubectl port-forward svc/splunk-s1-standalone-service -n $NAMESPACE_NAME :8000 :8088 :8089 > ./exposed_splunk_ports.log 2>&1 &
```

8. Get the mapped ports of 8000, 8088, 8089 and update the pytest.ini accordingly.

9. Access the splunk ui and install the addon by "Install app from file",
> - http://localhost:splunk-web-port/
> - Install modinput helper addon downloaded in step-1 , as a prerequisite of execution of modinput tests.

10. If TEST_TYPE is `ui` then follow the below steps,
  - Download Browser's specific driver
    > - For Chrome: download chromedriver
    > - For Firefox: download geckodriver
    > - For IE: download IEdriverserver
  - Put the downloaded driver into `test/ui/` directory, make sure that it is within the environment's PATH variable, and that it is executable
  - For Internet explorer, The steps mentioned at below link must be performed [selenium](https://github.com/SeleniumHQ/selenium/wiki/InternetExplorerDriver#required-configuration)

11. Execute Tests
- Modinput_Functional
```bash
python -m pytest -v --username=admin --password=Chang3d! --splunk-url=localhost --splunkd-port=<splunk-management-port> --remote -n 5 tests/modinput_functional
```

- UI
```bash
python -m pytest -v --splunk-type=external --splunk-host=localhost --splunkweb-port=<splunk-web-port> --splunk-port=<splunk-management-port> --splunk-password=Chang3d! --browser=<browser> --splunk-hec-port=<splunk-hec-port> --local tests/ui 
```

12. Delete the ./exposed_splunk_ports.log file and other kubernetes resources
```bash
kubectl delete -f ./splunk_standalone.yaml -n $NAMESPACE_NAME
sleep 30
kubectl delete secret splunk-$NAMESPACE_NAME-secret -n $NAMESPACE_NAME
kubectl delete -f ./namespace.yaml -n $NAMESPACE_NAME
sleep 60
```

## - With External

### Prerequisitory - external
- Git
- Python3 (>=3.7)
- Python2
- Splunk along with addon installed and HEC token created
- If Addon support the syslog data ingestion(sc4s)
  - Docker
  - Docker-compose

### Steps - external

1. Clone the repository
```bash
git clone git@github.com:splunk/<repo name>.git
cd <repo dir>
```

2. Install Requirements
```bash
poetry export --without-hashes --dev -o requirements_dev.txt
pip install -r requirements_dev.txt
```

3. Setup SC4S (if required for KO tests)

- If addon requires sc4s, need to update following in docker-compose.yml used to spin sc4s, (docker-compose.yml is already present in addon repo)

- docker-compose.yml file contents

```
sc4s:
    image: splunk/scs:1.51.6
    hostname: sc4s
    #When this is enabled test_common will fail
    #    command: -det
    ports:
      - "514"
      - "601"
      - "514/udp"
      - "9000"
      - "5000-5050"
      - "5000-5050/udp"
      - "6514"
    stdin_open: true
    tty: true
    environment:
      - SPLUNK_HEC_URL=https://http-inputs-noah-stack-3.stg.splunkcloud.com:443
      - SPLUNK_HEC_TOKEN=751f7b50-423e-4ddb-bf00-cab5e3d7b982
      - SC4S_SOURCE_TLS_ENABLE=no
      - SC4S_DEST_SPLUNK_HEC_TLS_VERIFY=no
      - SC4S_LISTEN_CISCO_ESA_TCP_PORT=9000
      - SC4S_LISTEN_JUNIPER_NETSCREEN_TCP_PORT=5000
      - SC4S_LISTEN_CISCO_ASA_TCP_PORT=5001
      - SC4S_LISTEN_CISCO_IOS_TCP_PORT=5002
      - SC4S_LISTEN_CISCO_MERAKI_TCP_PORT=5003
      - SC4S_LISTEN_JUNIPER_IDP_TCP_PORT=5004
      - SC4S_LISTEN_PALOALTO_PANOS_TCP_PORT=5005
      - SC4S_LISTEN_PFSENSE_TCP_PORT=5006
      - SC4S_LISTEN_CISCO_ASA_UDP_PORT=5001
      - SC4S_LISTEN_CISCO_IOS_UDP_PORT=5002
      - SC4S_LISTEN_CISCO_MERAKI_UDP_PORT=5003
      - SC4S_LISTEN_JUNIPER_IDP_UDP_PORT=5004
      - SC4S_LISTEN_PALOALTO_PANOS_UDP_PORT=5005
      - SC4S_LISTEN_PFSENSE_UDP_PORT=5006
      - SC4S_ARCHIVE_GLOBAL=no
      - SC4S_LISTEN_CHECKPOINT_SPLUNK_NOISE_CONTROL=yes
```

- sc4s-version,  use latest if no version mentioned in json file
- SPLUNK_HEC_TOKEN:  HEC token of the Noah created earlier
- SPLUNK_HEC_URL: HEC url of the splunk instance 

- And execute following to spin sc4s in your local or any other machine.

```
docker-compose -f docker-compose.yml up -d sc4s
```

- Validate the sc4s is up and running via `docker ps` with the given version and connected to splunk instance by checking if sc4s startup events are available in splunk instance at `sourcetype = sc4s:events:startup:out`

- Update the sc4s-host and sc4s-port value in pytest.ini file.
port value mapped to 514/tcp can be obtained via `docker ps` command

- Install required SC4S indexes using the SPL obtained from the link by executing below command.
```
export SC4S_INDEX_URL=$( curl -s https://api.github.com/repos/splunk/splunk-configurations-base-indexes/releases/latest \ | jq -r '.assets[] | select((.name | contains("spl")) and (.name | contains("search_head") | not) and (.name | contains("indexers") | not ) and (.name | contains("forwarders") | not)) | .browser_download_url ')
echo $SC4S_INDEX_URL
```


5. Run Tests

- Knowledge

```bash
pytest -vv --splunk-type=external --splunk-app=<path-to-addon-package> --splunk-data-generator=<path to pytest-splunk-addon-data.conf file> --splunk-host=<hostname> --splunk-port=<splunk-management-port> --splunk-user=<username> --splunk-password=<password> --splunk-hec-token=<splunk_hec_token> --sc4s-host=<sc4s_host> --sc4s-port=<sc4s_port>
```

- UI

1. Set all variables in environment mentioned at [test_credentials.env](test_credentials.env) file with appropriate values encoded with base64.
2. Download Browser's specific driver
    - For Chrome: download chromedriver
    - For Firefox: download geckodriver
    - For IE: download IEdriverserver
3. Put the downloaded driver into `test/ui/` directory, make sure that it is within the environment's PATH variable, and that it is executable
4. For Internet explorer, The steps mentioned at below link must be performed [selenium](https://github.com/SeleniumHQ/selenium/wiki/InternetExplorerDriver#required-configuration)

6. Execute the test cases
 ```script
pytest -vv --browser=<browser> --local --splunk-host=<web_url> --splunk-port=<mgmt_url> --splunk-user=<username> --splunk-password=<password>
 ```

- Modinput

Install [splunk-add-on-for-modinput-test](https://github.com/splunk/splunk-add-on-for-modinput-test/releases/latest/) addon in splunk and set all variables in environment mentioned at [test_credentials.env](test_credentials.env) file with appropriate values encoded with base64 or add variables in pytest command mentioned in conftest file.

Update the pytest command with additional params if required for the addon.

```bash
pytest -vv --username=<splunk_username> --password=<splunk_password> --splunk-url=<splunk_url> --remote
```