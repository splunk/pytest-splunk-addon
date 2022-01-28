#!/bin/sh
kubectl delete -f "$(dirname -- "$0")"/splunk_standalone_updated.yaml -n $NAMESPACE_NAME
sleep 15
kubectl delete svc nginx -n $NAMESPACE_NAME
kubectl delete pod nginx -n $NAMESPACE_NAME
kubectl delete secret splunk-$NAMESPACE_NAME-secret -n $NAMESPACE_NAME
kubectl delete -f "$(dirname -- "$0")"/namespace_updated.yaml
sleep 15