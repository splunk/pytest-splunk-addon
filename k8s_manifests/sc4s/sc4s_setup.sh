#!/bin/sh
kubectl apply -f ./k8s_manifests/sc4s/sc4s_deployment_updated.yaml -n $namespace_name
kubectl wait deployment -n $namespace_name --for=condition=available --timeout=900s -l='app=sc4s'
# while [[ $(kubectl get pod -n $namespace_name -l='app=sc4s' -o 'jsonpath={..status.conditions[?(@.type=="Ready")].status}') != "True" ]]; do echo "waiting for sc4s pod" && sleep 1; done
kubectl wait pod -n $namespace_name --for=condition=ready --timeout=900s -l='app=sc4s'
kubectl apply -f ./k8s_manifests/sc4s/sc4s_service.yaml -n $namespace_name
sleep 30
kubectl port-forward svc/sc4s-service -n $namespace_name :514 > ./exposed_sc4s_ports.log 2>&1 &
sleep 30
echo "sc4s up"