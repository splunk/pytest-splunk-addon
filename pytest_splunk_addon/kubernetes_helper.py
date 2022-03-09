#
# Copyright 2021 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# -*- coding: utf-8 -*-
import yaml, json
import time
from kubernetes import client, config, utils
from kubernetes.client.api import core_v1_api
from kubernetes.stream import stream
import tarfile
from tempfile import TemporaryFile
import logging

LOGGER = logging.getLogger("pytest-splunk-addon")


class KubernetesHelper:
    def __init__(self) -> None:
        """
        Check for KUBECONFIG provided in env variable,
        which will be used for kubernetes setup.
        """
        try:
            config.load_kube_config()
        except Exception as e:
            LOGGER.error("KUBECONFIG file not found")
        pass

    def create_namespace(self, file, namespace_name):
        """
        Create namespace
        file = Path of namespace.yaml file,
        namespace_name = Name of the namespace.
        """
        try:
            k8s_client = client.ApiClient()
            resp = utils.create_from_yaml(k8s_client, file)
            SLEEP_TIME = 3
            namespace_created = False
            wait_count = 1
            while wait_count <= 5:
                timer = SLEEP_TIME * wait_count
                initial_timer = 0
                while initial_timer < timer:
                    status = self.namespace_status(namespace_name)
                    if str(status) == "Active":
                        LOGGER.info("namespace created....")
                        namespace_created = True
                        break
                    else:
                        LOGGER.info("waiting for namespace to get created...")
                        time.sleep(1)
                        initial_timer += 1
                        continue
                if namespace_created == True:
                    break
                wait_count += 1
            if (wait_count > 5) and (namespace_created == False):
                LOGGER.error("Namespace creation took more than expected")
        except Exception as e:
            LOGGER.error("Exception occurred while creating namespace : {0}".format(e))

    def create_k8s_resource_from_yaml(self, file, namespace_name):
        """
        Create kubernetes resource from yaml file (Deployment, Service, Pod)
        file = Path of yaml file,
        namespace_name = Name of the namespace
        """
        try:
            k8s_client = client.ApiClient()
            resp = utils.create_from_yaml(k8s_client, file, namespace=namespace_name)
        except Exception as e:
            LOGGER.error(
                "Exception occurred while creating resource from {0} : {1}".format(
                    file, e
                )
            )

    def create_splunk_standalone(self, file, namespace_name):
        """
        Create Splunk Standalone
        file = Path of splunk_standalone.yaml,
        namespace_name = Name of the namespace
        """
        with open(file, "r") as f:
            lines = f.readlines()
        with open(file, "w") as f:
            for line in lines:
                if line.startswith("#"):
                    line.strip()
                else:
                    f.write(line)
        with open(file, "r") as yaml_in:
            yaml_object = yaml.safe_load(
                yaml_in
            )  # yaml_object will be a list or a dict
            body = json.loads(json.dumps(yaml_object))
        try:
            k8s_api = client.CustomObjectsApi()
            group = "enterprise.splunk.com"
            version = "v1"
            namespace = namespace_name
            plural = "standalones"
            LOGGER.info("Creating Splunk Standalone")
            api_response = k8s_api.create_namespaced_custom_object(
                group, version, namespace, plural, body
            )
            time.sleep(2)
        except:
            LOGGER.error("Exception occurred while creating splunk-deployment")
            LOGGER.error("Ensure splunk-operator is setup at cluster scoped level")

    def wait_for_pod_to_get_ready(self, pod_name, namespace_name):
        """
        Wait for pod to get ready,
        pod_name = Name of the pod,
        namespace_name = Name of the namespace
        """
        try:
            wait_count = 0
            SLEEP_TIME = 30
            pod_created = False
            while wait_count <= 5:
                timer = SLEEP_TIME * wait_count
                initial_timer = 0
                while initial_timer < timer:
                    LOGGER.info("wait_count is {0}".format(str(wait_count)))
                    api_instance = client.CoreV1Api()
                    api_response = api_instance.read_namespaced_pod_status(
                        name=pod_name, namespace=namespace_name
                    )
                    print(api_response.status.phase)
                    if api_response.status.phase != "Pending":
                        try:
                            api_response_log = api_instance.read_namespaced_pod_log(
                                name=pod_name, namespace=namespace_name
                            )
                            with open(
                                "{0}.log".format(pod_name), "w"
                            ) as splunk_standalone:
                                splunk_standalone.write(api_response_log)
                        except Exception as e:
                            LOGGER.error(
                                "Found exception in writing the logs for pod : {0}".format(
                                    pod_name
                                )
                            )
                        # readiness probe
                        if api_response.status.container_statuses[0].ready == True:
                            LOGGER.info("Pod {0} created....".format(pod_name))
                            pod_created = True
                            break
                        else:
                            LOGGER.info(
                                "waiting for pod {0} to get created...".format(pod_name)
                            )
                            initial_timer += 1
                            time.sleep(1)
                            continue
                    else:
                        LOGGER.error(
                            "Pod {0} is still in Pending state.".format(pod_name)
                        )
                        initial_timer += 1
                        time.sleep(1)
                        continue
                if pod_created == True:
                    break
                wait_count += 1
            if (wait_count > 5) and (pod_created == False):
                LOGGER.error(
                    "Waiting for pod {0} creation took more than expected, please check for logs".format(
                        pod_name
                    )
                )
        except Exception as e:
            LOGGER.error(
                "Found exception while waiting for pod {0} : {1}".format(pod_name, e)
            )

    def wait_for_deployment_to_get_available(self, deployment_name, namespace_name):
        """
        Wait for deployment to get available
        deployment_name = Name of the deployment,
        namespace_name = Name of the namespace
        """
        try:
            wait_count = 0
            SLEEP_TIME = 30
            deployment_created = False
            while wait_count <= 5:
                timer = SLEEP_TIME * wait_count
                initial_timer = 0
                while initial_timer < timer:
                    k8s_api = client.AppsV1Api()
                    api_response = k8s_api.read_namespaced_deployment_status(
                        deployment_name, namespace_name
                    )
                    if api_response.status.replicas != None:
                        LOGGER.info(
                            "Deployment {0} is available".format(deployment_name)
                        )
                        deployment_created = True
                        break
                    else:
                        LOGGER.error(
                            "Deployment {0} is still not available".format(
                                deployment_name
                            )
                        )
                        initial_timer += 1
                        time.sleep(1)
                        continue
                if deployment_created == True:
                    break
                wait_count += 1
            if (wait_count > 5) and (deployment_created == False):
                LOGGER.error(
                    "Waiting for deployment {0} to get available took more than expected".format(
                        deployment_name
                    )
                )
        except Exception as e:
            LOGGER.error(
                "Found exception while waiting for deployment {0} : {1}".format(
                    deployment_name, e
                )
            )

    def wait_for_statefulset_to_get_available(self, statefulset_name, namespace_name):
        """
        Wait for statefulset (Splunk Standalone) to get available
        statefulset_name = Name of the stateful set,
        namespace_name = Name of the namespace.
        """
        try:
            wait_count = 1
            SLEEP_TIME = 30
            statefulset_created = False
            while wait_count <= 5:
                timer = SLEEP_TIME * wait_count
                initial_timer = 0
                while initial_timer < timer:
                    k8s_api = client.AppsV1Api()
                    api_response = k8s_api.read_namespaced_stateful_set_status(
                        statefulset_name, namespace_name
                    )
                    if api_response.status.replicas != 0:
                        LOGGER.info(
                            "Statefulset {0} is available".format(statefulset_name)
                        )
                        statefulset_created = True
                        break
                    else:
                        LOGGER.error(
                            "Statefulset {0} is still not available".format(
                                statefulset_name
                            )
                        )
                        initial_timer += 1
                        time.sleep(1)
                        continue
                if statefulset_created == True:
                    break
                wait_count += 1
            if (wait_count > 5) and (statefulset_created == False):
                LOGGER.error(
                    "Waiting for statefulset {0} to get available took more than expected".format(
                        statefulset_name
                    )
                )
        except:
            LOGGER.error("Exception occurred while fetching statefulset status")

    def get_pod_name(self, namespace_name, label):
        """
        Get the pod name,
        namespace_name = Name of the namespace,
        label = Label of the pod

        returns name of the matching pod
        """
        try:
            api_instance = client.CoreV1Api()
            api_response = api_instance.list_namespaced_pod(
                namespace=namespace_name, label_selector="{}".format(label)
            )
            return str(api_response.items[0].metadata.name)
        except Exception as e:
            LOGGER.error(
                "Found exception while waiting for pod with label {0} : {1}".format(
                    label, e
                )
            )
            return None

    def copy_files_to_pod(
        self, pod_name, namespace_name, destination_location, source_location
    ):
        """
        Copy files to Pod
        pod_name = Name of the pod,
        namespace_name = Name of the namespace,
        destination_location = Location of the pod where files will be stored,
        source_location = Location of the source from where files will be copied.
        """
        try:
            LOGGER.info("Copy files to pod")
            api_instance = client.CoreV1Api()

            exec_command = ["tar", "xvf", "-", "-C", str(destination_location)]
            resp = stream(
                api_instance.connect_get_namespaced_pod_exec,
                pod_name,
                namespace_name,
                command=exec_command,
                stderr=True,
                stdin=True,
                stdout=True,
                tty=False,
                _preload_content=False,
            )

            with TemporaryFile() as tar_buffer:
                with tarfile.open(fileobj=tar_buffer, mode="w") as tar:
                    tar.add(source_location)
                tar_buffer.seek(0)
                commands = []
                commands.append(tar_buffer.read())
                while resp.is_open():
                    resp.update(timeout=1)
                    if resp.peek_stdout():
                        print("STDOUT: %s" % resp.read_stdout())
                    if resp.peek_stderr():
                        print("STDERR: %s" % resp.read_stderr())
                    if commands:
                        c = commands.pop(0)
                        resp.write_stdin(c)
                    else:
                        break
                resp.close()
        except Exception as e:
            LOGGER.error("Exception occurred while copying files : {0}".format(e))

    def get_splunk_creds(self, secret_name, namespace_name):
        """
        Get splunk secrets (HEC token, Password)
        secret_name = Name of the secret,
        namespace_name = Name of the namespace.

        Returns HEC_TOKEN and Password.
        """
        try:
            LOGGER.info("Get splunk secrets")
            core_v1 = core_v1_api.CoreV1Api()
            api_response = core_v1.read_namespaced_secret(
                name=secret_name, namespace=namespace_name
            )
            hec_token = api_response.data["hec_token"]
            password = api_response.data["password"]
            return hec_token, password
        except Exception as e:
            LOGGER.error(
                "Exception occurred while fetching splunk creds : {0}".format(e)
            )
            return None, None

    def delete_splunk_standalone(self, namespace_name):
        """
        Delete splunk standalone
        namespace_name = Name of the namespace
        """
        try:
            k8s_api = client.CustomObjectsApi()
            group = "enterprise.splunk.com"
            version = "v1"
            namespace = namespace_name
            plural = "standalones"
            api_response = k8s_api.delete_namespaced_custom_object(
                group, version, namespace, plural, name="s1"
            )

            SLEEP_TIME = 3
            standalone_deleted = False
            wait_count = 1
            while wait_count <= 5:
                timer = SLEEP_TIME * wait_count
                initial_timer = 0
                while initial_timer < timer:
                    pod_name = self.get_pod_name(
                        namespace_name,
                        "statefulset.kubernetes.io/pod-name=splunk-s1-standalone-0",
                    )
                    if pod_name == None:
                        standalone_deleted = True
                        LOGGER.info("Splunk deleted....")
                        break
                    LOGGER.info("Standalone in deletion...")
                    initial_timer += 1
                    time.sleep(1)
                wait_count += 1
                if standalone_deleted == True:
                    LOGGER.info("Splunk Standalone deleted successfully")
                    break
            if (wait_count > 5) and (standalone_deleted == False):
                LOGGER.error("Splunk standalone deletion took more than expected")
        except Exception as e:
            LOGGER.error(
                "Found exception while deleting Splunk Standalone : {0}".format(e)
            )

    def delete_kubernetes_deployment(self, deployment_name, namespace_name, pod_label):
        """
        Delete Kubernetes Deployments (SC4S and UF)
        deployment_name = Name of the deployment,
        namespace_name = Name of the namespace,
        pod_label = Label of the pod.
        """
        try:
            k8s_api = client.AppsV1Api()
            name = deployment_name
            namespace = namespace_name
            label = pod_label
            api_response = k8s_api.delete_namespaced_deployment(name, namespace)
            SLEEP_TIME = 3
            deployment_deleted = False
            wait_count = 1
            while wait_count <= 5:
                timer = SLEEP_TIME * wait_count
                initial_timer = 0
                while initial_timer < timer:
                    pod_name = self.get_pod_name(namespace_name, label)
                    if pod_name == None:
                        LOGGER.info("Deployment {0} deleted....".format(name))
                        deployment_deleted = True
                        break
                    LOGGER.info("Deployment {0} in deletion...".format(name))
                    initial_timer += 1
                    time.sleep(1)
                wait_count += 1
                if deployment_deleted == True:
                    LOGGER.info("Deployment {0} deleted successfully".format(name))
                    break
            if (wait_count > 5) and (deployment_deleted == False):
                LOGGER.error(
                    "Deployment {0} deletion took more than expected".format(name)
                )
        except Exception as e:
            LOGGER.error(
                "Found exception while deleting deployment {0} : {1}".format(
                    deployment_name, e
                )
            )

    def namespace_status(self, namespace_name):
        """
        Namespace status
        namespace_name = Name of the namespace

        return status = Status of the namespace
        """
        try:
            core_v1 = core_v1_api.CoreV1Api()
            api_response = core_v1.read_namespace_status(name=namespace_name)
            status = api_response.status.phase
            return status
        except Exception:
            LOGGER.error(
                "Found exception while finding namespace status for {0}".format(
                    namespace_name
                )
            )
            return None

    def delete_namespace(self, namespace_name):
        """
        Delete namespace
        namespace_name = Name of the namespace.
        """
        try:
            core_v1 = core_v1_api.CoreV1Api()
            api_response = core_v1.delete_namespace(name=namespace_name)
            core_v1_status = core_v1_api.CoreV1Api()
            api_response_status = core_v1_status.read_namespace_status(
                name=namespace_name
            )
            if str(api_response_status.status.phase) == "Terminating":
                LOGGER.info("Deleting Namespace : {0}".format(namespace_name))
            SLEEP_TIME = 3
            namespace_deleted = False
            wait_count = 1
            while wait_count <= 5:
                timer = SLEEP_TIME * wait_count
                initial_timer = 0
                while initial_timer < timer:
                    status = self.namespace_status(namespace_name)
                    if status == None:
                        LOGGER.info("Namespace {0} deleted".format(namespace_name))
                        namespace_deleted = True
                        break
                    LOGGER.info("Namespace in deletion...".format(namespace_name))
                    initial_timer += 1
                    time.sleep(1)
                wait_count += 1
                if namespace_deleted == True:
                    LOGGER.info(
                        "Namespace {0} deleted successfully".format(namespace_name)
                    )
                    break
            if (wait_count > 5) and (namespace_deleted == False):
                LOGGER.error(
                    "Namespace {0} deletion took more than expected".format(
                        namespace_name
                    )
                )
        except Exception as e:
            LOGGER.error("Exception occurred while deleting namespace : {0}".format(e))
