#!/bin/sh
kubectl delete -f "$(dirname -- "$0")"/sc4s_deployment_updated.yaml -n $NAMESPACE_NAME
sleep 15
kubectl delete -f "$(dirname -- "$0")"/sc4s_service.yaml -n $NAMESPACE_NAME