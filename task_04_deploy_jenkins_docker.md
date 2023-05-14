
- [Why Jenkins and why Docker?](#why-jenkins-and-why-docker)

# Why Jenkins and why Docker?

Jenkins have been used for years now and is a very well known and common CI tool. In many organizations in fulfills both the CI and CD roles.

Because it is likely to encounter Jenkins in the real, it is included in this lab. Keep in mind that there are a number of other tools and approaches. Even if you do not use Jenkins right now, it may still be good to at least follow the basic steps of this LAB to get it running, as it is perfect to illustrate some of the common CI approaches in modern Kubernetes systems, working alongside ArgoCD in cluster for CD tasks.

As with Gitlab, even if you can run Jenkins in Kubernetes, it is still most likely to run in dedicated server environments. This LAB, however, will take advantage of some more modern features of Jenkins to use Docker as build nodes.
