#!/bin/sh
kubectl apply -f "$(dirname -- "$0")"/sc4s_deployment_updated.yaml -n $NAMESPACE_NAME
kubectl wait deployment -n $NAMESPACE_NAME --for=condition=available --timeout=900s -l='app=sc4s'
# while [[ $(kubectl get pod -n $NAMESPACE_NAME -l='app=sc4s' -o 'jsonpath={..status.conditions[?(@.type=="Ready")].status}') != "True" ]]; do echo "waiting for sc4s pod" && sleep 1; done
kubectl wait pod -n $NAMESPACE_NAME --for=condition=ready --timeout=900s -l='app=sc4s'
kubectl apply -f "$(dirname -- "$0")"/sc4s_service.yaml -n $NAMESPACE_NAME
sleep 30
kubectl port-forward svc/sc4s-service -n $NAMESPACE_NAME :514 > $TEST_RUNNER_DIRECTORY/exposed_sc4s_ports.log 2>&1 &
sleep 30
echo "sc4s up"