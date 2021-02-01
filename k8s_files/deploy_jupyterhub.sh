#!/bin/bash

# Versions available from https://jupyterhub.github.io/helm-chart/
VERSION="0.11.1"

# Taken from https://zero-to-jupyterhub.readthedocs.io/en/latest/jupyterhub/installation.html 
# Suggested values: advanced users of Kubernetes and Helm should feel
# free to use different values.
RELEASE=jhub
NAMESPACE=jhub

Help()
{
    echo "Deploys a Jupter Hub service to a given cluster."
    echo "Note this assumes that \$KUBECONFIG has already been set and the cluster is reachable"
}

while getopts ":h" option; do
   case $option in
      h) # display Help
         Help
         exit;;
   esac
done

if ! kubectl cluster-info --request-timeout='5s' ; then
    echo "Cannot connect to cluster, have you set \$KUBECONFIG correctly?"
    exit 1;
fi

# Exit on any failure and echo what were up
# so that people can see there's "nothing up my sleeve"
set -ex

helm repo add jupyterhub https://jupyterhub.github.io/helm-chart/
helm repo update

kubectl apply -f cinder-kube-storage.yaml -n $NAMESPACE

helm upgrade --cleanup-on-fail \
  --install $RELEASE jupyterhub/jupyterhub \
  --namespace $NAMESPACE \
  --create-namespace \
  --version=$VERSION \
  --values config.yaml
