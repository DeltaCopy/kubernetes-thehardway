#!/usr/bin/env python

# 03

import random
import string
import base64
import os
import argparse
import sys
import json


print(":: Generating Data Encryption Config and Key.")

def generateEncKeys(clusterConfig):

    # clean existing file
    outfile = clusterConfig['k8sConfPath'] + "/encryption-config.yaml"
    template_file = clusterConfig['templatesPath'] + "/encryption-config.yaml"

    if os.path.exists(outfile):
        os.remove(outfile)

    randstr = "".join(
        random.SystemRandom().choice(string.ascii_letters + string.digits)
        for _ in range(32)
    )
    base64_bytes = base64.b64encode(randstr.encode("ascii"))
    base4_msg = base64_bytes.decode("ascii")

    encrypt_config = string.Template(open(template_file).read())
    encrypt_config_subst = {"secret": base4_msg}
    encrypt_config_data = encrypt_config.substitute(encrypt_config_subst)

    if(encrypt_config_data is not None and len(encrypt_config_data) > 0):
        print("> Data encrypted, saving to file.")

    with open(outfile, "w") as f:
        f.writelines(encrypt_config_data)

    if os.path.exists(outfile):
        print("File %s created." % os.path.abspath(outfile))
    else:
        print("Something went wrong generating Encryption config.")
        sys.exit(1)

def extractConfig(configFile):
    try:
        # read json file
        configData = json.load(open(configFile))

        if(len(configData) > 0):
           
            certificatesPath = configData[0]['certificatesPath']
            k8sConfPath = configData[0]['k8sConfPath']
            templatesPath = configData[0]['templatesPath']

          
            return {
                "certificatesPath" : certificatesPath,
                "k8sConfPath" : k8sConfPath,
                "templatesPath" : templatesPath
            }
    except Exception as error:
        print(error)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="KTHW [06] - Encryption Keys.")
    parser.add_argument(
        "--config", type=str, help="Specify the path to the Kubernetes cluster config json file."
    )

    args = parser.parse_args()

    if (args.config is not None):
        if(os.path.exists(args.config)):
        
            clusterConfig = extractConfig(args.config)
            generateEncKeys(clusterConfig)
        else:
            print("ERROR > Failed to locate config file.")
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()