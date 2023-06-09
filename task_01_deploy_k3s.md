
- [Prelude](#prelude)
- [Deploy k3s](#deploy-k3s)
- [Accessing the cluster](#accessing-the-cluster)
- [Test](#test)

Quick Nav: [Main](./README.md) | Task 1 | [Task 2](./task_02_deploy_argocd_in_kubernetes.md) | [Task 3](./task_03_deploy_gitlab_docker.md) | [Task 4](./task_04_deploy_jenkins_docker.md) | [Task 5](./task_05_integrate_jenkins_and_gitlab.md) | [Task 6](./task_06_setup_jenkins_build_for_test_application.md) | [Notes](./NOTES.md)


# Prelude

This step is optional and is only required if you do not have any Kubernetes cluster available or running that you can use for testing. Alternatives include Kubernetes that comes with Docker Desktop or related/similar tools.

# Deploy k3s

The deployment is done simply by running the script `deploy_k3s_on_multipass.sh`:

```shell
chmod 700 lab_artifacts/*.sh

lab_artifacts/deploy_k3s_on_multipass.sh
```

> **Note**
> There are some settings in the file you can modify to suite your needs, for example the number of nodes.

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

Quick Nav: [Main](./README.md) | Task 1 | [Task 2](./task_02_deploy_argocd_in_kubernetes.md) | [Task 3](./task_03_deploy_gitlab_docker.md) | [Task 4](./task_04_deploy_jenkins_docker.md) | [Task 5](./task_05_integrate_jenkins_and_gitlab.md) | [Task 6](./task_06_setup_jenkins_build_for_test_application.md) | [Notes](./NOTES.md)