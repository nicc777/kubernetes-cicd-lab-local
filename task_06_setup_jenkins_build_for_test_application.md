
- [Task Overview and Objectives](#task-overview-and-objectives)
  - [Objective 1 Goals](#objective-1-goals)
  - [Objective 2 Goals](#objective-2-goals)


# Task Overview and Objectives

This is probably one of the more important tasks, as this is where the configuration is done for building our final Helm charts and configuring ArgoCD to deploy our application in Kubernetes.

> **Note**
> It is vital for this step to ensure that Jenkins and Gitlab is properly integrated as described in [task 05](./task_05_integrate_jenkins_and_gitlab.md).

There are two main objectives:

* Objective 1: Create the CI and CD pipeline to act on changes in the application repository and deploy those changes to Kubernetes
* Objective 2: Create a maintenance pipeline to remove expired deployments and to suspend/un-suspend application deployments based on their application tag values.

## Objective 1 Goals

The goal is to implement the following steps:

![CI/CD Steps](lab_setup-CI_and_CD_Steps.png)

| Step | Description                                                                                                             |
|:----:|-------------------------------------------------------------------------------------------------------------------------|
| 1    | Developers will work on the project. Occasionally a change will be pushed to the Git repository.                        |
| 2    | Gitlab will act on the events as per configuration, and call the Webhook to Jenkins based on the configuration.         |
| 3    | Jenkins will first Checkout both the `application-repo-01` and `deployment-maintenance` repositories.                   |
| 4    | In the build process, Jenkins will prepare the Helm template and create a new deployment (namespaced)                   |
| 5    | Jenkins push the updated Helm charts and application manifest to the `deployment-maintenance` repository                |
| 6    | ArgoCD will synchronize the changes from the `deployment-maintenance` repository                                        |
| 7    | The new application is deployed in the Kubernetes cluster                                                               |

In the Helm chart, the `Application` manifest will add the following labels:

* `expires`: With a Unix timestamp in UTC by which time the application will be deleted from the cluster. Default expiry is 30 minutes after deployment (for LAB testing)
* `suspend-start`: with a unix timestamp of when the suspend action will start. Default is to suspend 5 minutes after the initial deployment and the crontab will be calculated therefore relative to the deployment timestamp.
* `suspend-end`: with a unix timestamp of when the suspend action will stop. The suspend will end 10 minutes before the application is scheduled for deletion, calculated relative to the deployment timestamp

Later, we will configure the maintenance pipeline to recalculate the next `suspend-start` and `suspend-end` values when the application comes out of a suspended state.

## Objective 2 Goals

TODO