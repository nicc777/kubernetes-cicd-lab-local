
- [Jenkins and Gitlab Integration](#jenkins-and-gitlab-integration)


# Jenkins and Gitlab Integration

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
