#!/bin/sh
kubectl delete -f ./k8s_manifests/splunk_standalone/splunk_standalone_updated.yaml -n $NAMESPACE_NAME
sleep 30
kubectl delete standalone s1 -n $NAMESPACE_NAME
kubectl delete svc nginx -n $NAMESPACE_NAME
kubectl delete pod nginx -n $NAMESPACE_NAME
sleep 15
kubectl delete secret splunk-$NAMESPACE_NAME-secret -n $NAMESPACE_NAME
sleep 60
kubectl delete -f ./k8s_manifests/splunk_standalone/namespace_updated.yaml
sleep 60