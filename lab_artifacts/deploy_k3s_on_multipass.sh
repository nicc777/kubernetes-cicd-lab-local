#!/usr/bin/env bash

# Refer to https://github.com/k3s-io/k3s/releases for your prefered release
export INSTALL_K3S_VERSION="v1.24.10+k3s1"

for node in node1 node2 node3 node4;do
echo "Lanchuing node ${node}"
multipass launch -n $node -c 2 -m 12G
done

# Init cluster on node1
multipass exec node1 -- bash -c "curl -sfL https://get.k3s.io | INSTALL_K3S_VERSION=$INSTALL_K3S_VERSION sh -"

# Get node1's IP
IP=$(multipass info node1 | grep IPv4 | awk '{print $2}')

# Get Token used to join nodes
TOKEN=$(multipass exec node1 sudo cat /var/lib/rancher/k3s/server/node-token)

# Join node2
multipass exec node2 -- \
bash -c "curl -sfL https://get.k3s.io | K3S_URL=\"https://$IP:6443\" K3S_TOKEN=\"$TOKEN\" sh -"

# Join node3
multipass exec node3 -- \
bash -c "curl -sfL https://get.k3s.io | K3S_URL=\"https://$IP:6443\" K3S_TOKEN=\"$TOKEN\" sh -"

# Join node4
multipass exec node4 -- \
bash -c "curl -sfL https://get.k3s.io | K3S_URL=\"https://$IP:6443\" K3S_TOKEN=\"$TOKEN\" sh -"

# Get cluster's configuration
multipass exec node1 sudo cat /etc/rancher/k3s/k3s.yaml > k3s.yaml

# Set node1's external IP in the configuration file
#sed -i '' "s/127.0.0.1/$IP/" k3s.yaml    # BASH
sed -i "s/127.0.0.1/$IP/" k3s.yaml        # ZSH

# We'r all set
echo
echo "K3s cluster is ready !"
echo
echo "Run the following command to set the current context:"
echo "$ export KUBECONFIG=$PWD/k3s.yaml"
echo
echo "and start to use the cluster:"
echo  "$ kubectl get nodes"
echo