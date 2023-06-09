
- [Why Gitlab and why Docker?](#why-gitlab-and-why-docker)
- [Preparing Docker](#preparing-docker)
- [Running Gitlab in Docker](#running-gitlab-in-docker)
- [Post Installation Tasks](#post-installation-tasks)
  - [Add hosts entry](#add-hosts-entry)
  - [Add Users](#add-users)
  - [Create Initial Group and Project](#create-initial-group-and-project)
  - [Import Initial Projects](#import-initial-projects)

Quick Nav: [Main](./README.md) | [Task 1](./task_01_deploy_k3s.md) | [Task 2](./task_02_deploy_argocd_in_kubernetes.md) | Task 3 | [Task 4](./task_04_deploy_jenkins_docker.md) | [Task 5](./task_05_integrate_jenkins_and_gitlab.md) | [Task 6](./task_06_setup_jenkins_build_for_test_application.md) | [Notes](./NOTES.md)

# Why Gitlab and why Docker?

Gitlab is my my humble opinion one of the fully featured Git servers that is the easiest to setup in a standalone/dedicated hosting environment.

Technically you could run Gitlab in Kubernetes, but in the last 20+ years of using Git, and even today, I still find most enterprises running Git either a standalone version or a newer cloud version (SaaS). The popular Git services you are most likely to find include Gitlab, GitHub and BitBucket.

Running Gitlab in DOcker therefore very closely resembles "real life" and since we are not too concerned about most of the power features in this LAB, Gitlab is a perfect option that is really easy to deploy and use.

More advanced users who want to take advantage of some more powerful built-in CI features in their respective Git application can easily skip this step and adjust some of the other configurations or commands to suite their needs.

# Preparing Docker

You will need to edit your systemd Docker configuration in `/lib/systemd/system/docker.service`

Replace the line `ExecStart=/usr/bin/dockerd -H fd:// --containerd=/run/containerd/containerd.sock` with:

```text
ExecStart=/usr/bin/dockerd -H tcp://0.0.0.0:4243 -H unix:///var/run/docker.sock
```

Afterwards run:

```shell
sudo systemctl daemon-reload

sudo service docker restart
```

> **Note**
> This step is technically only required from the Jenkins step, but doing this at this early stage prevents any potential issues with Gitlab later on 

> **Warning**
> This process will make your LAB environment insecure and it is highly recommended that he LAB network is in a network that does not allow any direct connection from the Internet. 

Refer to the [Docker documentation](https://docs.docker.com/engine/security/protect-access/#use-tls-https-to-protect-the-docker-daemon-socket) to secure your exposed Docker TCP port.

# Running Gitlab in Docker

> **Warning**
> Gitlab can be fairly resource intensive. If your system has 32 GiB or less RAM, I would recommend running Gitlab on a second computer.

Also note that the IP addresses shown in the example needs to be updated to your environment.

The commands below is essentially a summary of the [official documentation](https://docs.gitlab.com/ee/install/docker.html):

```shell
docker volume create gitlab_config

docker volume create gitlab_logs

docker volume create gitlab_data

# NOTE !!!
#
#   Replace the IP addresses below with the relevant IP addresses for your environment

docker run --detach \
  --hostname gitlab.example.tld \
  --publish 8443:443 --publish 8080:80 --publish 8022:22 \
  --name gitlab \
  --restart always \
  --volume gitlab_config:/etc/gitlab \
  --volume gitlab_logs:/var/log/gitlab \
  --volume gitlab_data:/var/opt/gitlab \
  --add-host="argocd:10.15.174.3" \
  --add-host="argocd.example.tld:10.15.174.3" \
  --add-host="jenkins:192.168.2.18" \
  --add-host="jenkins.example.tld:192.168.2.18" \
  --shm-size 256m \
  gitlab/gitlab-ce:15.9.8-ce.0

# See when install is done via:
docker logs -f gitlab

# get the password:
docker exec -it gitlab grep 'Password:' /etc/gitlab/initial_root_password
```

# Post Installation Tasks

## Add hosts entry

Assuming your Docker installation was successful, run the following command:

```shell
sudo cp /etc/hosts /etc/hosts_BACKUP_lab_03

sudo echo "192.168.2.18    gitlab gitlab.example.tld jenkins jenkins.example.tld" >> /etc/hosts
```

## Add Users

In the LAB environment you could use just the `root` account, but in order to test some other features with multiple users, it is recommended you create at least 2x other normal users.

At the same time, it may be a good idea to also create 2x local Unix user accounts. Create SSH keys for each and add the public keys to the corresponding Gitlab users.

> **Note**
> It may be a good idea to use the same username for the Unix account as well as the Gitlab account. It will then allow you to user variables like `$USER` in commands as shown below

The following command adds two Unix user accounts that will be active for 1 week:

```shell
sudo useradd -m -s /usr/bin/zsh -c "LAB Test User" -e `date +%Y-%m-%d -d "+7 days"` lab_user_1

sudo useradd -m -s /usr/bin/zsh -c "LAB Test User" -e `date +%Y-%m-%d -d "+7 days"` lab_user_2

# Verify Expiry:
(sudo chage -l lab_user_1 && sudo chage -l lab_user_2) | grep "Account expires"

# Set password:
sudo passwd lab_user_1

sudo passwd lab_user_2

# To quickly change to one of the new user accounts (this will require only your root password and not the user password):
sudo su - lab_user_1
```

For each of the Unix users, you need to add some config to their `~/.ssh/config` file:

```shell
# Setup user keys
ssh-keygen -f $HOME/.ssh/gitlab_local_docker

cat > ~/.ssh/config << EOF
Host gitlab
    Hostname gitlab
    Port 8022
    IdentityFile $HOME/.ssh/gitlab_local_docker
    IdentitiesOnly yes
EOF

chmod 600 $HOME/.ssh/config
```

Assuming you have a repository called `test`, you can now clone the repository with:

```shell
git clone git@gitlab:$USER/test.git
```

Without the SSH config, you need to run the following:

```shell
GIT_SSH_COMMAND='ssh -i ~/.ssh/gitlab_local_docker -p 8022 -o IdentitiesOnly=yes' git clone git@gitlab:$USER/test.git
```

## Create Initial Group and Project

Using the web UI, create a group called `lab` and add the test users with a role of `Developer` to the group.

Next, as an administrative user (like `root`), create the following blank projects with a README.md for the `lab` group:

* `application-repo-01`
* `deployment-maintenance`

Creating a new project should look something like this:

![Create Project](screenshots/gitlab_project_create.png)

Afterwards, you should see something like the following:

![projects](screenshots/gitlab_lab_projects.png)

For the LAB experiments to run more smoothly, remove the branch protection from the `main` branch for each of the new projects:

![Branch Protection](screenshots/gitlab_protected_branches.png)

After adding the LAB users to the `lab` group, the users view in Gitlab should look something like this:

![users](screenshots/gitlab_users.png)

## Import Initial Projects

As one of the LAB users, run the following commands to import the example projects:

```shell
# MAIN USER
sudo su - lab_user_1

# The rest of the commands are now run as user lab_user_1

git clone https://github.com/nicc777/kubernetes-cicd-lab-local.git

# Add the following public key to your GitLab account
cat .ssh/gitlab_local_docker.pub 

# After the SSH key is added, run the following commands:
git clone git@gitlab:lab/application-repo-01.git 

git clone git@gitlab:lab/deployment-maintenance.git 

cp -vfr kubernetes-cicd-lab-local/application-repo-01/* application-repo-01 

cp -vfr kubernetes-cicd-lab-local/deployment-maintenance/* deployment-maintenance 

cd application-repo-01 

git config --local user.name "User1"

git config --local user.email "user1@localhost"

add .

git commit -m "Import"

git push origin main

cd ../deployment-maintenance

git config --local user.name "User1"

git config --local user.email "user1@localhost"

add .

git commit -m "Import"

git push origin main
```

Quick Nav: [Main](./README.md) | [Task 1](./task_01_deploy_k3s.md) | [Task 2](./task_02_deploy_argocd_in_kubernetes.md) | Task 3 | [Task 4](./task_04_deploy_jenkins_docker.md) | [Task 5](./task_05_integrate_jenkins_and_gitlab.md) | [Task 6](./task_06_setup_jenkins_build_for_test_application.md) | [Notes](./NOTES.md)