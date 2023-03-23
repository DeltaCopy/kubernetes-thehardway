#!/usr/bin/env bash
set -euo pipefail

CONF="$1"

echo "::Setting kubectl remote access."
if [ -f "$CONF" ]; then
    KUBERNETES_PUBLIC_ADDRESS=$(cat $CONF | python -c 'import json,sys;obj=json.load(sys.stdin);print(obj[0]["staticExternalIP"])')
    KUBERNETES_CLUSTER_NAME=$(cat $CONF | python -c 'import json,sys;obj=json.load(sys.stdin);print(obj[0]["clusterName"])')
    KUBERNETES_CERTS=$(cat $CONF | python -c 'import json,sys;obj=json.load(sys.stdin);print(obj[0]["certificatesPath"])')
else
    echo "ERROR > Failed to locate Kubernetes cluster json file."
    echo "Script usage: $0 [path to cluster.json file]"
    exit 1
fi

if [ ! -z "$KUBERNETES_PUBLIC_ADDRESS" ] && [ ! -z "$KUBERNETES_CLUSTER_NAME" ] && [ ! -z "$KUBERNETES_CERTS" ]; then

    if [ ! -d "$KUBERNETES_CERTS" ]; then
        echo "ERROR > Failed to locate $KUBERNETES_CERTS"
        exit 1
    fi
    echo "KUBERNETES_PUBLIC_ADDRESS=$KUBERNETES_PUBLIC_ADDRESS"
    echo "KUBERNETES_CLUSTER_NAME=$KUBERNETES_CLUSTER_NAME"
    echo
    echo "::Setting cluster."
    kubectl config set-cluster $KUBERNETES_CLUSTER_NAME \
        --certificate-authority="$KUBERNETES_CERTS/ca.pem" \
        --embed-certs=true \
        --server=https://${KUBERNETES_PUBLIC_ADDRESS}:6443

    echo
    echo "::Setting credentials."
    kubectl config set-credentials admin \
        --client-certificate="$KUBERNETES_CERTS/admin.pem" \
        --client-key="$KUBERNETES_CERTS/admin-key.pem"

    echo
    echo "::Setting context."
    kubectl config set-context kubernetes-the-hard-way \
        --cluster=kubernetes-the-hard-way \
        --user=admin

    echo
    echo "::Using context $KUBERNETES_CLUSTER_NAME"
    kubectl config use-context kubernetes-the-hard-way

    echo
    # Validate kubectl remote access
    echo "********Version info********"
    kubectl version

    echo "********Worker nodes********"
    kubectl get nodes
else
    echo "ERROR > Failed to extract KUBERNETES_PUBLIC_ADDRESS, KUBERNETES_CLUSTER_NAME and KUBERNETES_CERTS"
    exit 1
fi
