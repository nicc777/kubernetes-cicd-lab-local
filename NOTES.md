
- [Observations during development and testing](#observations-during-development-and-testing)
  - [ArgoCD does not always cleanup deployments](#argocd-does-not-always-cleanup-deployments)
  - [Namespaces are not deleted](#namespaces-are-not-deleted)
- [Other Ideas and Thoughts](#other-ideas-and-thoughts)
  - [Suspend Logic](#suspend-logic)
- [Strategy for Testing](#strategy-for-testing)


# Observations during development and testing

## ArgoCD does not always cleanup deployments

It seems ArgoCD is not always happy if the deployment template manifests directory is not present in which case the application state goes to an `unknown` state and the application must be manually deleted from ArgoCD.

One possible solution: Delete only the application manifest and keep the deployment template directories. Only delete these latter directories at a later stage.

## Namespaces are not deleted

When applications are deleted, namespaces are not automatically deleted. 

A possible solution would be to have a process running in cluster to delete namespaces older than a couple of hours that have no resources (pods, services and deployments).

# Other Ideas and Thoughts

## Suspend Logic

The implementation in this LAB is really basic and probably most optimal only for this LAB.

Real world logic would probably have to be adjusted to take into considerations various factors. One real world scenario could have the following requirements:

1. Suspend all applications over weekend, starting at some time on Friday evening (say, after 21:00) and ending early Monday morning (say, after 08:00)
2. Suspend during the week days (Monday to Thursday) when no developers are working (perhaps from 21:00 the evening until 08:00 the next morning)
3. Perhaps add some kind of flag or configuration item that development teams can set to override the default behavior. This would be good for teams working after hours, or in a different time zone.
4. Consider a pipeline to manually bring a suspended application back into operation. This may allow a team that needs to work over a weekend to bring their suspended application deployments back online.

> **Note**
> About timezones, ensure that timezones and how it influences your logic and your team is well understood. As a guideline, consider using only UTC timestamps and all "time" is relative to UTC. Remember teams or team members in different time zones and also consider where the workload is physically deployed in terms of it's timezone.

# Strategy for Testing

The Python functions in the `deployment-maintenance` repository does the heavy lifting and can therefore be easily adapted for offline testing.

In terms of "offline" it really implies "without committing changes to the `deployment-maintenance` repository.

Since the python scripts essentially only create, move and delete files on the local file system, they can easily be manually run and tested to see the effects on the local file system without affecting the running cluster. 

In the `awesome-application-ci` pipeline, the commit for new application deployments are done in the Jenkins pipeline script, therefore creating new application deployments in the `application_helm_integration.py` script does not actually push changes to git. This script can therefore be tested unchanged with some hand crafted command line arguments for example:

```shell
cd /tmp

rm -frR /tmp/script-tests

mkdir /tmp/script-tests

cd /tmp/script-tests

git clone git@gitlab:lab/application-repo-01.git 

git clone git@gitlab:lab/deployment-maintenance.git 

cd deployment-maintenance

export TEST_NR="`date +%s`"

python3 "application_helm_integration.py"                             \
    "cli-test-${TEST_NR}"                                             \
    "/tmp/script-tests/application-repo-01"                           \
    "test-${TEST_NR}"                                                 \
    "/tmp/script-tests/deployment-maintenance"                        \
    "lab"                                                             \
    "awesome-application"                                             \
    "http://gitlab:8080/lab/application-repo-01.git"                  \
    "http://gitlab:8080/lab/deployment-maintenance.git"

python3 "application_cleanup.py"                \
    "/tmp/script-tests/deployment-maintenance"  \
    "TEST"

python3 "application_cleanup.py"                \
     "/tmp/script-tests/deployment-maintenance" \
     "TEST"
```

There will be some output generated from the script - mostly for debug and troubleshooting purposes. However, the following can also be done to inspect the result.

First, run:

```shell
tree deployments/lab
```

And now inspect the output (our output may be different):

```text
# output of the command : tree deployments/lab

deployments/lab
├── application-manifests
│   ├── app-issue-11-113.yaml
│   ├── app-test-1-cli-test-1.yaml
│   └── README.md
└── helm-manifests
├── app-issue-11-113
│   ├── Chart.yaml
│   ├── templates
│   │   ├── awesome_webpage.yaml
│   │   └── ingress.yaml
│   └── values.yaml
├── app-test-1-cli-test-1
│   ├── Chart.yaml
│   ├── templates
│   │   ├── awesome_webpage.yaml
│   │   └── ingress.yaml
│   └── values.yaml
└── README.md
```

In the above output, `app-issue-11-113` directory and files refers to an _actual_ deployment, where the `app-test-1-cli-test-1` directory and files refers to the test run.

To reset the test directories, simply run:

```shell
cd /tmp

rm -frR /tmp/script-tests

# No run the previous commands again...
```
