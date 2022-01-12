#!/bin/sh
kubectl delete -f ./k8s_manifests/sc4s/sc4s_deployment_updated.yaml -n $NAMESPACE_NAME
sleep 30
kubectl delete -f ./k8s_manifests/sc4s/sc4s_service.yaml -n $NAMESPACE_NAME