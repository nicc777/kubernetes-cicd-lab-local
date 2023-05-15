
- [Jenkins and Gitlab Integration](#jenkins-and-gitlab-integration)
  - [Preparation](#preparation)
  - [Integration Steps](#integration-steps)
- [Testing and Verification](#testing-and-verification)


# Jenkins and Gitlab Integration

## Preparation

Before starting, by using a user with administrative rights on Gitlab, enable requests on the local network:

![Allow local network](screenshots/integration_gitlab_allow_localnet.png)

## Integration Steps

Follow the instructions from [the Gitlab documentation](https://docs.gitlab.com/ee/integration/jenkins.html) to integrate Jenkins on Group level, using the `lab` group.

To create a group access token, follow [these instructions](https://docs.gitlab.com/ee/user/group/settings/group_access_tokens.html#create-a-group-access-token-using-ui) from the Gitlab documentation.

> **Note**
> These actions require a user with Administrative access. 

The access token on group level have a screen that looks like this:

![Group Access Token](screenshots/integration_gitlab_group_access_token.png)

After the group access token is created, ensure to copy the token value as this will be used in Jenkins.

> **Warning**
> You have to copy the Token while on that screen as there is no way to obtain it again afterwards. If the token value is lost, you need to recreate the token.

In Jenkins, you must first create install the Gitlab plugin, and then afterwards create a Gitlab token credentials:

![Jenkins Credentials](screenshots/integration_jenkins_add_token.png)

Afterward, the Gitlab connection can be made in the Jenkins System COnfiguration page:

![Jenkins System Configuration for Gitlab](screenshots/integration_jenkins_add_gitlab_config.png)

Back in Gitlab, opt for adding the Webhook to integrate a project with Jenkins - pick the `application-repo-1` project for the first test.

> **Warning**
> Since we are not using SSL, ensure the `SSL Verification` option is _**not**_ selected.

# Testing and Verification

Once both sides have been integrated, on Gitlab the webhook can be tested by simulating a PUSH event.

On both Jenkins and Gitlab the event and integration can then be verified:

![Jenkins Task](screenshots/integration_test_webhook_jenkins_view.png)

![Gitab Status](screenshots/integration_test_webhook_gitlab_view.png)
