#!/usr/bin/env bash 
set -euo pipefail

# Wrapper script to invoke the Python scripts and ansible-playbook
CONF=$1

#CONF="../conf/cluster.json"

if [ -f "$CONF" ] && [ ! -z $(echo $CONF|grep ".json") ]; then
    ansible_inventory=$(cat $CONF | python -c 'import json,sys;obj=json.load(sys.stdin);print(obj[0]["ansibleInventory"])')
    ansible_playbook=$(cat $CONF | python -c 'import json,sys;obj=json.load(sys.stdin);print(obj[0]["ansiblePlaybook"])')
    echo "[01] Generating TLS Certificates******************************************************************"
    python 01-generate-certs.py --config $CONF
    echo "[02] Generating Kubeconfig files******************************************************************"
    python 02-generate-kubeconfig.py --config $CONF
    echo "[03] Generating Encryption Key file***************************************************************"
    python 03-generate-encryption-keys.py --config $CONF
    echo "[04] Generating Ansible files*********************************************************************"
    python 04-generate-ansible-files.py --config $CONF
    echo "[05] Running ansible-playbook*********************************************************************"
    echo ansible-playbook "$ansible_playbook" -i "$ansible_inventory" 
    ansible-playbook "$ansible_playbook" -i "$ansible_inventory"

    if [ $? -eq 0 ]; then
        echo "[06] Configuring kubectl remote***************************************************************"
        ./05-kubectl-remote.sh
        echo "[07] Adding DNS*******************************************************************************"
        ./06-dns-addon.sh
    fi
else
    echo "$CONF is not a valid path to the .json config file."
    echo "Usage $0 [path to config .json file]"
    exit 1
fi