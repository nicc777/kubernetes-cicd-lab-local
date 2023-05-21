# Observations during development and testing

## ArgoCD does not always cleanup deployments

It seems ArgoCD is not always happy if the deployment template manifests directory is not present in which case the application state goes to an `unknown` state and the application must be manually deleted from ArgoCD.

One possible solution: Delete only the application manifest and keep the deployment template directories. Only delete these latter directories at a later stage.

## Namespaces are not deleted

When applications are deleted, namespaces are not automatically deleted. 

A possible solution would be to have a process running in cluster to delete namespaces older than a couple of hours that have no resources (pods, services and deployments).