#!/usr/bin/env bash


# Install Client tools
# 1 Install CFSSL
# 2 Install kubectl


# 1


cfssl_version="1.6.1"
cfssl_json_version="1.6.1"
install_dest="/usr/local/bin"


if [ -d ".tools" ]; then
    rm -rf ".tools"
fi


mkdir .tools

echo "::Downloading cfssl & cfssl-json"

curl -L -s https://github.com/cloudflare/cfssl/releases/download/v${cfssl_version}/cfssl_${cfssl_version}_linux_amd64 > ".tools/cfssl" && chmod +x ".tools/cfssl"
curl -L -s https://github.com/cloudflare/cfssl/releases/download/v${cfssl_json_version}/cfssljson_${cfssl_json_version}_linux_amd64 > ".tools/cfssl-json" && chmod +x ".tools/cfssl-json"

if [ $? -ne 0 ]; then
    echo "Download failed."
    exit 1
fi

echo "Done."
# 2

echo "::Downloading kubectl"

curl -L -s "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" > ".tools/kubectl" && chmod +x ".tools/kubectl"

if [ $? -ne 0 ]; then
    echo "Download failed."
    exit 1
fi

echo "Done."
# Verification

echo "::Verifying binaries."

echo "::cfssl"
.tools/cfssl version | grep $cfssl_version

echo "::cfssl-json"
.tools/cfssl-json -version | grep $cfssl_json_version

echo "::kubectl sha256sum check"

curl -LOs "https://dl.k8s.io/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl.sha256"
echo "$(<kubectl.sha256) .tools/kubectl" | sha256sum --check

echo "::kubectl client version"
.tools/kubectl version --client

echo "::Moving binaries to $install_dest"

sudo mv .tools/cfssl .tools/cfssl-json .tools/kubectl $install_dest
