
- [Preparations](#preparations)
- [Deploy ArgoCD in Kubernetes](#deploy-argocd-in-kubernetes)
- [Post Installation Tasks](#post-installation-tasks)
  - [Add hosts entry](#add-hosts-entry)
  - [Web Browser Proxy Configuration](#web-browser-proxy-configuration)
- [Test](#test)
- [Other useful commands](#other-useful-commands)

Quick Nav: [Main](./README.md) | [Task 1](./task_01_deploy_k3s.md) | Task 2 | [Task 3](./task_03_deploy_gitlab_docker.md) | [Task 4](./task_04_deploy_jenkins_docker.md) | [Task 5](./task_05_integrate_jenkins_and_gitlab.md) | [Task 6](./task_06_setup_jenkins_build_for_test_application.md) | [Notes](./NOTES.md)

# Preparations

There are some values that need to be edited in the values file.

To get the original values, run the following command:

```shell
helm show values argo/argo-cd --version=5.33.1 > /tmp/argocd-helm-values.yaml
```

One of the major changes was to add _**Ingress**_ to the configuration.

> **Note**
> In general you don't have to supply specific versions, however, there are at least two things to keep in mind: 1) In a LAB setting, you need repeatable experiments under a consistent environment. If a version changes by the time this LAB is followed, it may affect outcomes; and 2) Kubernetes major version changes usually introduce breaking changes. It is good to know which versions of applications is compatible with which version of Kubernetes and then target those known working versions based on the cluster version.

# Deploy ArgoCD in Kubernetes 

Run the following commands:

```shell
# Only needed once. Not required if this command was tun previously
helm repo add argo https://argoproj.github.io/argo-helm

kubectl create namespace argocd

helm install -n argocd argocd argo/argo-cd --version=5.33.1 -f lab_artifacts/argocd-helm-values.yaml

kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
# Expect something like doLsjoj1F8cTyrf9
```

> **Note**
> Save the admin password returned from the last command.

# Post Installation Tasks

## Add hosts entry

In order to use the web based UI from ArgoCD, a couple of extra steps is required to connect via the deployed Ingress configuration.

> **Note**
> Normally a Load Balancer will be used to connect ot the various proxy end-points exposed by the Ingress controller. However, to simplify the LAB environment, only one IP address of the cluster will be chosen as the entry point and in a web browser of your choice you would need to point to that Node IP address. Also, since this is a LAB environment, DNS for certain hosts are simulated by hosts file entries.

First, get the IP addresses of the nodes:

```shell
multipass list
```

Example output:

```text
Name                    State             IPv4             Image
node1                   Running           10.15.174.149    Ubuntu 22.04 LTS
                                          10.42.0.0
                                          10.42.0.1
node2                   Running           10.15.174.129    Ubuntu 22.04 LTS
                                          10.42.1.0
                                          10.42.1.1
node3                   Running           10.15.174.132    Ubuntu 22.04 LTS
                                          10.42.2.0
                                          10.42.2.1
node4                   Running           10.15.174.3      Ubuntu 22.04 LTS
                                          10.42.3.0
                                          10.42.3.1
```

Pick any of the primary IP addresses (one of `10.15.174.3`, `10.15.174.132`, `10.15.174.129` or `10.15.174.149` - but relevant to your environment)

Add the hosts entry:

```shell
sudo cp /etc/hosts /etc/hosts_BACKUP_lab_02

sudo echo "10.15.174.3   argocd argocd-grpc argocd.example.tld argocd-grpc.example.tld" >> /etc/hosts
```

## Web Browser Proxy Configuration

For the LAB environment, it is recommended you use a separate browser profile ([Firefox Documentation on Profiles](https://support.mozilla.org/en-US/kb/profile-manager-create-remove-switch-firefox-profiles)).

In Firefox, the proxy settings should be the following:

![Firefox Proxy Settings](screenshots/firefox_network_settings.png)

The `no-proxy` settings (for easy copy/paste):

```text
127.0.0.1,localhost,192.168.2.18,gitlab,gitlab.example.tld,jenkins,jenkins.example.tld
```

> **Note**
> The `192.168.2.18` IP address, is the IP address of the LAB system. Adjust to suite your environment.

# Test

After the installation and post-installation tasks are done, point your LAB browser to http://argocd.example.tld/

Login with the username `admin` and the password saved from the setup steps.

# Other useful commands

List all available Helm versions:

```shell
helm search repo argo/argo-cd -l
```

Quick Nav: [Main](./README.md) | [Task 1](./task_01_deploy_k3s.md) | Task 2 | [Task 3](./task_03_deploy_gitlab_docker.md) | [Task 4](./task_04_deploy_jenkins_docker.md) | [Task 5](./task_05_integrate_jenkins_and_gitlab.md) | [Task 6](./task_06_setup_jenkins_build_for_test_application.md) | [Notes](./NOTES.md)
