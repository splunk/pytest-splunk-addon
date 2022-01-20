#!/bin/sh
set -o errexit
set -o pipefail

wait_for_nodes(){
  while :
  do
    readyNodes=1
    statusList=$(kubectl get nodes --no-headers | awk '{ print $2}')
    while read status
    do
      if [ "$status" == "NotReady" ] || [ "$status" == "" ]
      then
        readyNodes=0
        break
      fi
    done <<< "$(echo -e  "$statusList")"
    if [[ $readyNodes == 1 ]]
    then
      break
    fi
    sleep 1
  done
}

echo "**** Begin installing k3s *** "
curl -sfL https://get.k3s.io  | INSTALL_K3S_EXEC=" --no-deploy traefik --write-kubeconfig-mode 664" sh -
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
wait_for_nodes