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
            _ = utils.create_from_yaml(k8s_client, file)
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
                if namespace_created is True:
                    break
                wait_count += 1
            if wait_count > 5 and namespace_created is False:
                LOGGER.error("Namespace creation took more than expected")
        except Exception as e:
            LOGGER.error(f"Exception occurred while creating namespace : {e}")

    def create_k8s_resource_from_yaml(self, file, namespace_name):
        """
        Create kubernetes resource from yaml file (Deployment, Service, Pod)
        file = Path of yaml file,
        namespace_name = Name of the namespace
        """
        try:
            k8s_client = client.ApiClient()
            _ = utils.create_from_yaml(k8s_client, file, namespace=namespace_name)
        except Exception as e:
            LOGGER.error(
                f"Exception occurred while creating resource from {file} : {e}"
            )

    def create_splunk_standalone(self, file, namespace_name):
        """
        Create Splunk Standalone
        file = Path of splunk_standalone_updated.yaml,
        namespace_name = Name of the namespace
        """
        with open(file) as yaml_in:
            body = yaml.safe_load(yaml_in)  # yaml_object will be a list or a dict
        try:
            k8s_api = client.CustomObjectsApi()
            group = "enterprise.splunk.com"
            version = "v1"
            namespace = namespace_name
            plural = "standalones"
            LOGGER.info("Creating Splunk Standalone")
            _ = k8s_api.create_namespaced_custom_object(
                group, version, namespace, plural, body
            )
            time.sleep(2)
        except Exception as e:
            LOGGER.error(
                f"Exception occurred while creating splunk-deployment, ensure splunk-operator is setup at cluster scoped : {e}"
            )

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
                    api_instance = client.CoreV1Api()
                    api_response = api_instance.read_namespaced_pod_status(
                        name=pod_name, namespace=namespace_name
                    )
                    if api_response.status.phase != "Pending":
                        try:
                            api_response_log = api_instance.read_namespaced_pod_log(
                                name=pod_name, namespace=namespace_name
                            )
                            with open(f"{pod_name}.log", "w") as splunk_standalone:
                                splunk_standalone.write(api_response_log)
                        except Exception as e:
                            LOGGER.error(
                                f"Found exception in writing the logs for pod : {pod_name}"
                            )
                        # readiness probe
                        if api_response.status.container_statuses[0].ready is True:
                            LOGGER.info(f"Pod {pod_name} created....")
                            pod_created = True
                            break
                        else:
                            LOGGER.info(f"waiting for pod {pod_name} to get created...")
                            initial_timer += 1
                            time.sleep(1)
                            continue
                    else:
                        LOGGER.warning(f"Pod {pod_name} is still in Pending state.")
                        initial_timer += 1
                        time.sleep(1)
                        continue
                if pod_created is True:
                    break
                wait_count += 1
            if wait_count > 5 and pod_created is False:
                LOGGER.error(
                    f"Waiting for pod {pod_name} creation took more than expected, please check for logs"
                )
        except Exception as e:
            LOGGER.error(f"Found exception while waiting for pod {pod_name} : {e}")

    def wait_for_kubernetes_resource_to_get_available(
        self, resource_name, namespace_name
    ):
        """
        Wait for deployment or statefulset to get available
        resource_name = Name of the deployment or statefulset,
        namespace_name = Name of the namespace
        """
        try:
            wait_count = 0
            SLEEP_TIME = 30
            resource_created = False
            while wait_count <= 5:
                timer = SLEEP_TIME * wait_count
                initial_timer = 0
                while initial_timer < timer:
                    k8s_api = client.AppsV1Api()
                    if resource_name == "splunk-s1-standalone":
                        api_response = k8s_api.read_namespaced_stateful_set_status(
                            resource_name, namespace_name
                        )
                    else:
                        api_response = k8s_api.read_namespaced_deployment_status(
                            resource_name, namespace_name
                        )
                    if api_response.status.replicas:
                        LOGGER.info(f"Resource {resource_name} is available")
                        resource_created = True
                        break
                    else:
                        LOGGER.warning(
                            f"Resource {resource_name} is still not available"
                        )
                        initial_timer += 1
                        time.sleep(1)
                        continue
                if resource_created is True:
                    break
                wait_count += 1
            if wait_count > 5 and resource_created is False:
                LOGGER.error(
                    f"Waiting for resource {resource_name} to get available took more than expected"
                )
        except Exception as e:
            LOGGER.error(
                f"Found exception while waiting for resource {resource_name} : {e}"
            )

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
                namespace=namespace_name, label_selector=f"{label}"
            )
            return str(api_response.items[0].metadata.name)
        except Exception as e:
            LOGGER.error(
                f"Found exception while waiting for pod with label {label} : {e}"
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
                        LOGGER.warning(f"STDOUT: {resp.read_stdout()}")
                    if resp.peek_stderr():
                        LOGGER.warning(f"STDERR: {resp.read_stderr()}")
                    if commands:
                        c = commands.pop(0)
                        resp.write_stdin(c)
                    else:
                        break
                resp.close()
        except Exception as e:
            LOGGER.error(f"Exception occurred while copying files : {e}")

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
            LOGGER.error(f"Exception occurred while fetching splunk creds : {e}")
            return None, None

    def delete_kubernetes_resource(self, resource_name, namespace_name, pod_label):
        """
        Delete Kubernetes Deployments or Statefulset (SC4S, UF and Standalone )
        resource_name = Name of the resource,
        namespace_name = Name of the namespace,
        pod_label = Label of the pod.
        """
        try:
            if resource_name == "Standalone":
                k8s_api = client.CustomObjectsApi()
                group = "enterprise.splunk.com"
                version = "v1"
                namespace = namespace_name
                plural = "standalones"
                name = resource_name
                _ = k8s_api.delete_namespaced_custom_object(
                    group, version, namespace, plural, name="s1"
                )
            else:
                k8s_api = client.AppsV1Api()
                name = resource_name
                namespace = namespace_name
                _ = k8s_api.delete_namespaced_deployment(name, namespace)
            label = pod_label
            SLEEP_TIME = 3
            resource_deleted = False
            wait_count = 1
            while wait_count <= 5:
                timer = SLEEP_TIME * wait_count
                initial_timer = 0
                while initial_timer < timer:
                    pod_name = self.get_pod_name(namespace_name, label)
                    if pod_name == None:
                        LOGGER.info(f"Kubernetes resource {name} deleted....")
                        resource_deleted = True
                        break
                    LOGGER.info(f"Kubernetes resource {name} in deletion...")
                    initial_timer += 1
                    time.sleep(1)
                wait_count += 1
                if resource_deleted is True:
                    LOGGER.info(f"Kubernetes resource {name} deleted successfully")
                    break
            if wait_count > 5 and resource_deleted is False:
                LOGGER.error(
                    f"Kubernetes resource {name} deletion took more than expected"
                )
        except Exception as e:
            LOGGER.error(
                f"Found exception while deleting kubernetes resource {resource_deleted} : {e}"
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
                f"Found exception while finding namespace status for {namespace_name}"
            )
            return None

    def delete_namespace(self, namespace_name):
        """
        Delete namespace
        namespace_name = Name of the namespace.
        """
        try:
            core_v1 = core_v1_api.CoreV1Api()
            _ = core_v1.delete_namespace(name=namespace_name)
            core_v1_status = core_v1_api.CoreV1Api()
            api_response_status = core_v1_status.read_namespace_status(
                name=namespace_name
            )
            if str(api_response_status.status.phase) == "Terminating":
                LOGGER.info(f"Deleting Namespace : {namespace_name}")
            SLEEP_TIME = 3
            namespace_deleted = False
            wait_count = 1
            while wait_count <= 5:
                timer = SLEEP_TIME * wait_count
                initial_timer = 0
                while initial_timer < timer:
                    status = self.namespace_status(namespace_name)
                    if status == None:
                        LOGGER.info(f"Namespace {namespace_name} deleted")
                        namespace_deleted = True
                        break
                    LOGGER.info(f"Namespace {namespace_name} in deletion")
                    initial_timer += 1
                    time.sleep(1)
                wait_count += 1
                if namespace_deleted is True:
                    LOGGER.info(f"Namespace {namespace_name} deleted successfully")
                    break
            if wait_count > 5 and namespace_deleted is False:
                LOGGER.error(
                    f"Namespace {namespace_name} deletion took more than expected"
                )
        except Exception as e:
            LOGGER.error(f"Exception occurred while deleting namespace : {e}")
