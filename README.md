# kubernetes-thehardway

Repository to store automation assets to build a production grade Kubernetes cluster in the public cloud.

# Description of files

## Configuration file

- conf/cluster.json

This configuration file stores information about certain file paths, IP-Addresses, SSH usernames and configuration related to run Ansible.
If this file is not updated correctly it can potentially lead to issues in bootstrapping Kubernetes.

So, make sure this file is updated correctly.
All Python and shell handler scripts will reference this file, to generate certificates, configuration, dynamically generate Ansible inventory and Playbook.

## Python scripts

- src/01-generate-certs.py

This Python script will generate the SSL Certificates used by the Kubernetes cluster.

- src/02-generate-kubeconfig.py

This Python script will generate the Kubeconfig files for the controller-manager, kube-scheduler, admin user, kube proxy, worker nodes.

- src/03-generate-encryption-keys.py

This Python script will generate an encryption key file used on the Kubernetes Controllers.

- src/04-generate-ansible-files.py

This Python script will generate a dynamic Ansible inventory file along with associated Playbook - data is derived from the conf/cluster.json file.

## Shell scripts

- src/05-kubectl-remote.sh

This shell script will configure kubectl to connect remotely to the Kubernetes cluster, it will connect to the external loadbalancers external IP-Address to communicate with the cluster.

- src/06-dns-addon.sh

This shell script will deploy CoreDNS into the cluster.

- src/setup-client-tools.sh

This shell script will install the required tools necessary to run cfssl, cfssl-json, kubectl

- src/wrapper.sh

This shell script calls all the scripts, then finally the Ansible playbook.

## Templates

A list of static files used by the Python scripts to generate content dynamically.
