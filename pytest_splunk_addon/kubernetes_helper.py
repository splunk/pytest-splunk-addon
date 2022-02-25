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
from os import path
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
            print(file)
            LOGGER.info("file in create_namespace: {0}".format(file))
            if path.exists(file):
                print("File exists....{0}".format(file))
            resp = utils.create_from_yaml(k8s_client, file)
            while True:
                core_v1 = core_v1_api.CoreV1Api()
                api_response = core_v1.read_namespace_status(name=namespace_name)
                if str(api_response.status.phase) == "Active":
                    LOGGER.info("namespace created....")
                    break
                else:
                    LOGGER.info("waiting for namespace to get created...")
                    continue
        except Exception as e:
            LOGGER.error("Exception occured while creating namespace : {0}".format(e))

    def create_k8s_resource_from_yaml(self, file, namespace_name):
        """
        Create kubernetes resource from yaml file (Deployment, Service, Pod)
        file = Path of yaml file,
        namespace_name = Name of the namespace
        """
        try:
            k8s_client = client.ApiClient()
            resp = utils.create_from_yaml(k8s_client, file, namespace=namespace_name)
            time.sleep(1)
        except Exception as e:
            LOGGER.error(
                "Exception occured while creating resource from {0} : {1}".format(
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
            LOGGER.error("Exception occured while creating splunk-deployment")

    def wait_for_pod_to_get_ready(self, pod_name, namespace_name):
        """
        Wait for pod to get ready,
        pod_name = Name of the pod,
        namespace_name = Name of the namespace
        """
        try:
            wait_count = 0
            while wait_count <= 5:
                LOGGER.info("wait_count is {0}".format(str(wait_count)))
                api_instance = client.CoreV1Api()
                api_response = api_instance.read_namespaced_pod_status(
                    name=pod_name, namespace=namespace_name
                )
                print(api_response.status.phase)
                if api_response.status.phase != "Pending":
                    if str(api_response.status.container_statuses[0].ready) == "True":
                        LOGGER.info("Pod {0} created....".format(pod_name))
                        break
                    else:
                        LOGGER.info(
                            "waiting for pod {0} to get created...".format(pod_name)
                        )
                        try:
                            api_response = api_instance.read_namespaced_pod_log(
                                name=pod_name, namespace=namespace_name
                            )
                            with open(
                                "{0}.log".format(pod_name), "w"
                            ) as splunk_standalone:
                                splunk_standalone.write(api_response)
                        except Exception as e:
                            LOGGER.error(
                                "Found exception in writing the logs for pod : {0}".format(
                                    pod_name
                                )
                            )
                        time.sleep(30)
                        wait_count += 1
                        continue
                else:
                    LOGGER.error("Pod {0} is still in Pending state.".format(pod_name))
                    time.sleep(30)
                    wait_count += 1
                    continue
            if wait_count > 5:
                LOGGER.error(
                    "Waiting for pod {0} creation took more than expected, please check for logs".format(
                        pod_name
                    )
                )
        except Exception as e:
            LOGGER.error(
                "Found exception while waiting for pod {0} : {1}".format(pod_name, e)
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
                namespace=namespace_name, label_selector="{}".format(label)
            )
            return str(api_response.items[0].metadata.name)
        except Exception as e:
            LOGGER.error(
                "Found exception while waiting for pod {0} : {1}".format(
                    namespace_name, e
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
            LOGGER.error("Exception occured while copying files : {0}".format(e))

    def get_splunk_creds(self, secret_name, namespace_name):
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
                "Exception occured while fetching splunk creds : {0}".format(e)
            )
            return None, None

    def delete_splunk_standalone(self, namespace_name):
        try:
            k8s_api = client.CustomObjectsApi()
            group = "enterprise.splunk.com"
            version = "v1"
            namespace = namespace_name
            plural = "standalones"
            api_response = k8s_api.delete_namespaced_custom_object(
                group, version, namespace, plural, name="s1"
            )

            while True:
                pod_name = self.get_pod_name(
                    namespace_name,
                    "statefulset.kubernetes.io/pod-name=splunk-s1-standalone-0",
                )
                if pod_name == None:
                    LOGGER.info("Splunk deleted....")
                    return False
        except Exception as e:
            LOGGER.error(
                "Found exception while deleting Splunk Standalone : {0}".format(e)
            )

    def delete_kubernetes_deployment(self, deployment_name, namespace_name, pod_label):
        try:
            k8s_api = client.AppsV1Api()
            name = deployment_name
            namespace = namespace_name
            label = pod_label
            api_response = k8s_api.delete_namespaced_deployment(name, namespace)

            while True:
                pod_name = self.get_pod_name(namespace_name, label)
                if pod_name == None:
                    LOGGER.info("Deployment {0} deleted....".format(name))
                    return False
        except Exception as e:
            LOGGER.error(
                "Found exception while deleting Splunk Standalone : {0}".format(e)
            )

    def delete_namespace(self, namespace_name):
        """
        Delete namespace
        namespace_name = Name of the namespace.
        """
        try:
            while True:
                core_v1 = core_v1_api.CoreV1Api()
                api_response = core_v1.delete_namespace(name=namespace_name)
                core_v1_status = core_v1_api.CoreV1Api()
                api_response_status = core_v1_status.read_namespace_status(
                    name=namespace_name
                )
                if str(api_response_status.status.phase) == "Terminating":
                    LOGGER.error("Deleting Namespace : {0}".format(namespace_name))
                    time.sleep(10)
                    break
        except Exception as e:
            LOGGER.error("Exception occured while deleting namespace : {0}".format(e))
