
- [Deploy k3s](#deploy-k3s)
- [Accessing the cluster](#accessing-the-cluster)
- [Test](#test)


# Deploy k3s

The deployment is done simply by running the script `deploy_k3s_on_multipass.sh`:

```shell
chmod 700 lab_artifacts/*.sh

lab_artifacts/deploy_k3s_on_multipass.sh
```

# Accessing the cluster

A separate Kubernetes client configuration file is created in `$PWD/k3s.yaml`, and you can easily use this by setting the following environment variable:

```shell
export KUBECONFIG=$PWD/k3s.yaml
```

> **Note**
> Do this in every terminal from where you want to access the local cluster.

The configuration can also be combined with an existing Kubernetes configuration, but that is not in scope for this lab.

# Test

If the following command works, the setup was successful:

```shell
kubectl get nodes
```

Example output:

```text
NAME    STATUS   ROLES                  AGE    VERSION
node3   Ready    <none>                 2d1h   v1.26.4+k3s1
node4   Ready    <none>                 2d1h   v1.26.4+k3s1
node2   Ready    <none>                 2d1h   v1.26.4+k3s1
node1   Ready    control-plane,master   2d1h   v1.24.10+k3s1
```

