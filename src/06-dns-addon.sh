#!/usr/bin/env bash

# DNS Addon
# Deploying the DNS cluster addon

# DNS add-on which provides DNS based service discovery, backed by CoreDNS, to applications running inside the Kubernetes cluster.

# The DNS Cluster Add-on

kubectl apply -f https://storage.googleapis.com/kubernetes-the-hard-way/coredns-1.8.yaml

# List the pods created by the kube-dns deployment:

kubectl get pods -l k8s-app=kube-dns -n kube-system

# Verification

# Create a busybox deployment:

kubectl run busybox --image=busybox:1.28 --command -- sleep 3600

# List the pod created by the busybox deployment:

kubectl get pods -l run=busybox

# Retrieve the full name of the busybox pod:

POD_NAME=$(kubectl get pods -l run=busybox -o jsonpath="{.items[0].metadata.name}")

#Execute a DNS lookup for the kubernetes service inside the busybox pod:

kubectl exec -ti $POD_NAME -- nslookup kubernetes
