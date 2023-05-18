# Deployment and Maintenance Repository

This repository is firstly for scripts to integrate the application build artifacts into Helm charts for deployment. Secondly, the scripts can also be used to manage the deployment of artifacts like deleting them or suspending them.

| Script File                                                            | Purpose                                                     |
|------------------------------------------------------------------------|-------------------------------------------------------------|
| [application_helm_integration.py](./application_helm_integration.py)   | Produce the Helm charts for a deployment                    |
| [application_cleanup.py](./application_cleanup.py)                     | Deletes currently deployed applications that expired        |
| [application_suspend.py](./application_suspend.py)                     | Ensures applications are deployed only during certain times |

