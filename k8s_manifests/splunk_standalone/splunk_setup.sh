#!/bin/sh
kubectl apply -f ./k8s_manifests/splunk_standalone/namespace_updated.yaml
kubectl run nginx -n $NAMESPACE_NAME --image=nginx --port=80 --expose
# while [[ $(kubectl get pod nginx -n $NAMESPACE_NAME -o 'jsonpath={..status.conditions[?(@.type=="Ready")].status}') != "True" ]]; do echo "waiting for nginx pod" && sleep 1; done
# until kubectl get pod nginx -n $NAMESPACE_NAME 2>&1 >/dev/null; do sleep 3; done
kubectl wait pod nginx --for=condition=ready --timeout=300s -n $NAMESPACE_NAME
find ./tests/src -iname "*.spl" -exec kubectl cp {} nginx:/usr/share/nginx/html -n $NAMESPACE_NAME \;
cat ./k8s_manifests/splunk_standalone/addon_information.yaml >> ./k8s_manifests/splunk_standalone/addon_information_updated.yaml
export SC4S_INDEX_URL=$( curl -s https://api.github.com/repos/splunk/splunk-configurations-base-indexes/releases/latest \ | jq -r '.assets[] | select((.name | contains("spl")) and (.name | contains("search_head") | not) and (.name | contains("indexers") | not ) and (.name | contains("forwarders") | not)) | .browser_download_url ')
echo $SC4S_INDEX_URL | sed "s|^|        - https://api.github.com/repos/splunk/splunk-configurations-base-indexes/|" >> ./k8s_manifests/splunk_standalone/addon_information_updated.yaml
find ./tests/src -iname "*.spl" | sed 's/.\/tests\/src\//        - http:\/\/nginx\//g' >> ./k8s_manifests/splunk_standalone/addon_information_updated.yaml
cat ./k8s_manifests/splunk_standalone/addon_information_updated.yaml >> ./k8s_manifests/splunk_standalone/splunk_standalone_updated.yaml
kubectl create secret generic splunk-$NAMESPACE_NAME-secret --from-literal='password=Chang3d!' --from-literal='hec_token=9b741d03-43e9-4164-908b-e09102327d22' -n $NAMESPACE_NAME
# while [[ $(kubectl get deploy splunk-operator -n $NAMESPACE_NAME -o 'jsonpath={..status.conditions[?(@.type=="Ready")].status}') != "True" ]]; do echo "waiting for splunk-operator deployment" && sleep 1; done
# until kubectl get deploy splunk-operator -n $NAMESPACE_NAME 2>&1 >/dev/null; do sleep 3; done
kubectl apply -f ./k8s_manifests/splunk_standalone/splunk_standalone_updated.yaml -n $NAMESPACE_NAME
sleep 30
kubectl wait pod splunk-s1-standalone-0 --for=condition=ready --timeout=900s -n $NAMESPACE_NAME
# while [[ $(kubectl get pod splunk-s1-standalone-0 -n $NAMESPACE_NAME -o 'jsonpath={..status.conditions[?(@.type=="Ready")].status}') != "True" ]]; do echo "waiting for splunk standalone" && sleep 1; done
kubectl port-forward svc/splunk-s1-standalone-service -n $NAMESPACE_NAME :8000 :8088 :8089 > ./exposed_splunk_ports.log 2>&1 &
sleep 30
echo "splunk up"