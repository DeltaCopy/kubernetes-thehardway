#!/usr/bin/env python

# 05

import os
import subprocess
import sys
import argparse
import shutil
import json
import tarfile
import glob


def genWorkerConfig(configData):
    print(":: Generating kubeconfig file for each worker.")

    for worker in range(1,  configData['workersCount'] + 1):
        # clean old files if present

        if os.path.exists("%s/%s.kubeconfig" % (configData['k8sConfPath'], configData["workers"][worker -1]['name'])):
            os.remove("%s/%s.kubeconfig" % (configData['k8sConfPath'], configData["workers"][worker -1]['name']))

        p1_kubeconfig = subprocess.check_output(
            [
                "kubectl",
                "config",
                "set-cluster",
                "kubernetes-the-hard-way",
                "--certificate-authority=%s/ca.pem" % configData['certificatesPath'],
                "--embed-certs=true",
                #"--server=https://%s:6443" % (configData["workers"][worker -1]['externalIP']),
                "--server=https://%s:6443" % configData['staticExternalIP'],
                "--kubeconfig=%s/%s.kubeconfig" % (configData['k8sConfPath'], configData["workers"][worker -1]['name']),
            ]
        )

        if 'Cluster "kubernetes-the-hard-way" set.' in str(p1_kubeconfig):
            if os.path.exists("%s/worker-%s.kubeconfig" % (configData['k8sConfPath'], str(worker))):
                print("worker-%s kubeconfig file generated." % str(worker))
        else:
            sys.exit(1)

        p2_kubeconfig = subprocess.check_output(
            [
                "kubectl",
                "config",
                "set-credentials",
                "system:node:%s" % configData["workers"][worker -1]['name'],
                "--client-certificate=%s/%s.pem" % (configData['certificatesPath'], configData["workers"][worker -1]['name']),
                "--client-key=%s/%s-key.pem" % (configData['certificatesPath'], configData["workers"][worker -1]['name']),
                "--embed-certs=true",
                "--kubeconfig=%s/%s.kubeconfig" % (configData['k8sConfPath'], configData["workers"][worker -1]['name']),
            ]
        )

        if 'User "system:node:%s" set.' % configData["workers"][worker -1]['name'] in str(p2_kubeconfig):
            print("%s system node set." % configData["workers"][worker -1]['name'])

        p3_kubeconfig = subprocess.check_output(
            [
                "kubectl",
                "config",
                "set-context",
                "default",
                "--cluster=kubernetes-the-hard-way",
                "--user=system:node:%s" % configData["workers"][worker -1]['name'],
                "--kubeconfig=%s/%s.kubeconfig" % (configData['k8sConfPath'], configData["workers"][worker -1]['name']),
            ]
        )

        if 'Context "default" created.' or 'Context "default" modified.' in str(
            p3_kubeconfig
        ):
            print("%s context default created." % configData["workers"][worker -1]['name'])
        else:
            print(str(p3_kubeconfig.strip()))
            sys.exit(1)

        p4_kubeconfig = subprocess.check_output(
            [
                "kubectl",
                "config",
                "use-context",
                "default",
                "--kubeconfig=%s/%s.kubeconfig" % (configData['k8sConfPath'], configData["workers"][worker -1]['name']),
            ]
        )

        if 'Switched to context "default".' in str(p4_kubeconfig):
            print('%s switched to context "default".' % configData["workers"][worker -1]['name'])
        else:
            print(str(p4_kubeconfig.strip()))
            sys.exit(1)


def genKubeProxyConfig(configData):
    print(":: Generating kubeconfig file for kube-proxy service.")

    # Clean old file

    if os.path.exists("%s/kube-proxy.kubeconfig" % configData['k8sConfPath']):
        os.remove("%s/kube-proxy.kubeconfig" % configData['k8sConfPath'])

    p5_kubeconfig = subprocess.check_output(
        [
            "kubectl",
            "config",
            "set-cluster",
            "kubernetes-the-hard-way",
            "--certificate-authority=%s/ca.pem" % configData['certificatesPath'],
            "--embed-certs=true",
            "--server=https://%s:6443" % configData['staticExternalIP'],
            "--kubeconfig=%s/kube-proxy.kubeconfig" % configData['k8sConfPath'],
        ]
    )
    if 'Cluster "kubernetes-the-hard-way" set.' in str(
        p5_kubeconfig
    ) and os.path.exists("%s/kube-proxy.kubeconfig" % configData['k8sConfPath']):
        print('Cluster "kubernetes-the-hard-way" set.')
    else:
        print(str(p5_kubeconfig))
        sys.exit(1)

    p6_kubeconfig = subprocess.check_output(
        [
            "kubectl",
            "config",
            "set-credentials",
            "system:kube-proxy",
            "--client-certificate=%s/kube-proxy.pem" % configData['certificatesPath'],
            "--client-key=%s/kube-proxy-key.pem" % configData['certificatesPath'],
            "--embed-certs=true",
            "--kubeconfig=%s/kube-proxy.kubeconfig" % configData['k8sConfPath'],
        ]
    )
    if 'User "system:kube-proxy" set.' in str(p6_kubeconfig):
        print('User "system:kube-proxy" set.')
    else:
        print(str(p6_kubeconfig))
        sys.exit(1)

    p7_kubeconfig = subprocess.check_output(
        [
            "kubectl",
            "config",
            "set-context",
            "default",
            "--cluster=kubernetes-the-hard-way",
            "--user=system:kube-proxy",
            "--kubeconfig=%s/kube-proxy.kubeconfig" % configData['k8sConfPath'],
        ]
    )

    if 'Context "default" created.' in str(p7_kubeconfig):
        print('Context "default" created.')
    else:
        print(str(p7_kubeconfig))
        sys.exit(1)

    p8_kubeconfig = subprocess.check_output(
        [
            "kubectl",
            "config",
            "use-context",
            "default",
            "--kubeconfig=%s/kube-proxy.kubeconfig" % configData['k8sConfPath'],
        ]
    )

    if 'Switched to context "default".' in str(p8_kubeconfig):
        print('kube-proxy switched to context "default".')
    else:
        print(str(p8_kubeconfig.strip()))
        sys.exit(1)


def genControllerMgrConfig(configData):
    print(":: Generating kubeconfig file for kube-controller-manager service.")

    # Clean old file

    if os.path.exists("%s/kube-controller-manager.kubeconfig" % configData['k8sConfPath']):
        os.remove("%s/kube-controller-manager.kubeconfig" % configData['k8sConfPath'])

    p9_kubeconfig = subprocess.check_output(
        [
            "kubectl",
            "config",
            "set-cluster",
            "kubernetes-the-hard-way",
            "--certificate-authority=%s/ca.pem" % configData['certificatesPath'],
            "--embed-certs=true",
            "--server=https://127.0.0.1:6443",
            "--kubeconfig=%s/kube-controller-manager.kubeconfig" % configData['k8sConfPath'],
        ]
    )

    if 'Cluster "kubernetes-the-hard-way" set.' in str(p9_kubeconfig):
        print('Cluster "kubernetes-the-hard-way" set')
    else:
        print(str(p9_kubeconfig))
        sys.exit(1)

    p10_kubeconfig = subprocess.check_output(
        [
            "kubectl",
            "config",
            "set-credentials",
            "system:kube-controller-manager",
            "--client-certificate=%s/kube-controller-manager.pem" % configData['certificatesPath'],
            "--client-key=%s/kube-controller-manager-key.pem" % configData['certificatesPath'],
            "--embed-certs=true",
            "--kubeconfig=%s/kube-controller-manager.kubeconfig" % configData['k8sConfPath'],
        ]
    )

    if 'User "system:kube-controller-manager" set.' in str(p10_kubeconfig):
        print('User "system:kube-controller-manager" set.')
    else:
        print(str(p10_kubeconfig))
        sys.exit(1)

    p11_kubeconfig = subprocess.check_output(
        [
            "kubectl",
            "config",
            "set-context",
            "default",
            "--cluster=kubernetes-the-hard-way",
            "--user=system:kube-controller-manager",
            "--kubeconfig=%s/kube-controller-manager.kubeconfig" % configData['k8sConfPath'],
        ]
    )

    if 'Context "default" created.' in str(p11_kubeconfig):
        print('Context "default" created.')
    else:
        print(str(p11_kubeconfig))
        sys.exit(1)

    p12_kubeconfig = subprocess.check_output(
        [
            "kubectl",
            "config",
            "use-context",
            "default",
            "--kubeconfig=%s/kube-controller-manager.kubeconfig" % configData['k8sConfPath'],
        ]
    )

    if 'Switched to context "default".' in str(p12_kubeconfig):
        print('kube-controller-manager switched to context "default".')
    else:
        print(str(p12_kubeconfig.strip()))
        sys.exit(1)


def genKubeSchedConfig(configData):
    print(":: Generating kubeconfig file for kube-scheduler service.")

    # Clean old file

    if os.path.exists("%s/kube-scheduler.kubeconfig" % configData['k8sConfPath']):
        os.remove("%s/kube-scheduler.kubeconfig" % configData['k8sConfPath'])

    p13_kubeconfig = subprocess.check_output(
        [
            "kubectl",
            "config",
            "set-cluster",
            "kubernetes-the-hard-way",
            "--certificate-authority=%s/ca.pem" % configData['certificatesPath'],
            "--embed-certs=true",
            "--server=https://127.0.0.1:6443",
            "--kubeconfig=%s/kube-scheduler.kubeconfig" % configData['k8sConfPath'],
        ]
    )

    if 'Cluster "kubernetes-the-hard-way" set.' in str(p13_kubeconfig):
        print('Cluster "kubernetes-the-hard-way" set')
    else:
        print(str(p13_kubeconfig))
        sys.exit(1)

    p14_kubeconfig = subprocess.check_output(
        [
            "kubectl",
            "config",
            "set-credentials",
            "system:kube-scheduler",
            "--client-certificate=%s/kube-scheduler.pem" % configData['certificatesPath'],
            "--client-key=%s/kube-scheduler-key.pem" % configData['certificatesPath'],
            "--embed-certs=true",
            "--kubeconfig=%s/kube-scheduler.kubeconfig" % configData['k8sConfPath'],
        ]
    )

    if 'User "system:kube-scheduler" set.' in str(p14_kubeconfig):
        print('User "system:kube-scheduler" set.')
    else:
        print(str(p14_kubeconfig))
        sys.exit(1)

    p15_kubeconfig = subprocess.check_output(
        [
            "kubectl",
            "config",
            "set-context",
            "default",
            "--cluster=kubernetes-the-hard-way",
            "--user=system:kube-scheduler",
            "--kubeconfig=%s/kube-scheduler.kubeconfig" % configData['k8sConfPath'],
        ]
    )

    if 'Context "default" created.' in str(p15_kubeconfig):
        print('Context "default" created.')
    else:
        print(str(p15_kubeconfig))
        sys.exit(1)

    p16_kubeconfig = subprocess.check_output(
        [
            "kubectl",
            "config",
            "use-context",
            "default",
            "--kubeconfig=%s/kube-scheduler.kubeconfig" % configData['k8sConfPath'],
        ]
    )

    if 'Switched to context "default".' in str(p16_kubeconfig):
        print('kube-scheduler switched to context "default".')
    else:
        print(str(p16_kubeconfig.strip()))
        sys.exit(1)


def genAdminConfig(configData):
    print(":: Generating kubeconfig file for Admin user.")

    # Clean old file

    if os.path.exists("%s/admin.kubeconfig" % configData['k8sConfPath']):
        os.remove("%s/admin.kubeconfig" % configData['k8sConfPath'])

    p17_kubeconfig = subprocess.check_output(
        [
            "kubectl",
            "config",
            "set-cluster",
            "kubernetes-the-hard-way",
            "--certificate-authority=%s/ca.pem" % configData['certificatesPath'],
            "--embed-certs=true",
            "--server=https://127.0.0.1:6443",
            "--kubeconfig=%s/admin.kubeconfig" % configData['k8sConfPath'],
        ]
    )

    if 'Cluster "kubernetes-the-hard-way" set.' in str(p17_kubeconfig):
        print('Cluster "kubernetes-the-hard-way" set')
    else:
        print(str(p17_kubeconfig))
        sys.exit(1)

    p18_kubeconfig = subprocess.check_output(
        [
            "kubectl",
            "config",
            "set-credentials",
            "admin",
            "--client-certificate=%s/admin.pem" % configData['certificatesPath'],
            "--client-key=%s/admin-key.pem" % configData['certificatesPath'],
            "--embed-certs=true",
            "--kubeconfig=%s/admin.kubeconfig" % configData['k8sConfPath'],
        ]
    )

    if 'User "admin" set.' in str(p18_kubeconfig):
        print('User "admin" set.')
    else:
        print(str(p18_kubeconfig))
        sys.exit(1)

    p19_kubeconfig = subprocess.check_output(
        [
            "kubectl",
            "config",
            "set-context",
            "default",
            "--cluster=kubernetes-the-hard-way",
            "--user=admin",
            "--kubeconfig=%s/admin.kubeconfig" % configData['k8sConfPath'],
        ]
    )

    if 'Context "default" created.' in str(p19_kubeconfig):
        print('Context "default" created.')
    else:
        print(str(p19_kubeconfig))
        sys.exit(1)

    p20_kubeconfig = subprocess.check_output(
        [
            "kubectl",
            "config",
            "use-context",
            "default",
            "--kubeconfig=%s/admin.kubeconfig" % configData['k8sConfPath'],
        ]
    )

    if 'Switched to context "default".' in str(p20_kubeconfig):
        print('admin switched to context "default".')
    else:
        print(str(p20_kubeconfig.strip()))
        sys.exit(1)

def extractConfig(configFile):
    try:
        # read json file
        configData = json.load(open(configFile))

        if(len(configData) > 0):
            workersCount = configData[0]['workersCount']
            controllersCount = configData[0]['controllersCount']

            staticExternalIP = configData[0]['staticExternalIP']

            controllers = configData[0]['controllers']
            workers = configData[0]['workers']
            certificatesPath = configData[0]['certificatesPath']
            k8sConfPath = configData[0]['k8sConfPath']


            return {
                "workersCount" : workersCount,
                "controllersCount": controllersCount,
                "workers" : workers,
                "controllers": controllers,
                "staticExternalIP": staticExternalIP,
                "certificatesPath" : certificatesPath,
                "k8sConfPath" : k8sConfPath
            }
    except Exception as error:
        print(error)
        sys.exit(1)

def archiveFiles(clusterConfig):
    print("::Archiving files.")
    try:
        path = clusterConfig['k8sConfPath']
        tarFilename = path + "/k8s-kubeconfig.tar.gz"
        
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

    parser = argparse.ArgumentParser(description="KTHW [05] - Kubectl config.")

    parser.add_argument(
        "--config", type=str, help="Specify the path to the Kubernetes cluster config json file."
    )

    args = parser.parse_args()

    if args.config is not None:
        if len(args.config) == 0:
            parser.print_help()
            sys.exit(1)
        else:
            if os.path.exists(args.config):
                clusterConfig = extractConfig(args.config)
            else:
                print("ERROR > Failed to locate config file.")
                sys.exit(1)

            if not os.path.exists(clusterConfig['k8sConfPath']):
                os.mkdir(clusterConfig['k8sConfPath'])
            else:
                print('removing..')
                shutil.rmtree(clusterConfig['k8sConfPath'])
                os.mkdir(clusterConfig['k8sConfPath'])

            '''
            if os.path.exists(clusterConfig['k8sConfPath']):
                pattern = r"%s/**.kubeconfig" % clusterConfig['k8sConfPath']

                for item in glob.iglob(pattern,recursive=True):
                    os.remove(item)
            #os.mkdir(configData['k8sConfPath'])

            '''

            genWorkerConfig(clusterConfig)
            genKubeProxyConfig(clusterConfig)
            genControllerMgrConfig(clusterConfig)
            genKubeSchedConfig(clusterConfig)
            genAdminConfig(clusterConfig)

            archiveFiles(clusterConfig)
            
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
