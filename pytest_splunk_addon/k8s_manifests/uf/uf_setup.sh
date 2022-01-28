#!/bin/sh
kubectl apply -f "$(dirname -- "$0")"/uf_deployment_updated.yaml -n $NAMESPACE_NAME
kubectl wait deployment -n $NAMESPACE_NAME --for=condition=available --timeout=900s -l='app=uf'
kubectl wait pod -n $NAMESPACE_NAME --for=condition=ready --timeout=900s -l='app=uf'
kubectl apply -f "$(dirname -- "$0")"/uf_service.yaml -n $NAMESPACE_NAME
sleep 15
kubectl port-forward svc/uf-service -n $NAMESPACE_NAME :8089 > $TEST_RUNNER_DIRECTORY/exposed_uf_ports.log 2>&1 &
sleep 15
echo "UF up"