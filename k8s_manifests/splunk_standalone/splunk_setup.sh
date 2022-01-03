#!/bin/sh
kubectl create ns $namespace_name
kubectl run nginx -n $namespace_name --image=nginx --port=80 --expose
# while [[ $(kubectl get pod nginx -n $namespace_name -o 'jsonpath={..status.conditions[?(@.type=="Ready")].status}') != "True" ]]; do echo "waiting for nginx pod" && sleep 1; done
# until kubectl get pod nginx -n $namespace_name 2>&1 >/dev/null; do sleep 3; done
kubectl wait pod nginx --for=condition=ready --timeout=300s -n $namespace_name
find ./tests/src -iname "*.tgz" -exec kubectl cp {} nginx:/usr/share/nginx/html -n $namespace_name \;
kubectl create secret generic splunk-$namespace_name-secret --from-literal='password=Chang3d!' --from-literal='hec_token=9b741d03-43e9-4164-908b-e09102327d22' -n $namespace_name
kubectl apply -f ./k8s_manifests/splunk_standalone/splunk-operator-install_updated.yaml -n $namespace_name
# while [[ $(kubectl get deploy splunk-operator -n $namespace_name -o 'jsonpath={..status.conditions[?(@.type=="Ready")].status}') != "True" ]]; do echo "waiting for splunk-operator deployment" && sleep 1; done
# until kubectl get deploy splunk-operator -n $namespace_name 2>&1 >/dev/null; do sleep 3; done
kubectl wait deployment splunk-operator -n $namespace_name --for=condition=available --timeout=240s
kubectl apply -f ./k8s_manifests/splunk_standalone/splunk_standalone_updated.yaml -n $namespace_name
sleep 30
kubectl wait pod splunk-s1-standalone-0 --for=condition=ready --timeout=900s -n $namespace_name
# while [[ $(kubectl get pod splunk-s1-standalone-0 -n $namespace_name -o 'jsonpath={..status.conditions[?(@.type=="Ready")].status}') != "True" ]]; do echo "waiting for splunk standalone" && sleep 1; done
kubectl port-forward svc/splunk-s1-standalone-service -n $namespace_name :8000 :8088 :8089 > ./exposed_splunk_ports.log 2>&1 &
sleep 30
echo "splunk up"