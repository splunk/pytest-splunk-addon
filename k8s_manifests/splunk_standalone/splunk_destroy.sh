#!/bin/sh
kubectl delete -f ./k8s_manifests/splunk_standalone/splunk_standalone_updated.yaml -n $namespace_name
sleep 30
kubectl delete standalone s1 -n $namespace_name
kubectl delete svc nginx -n $namespace_name
kubectl delete pod nginx -n $namespace_name
sleep 15
kubectl delete secret splunk-$namespace_name-secret -n $namespace_name
kubectl delete -f ./k8s_manifests/splunk_standalone/splunk-operator-install_updated.yaml -n $namespace_name
sleep 60
kubectl delete ns $namespace_name
sleep 120