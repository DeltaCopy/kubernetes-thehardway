#!/usr/bin/env python

import sys
import argparse
import json
import os
from string import Template
import yaml

ANSIBLE_PLAYBOOK_TEMPLATE="ansible-playbook.yml"

# Generate Ansible inventory file and playbook dynamically from json conf file.

def generateAnsibleFiles(configFile):
    print(":: Generating ansible-inventory.")
    try:
        # read json file
        configData = json.load(open(configFile))

        if(len(configData) > 0):
            controllers = configData[0]['controllers']
            workers = configData[0]['workers']
            ansibleInventory = configData[0]['ansibleInventory']
            ansiblePlaybook = configData[0]['ansiblePlaybook']
            staticExternalAddress = configData[0]['staticExternalIP']

            ansibleSettings = configData[0]['ansibleSettings']
            templatesPath = configData[0]['templatesPath']

            with open(ansibleInventory,"w") as f:
                f.writelines("---\n")
                f.writelines("controllers:\n")
                f.writelines("  hosts:\n")
                for controller in controllers:
                    f.writelines("        %s:\n" % controller['name'])
                    f.writelines("            ansible_host: %s\n" % controller['externalIP'])
                    f.writelines("            ansible_ssh_user: %s\n" % controller['sshUser'])
                f.writelines("workers:\n")
                f.writelines("  hosts:\n")
                for worker in workers:
                    f.writelines("        %s:\n" % worker['name'])
                    f.writelines("            ansible_host: %s\n" % worker['externalIP'])
                    f.writelines("            ansible_ssh_user: %s\n" % worker['sshUser'])

            if(os.path.exists(ansibleInventory)):
                print("ansible-inventory created in %s" % ansibleInventory)
            else:
                print("Failed to create ansible-inventory file.")
                sys.exit(1)

            playbookTemplate = templatesPath + "/%s" % ANSIBLE_PLAYBOOK_TEMPLATE 

            if(os.path.exists(playbookTemplate)):
                print("template found.")

                playbook = Template(open(playbookTemplate).read())

                etcdServers=""
                for etcdServer in ansibleSettings['etcdServers']:
                    etcdServers += "\n      - %s: %s" % (etcdServer, ansibleSettings['etcdServers'][etcdServer])

                workerPodCIDR=""
                for podCIDR in ansibleSettings['podCIDR']:
                    workerPodCIDR += "\n      - %s: %s" % (podCIDR,ansibleSettings['podCIDR'][podCIDR])


                values = { 
                    "etcd_servers": etcdServers.strip(),
                    "pod_cidr": workerPodCIDR.strip(),
                    "kubernetes_version" : ansibleSettings['kubernetesVersion'],
                    "kubernetes_public_address": staticExternalAddress,
                    "kube_apiserver_count": ansibleSettings['kubeAPIServerCount'],
                    "cluster_dns": ansibleSettings['clusterDNS'],
                    "cluster_cidr" : ansibleSettings['cluster_cidr']
                }
                                
                

                with open(ansiblePlaybook,"w") as f:
                    f.writelines(yaml.safe_load(yaml.dump(playbook.substitute(values))))

    except Exception as err:
        print("error: %s" % err)
        sys.exit(1)

def main():

    parser = argparse.ArgumentParser(description="KTHW [04] - Generate Ansible files.")

    parser.add_argument(
        "--config", type=str, help="Specify the path to the Kubernetes cluster config json file."
    )

    args = parser.parse_args()

    if (args.config is not None):
        if(os.path.exists(args.config)):
            generateAnsibleFiles(args.config)
        else:
            print("ERROR > Failed to locate config file.")
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()