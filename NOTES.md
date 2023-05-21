
- [Observations during development and testing](#observations-during-development-and-testing)
  - [ArgoCD does not always cleanup deployments](#argocd-does-not-always-cleanup-deployments)
  - [Namespaces are not deleted](#namespaces-are-not-deleted)
- [Other Ideas and Thoughts](#other-ideas-and-thoughts)
  - [Suspend Logic](#suspend-logic)


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
