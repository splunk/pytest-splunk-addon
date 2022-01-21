#!/bin/sh
kubectl apply -f "$(dirname -- "$0")"/uf_deployment_updated.yaml -n $NAMESPACE_NAME
kubectl wait deployment -n $NAMESPACE_NAME --for=condition=available --timeout=900s -l='app=uf'
# while [[ $(kubectl get pod -n $namespace_name -l='app=sc4s' -o 'jsonpath={..status.conditions[?(@.type=="Ready")].status}') != "True" ]]; do echo "waiting for sc4s pod" && sleep 1; done
kubectl wait pod -n $NAMESPACE_NAME --for=condition=ready --timeout=900s -l='app=uf'
kubectl apply -f "$(dirname -- "$0")"/uf_service.yaml -n $NAMESPACE_NAME
sleep 30
kubectl port-forward svc/uf-service -n $NAMESPACE_NAME :8089 > $TEST_RUNNER_DIRECTORY/exposed_uf_ports.log 2>&1 &
sleep 30
echo "UF up"