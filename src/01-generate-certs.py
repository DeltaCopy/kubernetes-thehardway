#!/usr/bin/env python

# 04

import os
import subprocess
import sys
import argparse
import json
from string import Template
import shutil
import logging
import tarfile

kubernetes_hostnames = "kubernetes,kubernetes.default,kubernetes.default.svc,kubernetes.default.svc.cluster,kubernetes.svc.cluster.local"

'''
The Kubernetes API server is automatically assigned the kubernetes internal dns name, 
which will be linked to the first IP address (10.32.0.1) from the address range (10.32.0.0/24)
'''

kubernetes_static_ip_addresses = "10.32.0.1"
# tools

cfssl = "cfssl"
cfssl_json = "cfssl-json"

print(":: Setting up SSL certificates")

def checkCertsDir(clusterConfig,template_files):
    print(":: Checking certs directory exists.")

    if not os.path.exists(clusterConfig['certificatesPath']):
        os.mkdir(clusterConfig['certificatesPath'])
    else:
        print('removing..')
        shutil.rmtree(clusterConfig['certificatesPath'])
        os.mkdir(clusterConfig['certificatesPath'])

    if (
        os.path.exists(template_files["ca_config"])
        and os.path.exists(template_files["ca_csr"])
        and os.path.exists(template_files["admin_csr"])
        and os.path.exists(template_files["worker_csr"])
    ):
        print("File: %s found." % template_files["ca_config"])
        print("File: %s found." % template_files["ca_csr"])
        print("File: %s found." % template_files["admin_csr"])
        print("File: %s found." % template_files["worker_csr"])
    else:
        print("ERROR > Failed to find all pre-check files.")
        sys.exit(1)


def genPemFiles(clusterConfig,template_files):
    # check cfssl is installed
    try:
        print(":: Generating Certificates.")
        print("Generating .pem files")

        p1_gen_cert1 = subprocess.Popen(
            [cfssl, "gencert", "-initca", template_files["ca_csr"]],
            stdout=subprocess.PIPE,
        )

        print(
            "#################################################################################################################"
        )
        p2_json_out1 = subprocess.Popen(
            [cfssl_json, "-bare", clusterConfig['certificatesPath'] + "/" + "ca"],
            stdin=p1_gen_cert1.stdout,
            stdout=subprocess.PIPE,
        )

        p1_gen_cert1.stdout.close()
        output, err = p2_json_out1.communicate()
        # cfssl gencert -initca ca-csr.json | cfssljson -bare ca

        if (
            os.path.exists(clusterConfig['certificatesPath'] + "/ca.pem")
            and os.path.exists(clusterConfig['certificatesPath'] + "/ca-key.pem")
            and os.path.exists(clusterConfig['certificatesPath'] + "/ca.csr")
        ):
            print(".pem files generated.")
        else:
            sys.exit(1)
        # Generate admin certificates

        print(
            "#################################################################################################################"
        )
    except Exception as err:
        print(err)
        sys.exit(1)

def genAdminCert(clusterConfig,template_files):

    p2_gen_cert1 = subprocess.Popen(
        [
            cfssl,
            "gencert",
            "-ca=%s"% clusterConfig['certificatesPath'] + "/" + "ca.pem",
            "-ca-key=%s" % clusterConfig['certificatesPath'] + "/" + "ca-key.pem",
            "-config=%s" % template_files["ca_config"],
            "-profile=kubernetes",
            "%s" % template_files["admin_csr"],
        ],
        stdout=subprocess.PIPE,
    )

    p2_json_out1 = subprocess.Popen(
        [cfssl_json, "-bare", clusterConfig['certificatesPath'] + "/" + "admin"],
        stdin=p2_gen_cert1.stdout,
        stdout=subprocess.PIPE,
    )

    p2_gen_cert1.stdout.close()
    output, err = p2_json_out1.communicate()

    if p2_json_out1.returncode == 0:
        print("> admin certificate generated.")
    else:
        sys.exit(1)

def genNodeCerts(clusterConfig,template_files):
    # Worker node certificates
    # Generate a certificate and private key for each Kubernetes worker node:

    worker_csr = Template(open(template_files["worker_csr"]).read())

    for worker in range(1, clusterConfig['workersCount'] + 1):
        worker_csr_subst = {"instance": clusterConfig["workers"][worker -1]['name']}
        worker_csr_data = worker_csr.substitute(worker_csr_subst)

        with open(clusterConfig['certificatesPath'] + "/" + clusterConfig["workers"][worker -1]['name'] + "-csr.json", "w") as f:
            f.writelines(json.dumps(json.loads(worker_csr_data), indent=4))
        print(
            "#################################################################################################################"
        )
        p3_gen_cert1 = subprocess.Popen(
            [
                cfssl,
                "gencert",
                "-ca=%s" % clusterConfig['certificatesPath'] + "/" + "ca.pem",
                "-ca-key=%s" % clusterConfig['certificatesPath'] + "/" + "ca-key.pem",
                "-config=%s" % template_files["ca_config"],
                "-hostname=%s,%s,%s" % (clusterConfig["workers"][worker -1]['name'], clusterConfig["workers"][worker -1]['externalIP'], clusterConfig["workers"][worker -1]['internalIP']),
                "-profile=kubernetes",
                "%s" % clusterConfig['certificatesPath'] + "/" + clusterConfig["workers"][worker -1]['name'] + "-csr.json",
            ],
            stdout=subprocess.PIPE,
        )

        p3_json_out1 = subprocess.Popen(
            [cfssl_json, "-bare", clusterConfig['certificatesPath'] + "/" + "%s" % clusterConfig["workers"][worker -1]['name']],
            stdin=p3_gen_cert1.stdout,
            stdout=subprocess.PIPE,
        )

        p3_gen_cert1.stdout.close()
        output, err = p3_json_out1.communicate()

        if p3_json_out1.returncode == 0:
            print("> %s certificate successfully generated." % clusterConfig["workers"][worker -1]['name'])
        else:
            sys.exit(1)

    print("> Worker node certificates stored in %s" % clusterConfig['certificatesPath'])
    # f.close()


def genKubeControllerCert(clusterConfig,template_files):
    print(":: Generating kube-controller-manager client certificate/private key.")

    print(
        "#################################################################################################################"
    )

    p4_gen_cert1 = subprocess.Popen(
        [
            cfssl,
            "gencert",
            "-ca=%s" % clusterConfig['certificatesPath'] + "/" + "ca.pem",
            "-ca-key=%s" % clusterConfig['certificatesPath'] + "/" + "ca-key.pem",
            "-config=%s" % template_files["ca_config"],
            "-profile=kubernetes",
            template_files["kube_controller_manager_csr"],
        ],
        stdout=subprocess.PIPE,
    )

    p4_json_out1 = subprocess.Popen(
        [cfssl_json, "-bare", clusterConfig['certificatesPath'] + "/" + "kube-controller-manager"],
        stdin=p4_gen_cert1.stdout,
        stdout=subprocess.PIPE,
    )

    p4_gen_cert1.stdout.close()
    output, err = p4_json_out1.communicate()

    if p4_json_out1.returncode == 0:
        print("> kube-controller-manager client certificate generated.")
    else:
        sys.exit(1)


def genKubeProxyCert(clusterConfig,template_files):
    print(":: Generating kube-proxy certificate/private key.")

    print(
        "#################################################################################################################"
    )

    p5_gen_cert1 = subprocess.Popen(
        [
            cfssl,
            "gencert",
            "-ca=%s" % clusterConfig['certificatesPath'] + "/" + "ca.pem",
            "-ca-key=%s" % clusterConfig['certificatesPath'] + "/" + "ca-key.pem",
            "-config=%s" % template_files["ca_config"],
            "-profile=kubernetes",
            template_files["kube_proxy_csr"],
        ],
        stdout=subprocess.PIPE,
    )

    p5_json_out1 = subprocess.Popen(
        [cfssl_json, "-bare", clusterConfig['certificatesPath'] + "/" + "kube-proxy"],
        stdin=p5_gen_cert1.stdout,
        stdout=subprocess.PIPE,
    )

    p5_gen_cert1.stdout.close()
    output, err = p5_json_out1.communicate()

    if p5_json_out1.returncode == 0:
        print("> kube-proxy client certificate generated.")
    else:
        sys.exit(1)


def genKubeScheduler(clusterConfig,template_files):
    print(":: Generating kube-scheduler certificate/private key.")

    print(
        "#################################################################################################################"
    )

    p6_gen_cert1 = subprocess.Popen(
        [
            cfssl,
            "gencert",
            "-ca=%s" % clusterConfig['certificatesPath'] + "/" + "ca.pem",
            "-ca-key=%s" % clusterConfig['certificatesPath'] + "/" + "ca-key.pem",
            "-config=%s" % template_files["ca_config"],
            "-profile=kubernetes",
            template_files["kube_scheduler_csr"],
        ],
        stdout=subprocess.PIPE,
    )

    p6_json_out1 = subprocess.Popen(
        [cfssl_json, "-bare", clusterConfig['certificatesPath'] + "/" + "kube-scheduler"],
        stdin=p6_gen_cert1.stdout,
        stdout=subprocess.PIPE,
    )

    p6_gen_cert1.stdout.close()
    output, err = p6_json_out1.communicate()

    if p6_json_out1.returncode == 0:
        print("> kube-scheduler certificate generated.")
    else:
        sys.exit(1)


def genApiServerCert(clusterConfig,template_files):
    print(":: Generating API Server certificate/private key.")

    print(
        "#################################################################################################################"
    )

    static_internal_ip = ""

    for controller in clusterConfig['controllers']:

        static_internal_ip += controller['internalIP'] + ","
  
    p7_gen_cert1 = subprocess.Popen(
        [
            cfssl,
            "gencert",
            "-ca=%s" % clusterConfig['certificatesPath'] + "/" + "ca.pem",
            "-ca-key=%s" % clusterConfig['certificatesPath'] + "/" + "ca-key.pem",
            "-config=%s" % template_files["ca_config"],
            "-hostname=%s,%s,127.0.0.1,%s"
                            % (kubernetes_static_ip_addresses + "," + static_internal_ip[:-1], clusterConfig['staticExternalIP'], kubernetes_hostnames),
            "-profile=kubernetes",
            template_files["kubernetes_csr"],
        ],
        stdout=subprocess.PIPE,
    )

    p7_json_out1 = subprocess.Popen(
        [cfssl_json, "-bare", clusterConfig['certificatesPath'] + "/" + "kubernetes"],
        stdin=p7_gen_cert1.stdout,
        stdout=subprocess.PIPE,
    )

    p7_gen_cert1.stdout.close()
    output, err = p7_json_out1.communicate()

    if p7_json_out1.returncode == 0:
        print("> API Server certificate generated.")
    else:
        sys.exit(1)


def genServiceAccCert(clusterConfig,template_files):
    print(":: Generating Service account certificate/private key.")

    print(
        "#################################################################################################################"
    )

    p8_gen_cert1 = subprocess.Popen(
        [
            cfssl,
            "gencert",
            "-ca=%s" % clusterConfig['certificatesPath'] + "/" + "ca.pem",
            "-ca-key=%s" % clusterConfig['certificatesPath'] + "/" + "ca-key.pem",
            "-config=%s" % template_files["ca_config"],
            "-profile=kubernetes",
            template_files["service_account_csr"],
        ],
        stdout=subprocess.PIPE,
    )

    p8_json_out1 = subprocess.Popen(
        [cfssl_json, "-bare", clusterConfig['certificatesPath'] + "/" + "service-account"],
        stdin=p8_gen_cert1.stdout,
        stdout=subprocess.PIPE,
    )

    p8_gen_cert1.stdout.close()
    output, err = p8_json_out1.communicate()

    if p8_json_out1.returncode == 0:
        print("> Service account certificate generated.")
    else:
        sys.exit(1)


def extractConfig(configFile):
    try:
        # read json file
        configData = json.load(open(configFile))

        if(len(configData) > 0):
            workersCount = configData[0]['workersCount']
            controllersCount = configData[0]['controllersCount']

            staticExternalIP = configData[0]['staticExternalIP']

            certificatesPath = configData[0]['certificatesPath']
            k8sCertsPath = configData[0]['certificatesPath']
            templatesPath = configData[0]['templatesPath']

            controllers = configData[0]['controllers']
            workers = configData[0]['workers']



            return {
                "workersCount" : workersCount,
                "controllersCount": controllersCount,
                "workers" : workers,
                "controllers": controllers,
                "staticExternalIP": staticExternalIP,
                "certificatesPath" : certificatesPath,
                "templatesPath" : templatesPath
            }
    except Exception as error:
        print(error)
        sys.exit(1)

def archiveFiles(clusterConfig):
    print("::Archiving files.")
    try:
        path = clusterConfig['certificatesPath']
        tarFilename = path + "/k8s-certs.tar.gz"
        
        filenames = []
        with tarfile.open(tarFilename,"w:gz") as archive:
            for root,dirs,files in os.walk(path):
                for file in files:
                
                    archive.add(os.path.join(root,file),arcname=os.path.basename(file))
        archive.close()


    except Exception as err:
        print(err)
        sys.exit(1)

def main():

    parser = argparse.ArgumentParser(description="KTHW [04] - SSL Certificates.")

    parser.add_argument(
        "--config", type=str, help="Specify the path to the Kubernetes cluster config json file."
    )

    args = parser.parse_args()

    if (args.config is not None):
        if(os.path.exists(args.config)):
        
            clusterConfig = extractConfig(args.config)
            template_files = {
                "ca_config": clusterConfig['templatesPath'] + "/ca-config.json",
                "ca_csr": clusterConfig['templatesPath'] + "/ca-csr.json",
                "admin_csr": clusterConfig['templatesPath'] + "/admin-csr.json",
                "worker_csr": clusterConfig['templatesPath'] + "/worker-csr.json",
                "kube_controller_manager_csr": clusterConfig['templatesPath'] + "/kube-controller-manager-csr.json",
                "kube_proxy_csr": clusterConfig['templatesPath'] + "/kube-proxy-csr.json",
                "kube_scheduler_csr": clusterConfig['templatesPath'] + "/kube-scheduler-csr.json",
                "kubernetes_csr": clusterConfig['templatesPath'] + "/kubernetes-csr.json",
                "service_account_csr": clusterConfig['templatesPath'] + "/service-account-csr.json",
            }

            checkCertsDir(clusterConfig,template_files)
            genPemFiles(clusterConfig,template_files)
            genAdminCert(clusterConfig,template_files)
            genNodeCerts(clusterConfig,template_files)
            genKubeControllerCert(clusterConfig,template_files)
            genKubeProxyCert(clusterConfig,template_files)
            genKubeScheduler(clusterConfig,template_files)
            genApiServerCert(clusterConfig,template_files)
            genServiceAccCert(clusterConfig,template_files)

            archiveFiles(clusterConfig)
        else:
            print("ERROR > Failed to locate config file.")
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
