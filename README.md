
- [Introduction](#introduction)
  - [System Requirements Guidance](#system-requirements-guidance)
  - [Official Product Pages](#official-product-pages)
  - [Final Remarks and Disclaimers](#final-remarks-and-disclaimers)
- [Lab Objectives](#lab-objectives)


# Introduction

A single host lab environment running Kubernetes (K3s) with ArgoCD and also, Docker instances of Jenkins, Gitlab to explore some options.

What does this mean? A single host is exactly that - one single computer. That means this lab can be run on a single system to explore some of the concept around CI/CD ([wikipedia](https://en.wikipedia.org/wiki/CI/CD)).

## System Requirements Guidance

The lab was run on the following hardware and it is therefore recommended as a "known to work" configuration:

* AMD Ryzen 7 5700U ([product page](https://www.amd.com/en/products/apu/amd-ryzen-7-5700u)) (8 core system)
* 64 GiB RAM
* 500 GiB SSD 

The specific product was a "_TUXEDO Pulse 15 - Gen2_" purchased from [Tuxedo](https://www.tuxedocomputers.com/) ([product page](https://www.tuxedocomputers.com/en/Linux-Hardware/Notebooks/15-16-inch/TUXEDO-Pulse-15-Gen2.tuxedo), last visited 13 May 2023)

> **Note**
> Smaller spec systems may work, but the more RAM and cores, generally the better. Some aspects of the LAB may need to be adjusted if your system has less memory or older CPU's with far less cores.

## Official Product Pages

The featured products are listed below.

* Host Operating System: Ubuntu 22.04.2 LTS (Kubuntu Flavor), installed by Tuxedo (with their modifications)
* Canonical Multipass: Used as Virtual Host orchestrator for running a 4x node k3s cluster. ([product page](https://multipass.run/))
* Kubernetes Distribution: [Rancher K3s](https://k3s.io/) - LAB run on version v1.24.10+k3s1
* Kubernetes Continuous Delivery: ArgoCD version 2.7.1 ([GitHub branch](https://github.com/argoproj/argo-cd/tree/v2.7.1)), deployed in Kubernetes
* Container environment: Docker Community Edition version 20.10.21
* Git Repo for LAB: Gitlab Community Edition version 15.9.8-ce.0, running as a Docker container ([product page](https://docs.gitlab.com/ee/install/docker.html))
* Continuous Integration: Jenkins version 2.387.3 ([product page](https://www.jenkins.io/doc/book/getting-started/))

Many other tools and command were also used, and the following must therefore also be available/installed on the system:

* A shell, preferably BASH or a compatible alternative
* Kubectl ([installation instructions](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/))
* Helm version v3.11.2
* A text editor or IDE (Vim and VSCode will do, but this is largely personal preference)
* Python3 (some scripts for managing Git repositories were written in Python)

## Final Remarks and Disclaimers

The LAB demonstrates some concepts and is not to be interpreted as anything official or as a reference implementation. In fact, it is probably more useful in the context of learning and testing, especially testing upgrades of key software components. 

This LAB is bound to age quickly and I hope I can keep this more-or-less up to date.

Many of the LAB settings were deliberately made insecure to concentrate on the functionality and features. 

> **Warning**
> These configurations are **NOT PRODUCTION READY**

It is highly recommended that the LAB systems be shutdown after use to avoid potential security issues. 

> **Warning**
> In addition, keep in mind that LAB environments may be unstable and may cause damage to your system, either by causing data loss or by causing some other form of damage. As such, the owner of this repository (or owners of forks of this repository) cannot be held liable for any damages as a result of using this LAB and following its instructions. Each person using the tools, scripts and other artifacts provided, do so entirely at their own risk. It is highly recommended to experiment with this LAB on a dedicated system that does not have any sensitive or important data stored on it.

# Lab Objectives

![Lab Environment](lab_setup.drawio.png)

Below is a list of objectives of the LAB. Each checked item means the task is more-or-less ready for LAB use. In this lab you fill find instructions for the following:

* [ ] Deploy a 4x node K3s Kubernetes cluster using Multipass on Ubuntu (script)
* [ ] Deploy ArgoCD using Helm
* [ ] Prepare environment and install Gitlab in Docker, including some post installation steps
* [ ] Prepare environment and install Jenkins in Docker
* [ ] Setup Jenkins to use Docker Plugin for Builds
* [ ] Create initial Gitlab repositories
* [ ] Link Jenkins and Gitlab and perform first builds
* [ ] Link ArgoCD to Gitlab for first deployments
* [ ] Perform some common operational procedures:
  * [ ] Update a project and subsequent deployment
  * [ ] Add a suspend feature to remove deployments temporarily or permanently based on configuration

The Web UI will also be used for ArgoCD and Jenkins and as such some steps may be explained based on Firefox. Most of the concepts should also work perfectly on other browsers.

Throughout the experiments you may also want to use additional tools like `kubectl`, `k9s` and the web interface of `traefik`. These may be mentioned, but is completely optional and various other tools may work just as good.