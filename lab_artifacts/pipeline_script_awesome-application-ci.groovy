pipeline {
    agent { node { label "docker-build-node" }}
    stages {
        stage('checkout-application-branch') {
            steps {
                updateGitlabCommitStatus name: 'checkout', state: 'pending'
                echo "Checkout Application Repo"
                
                script {
                    def whoami = sh (
                        script: 'whoami',
                        returnStdout: true
                    )
                    echo "whoami: ${whoami}"
                }
                
                script {
                    def myHome = sh (
                        script: 'echo $HOME',
                        returnStdout: true
                    )
                    echo "Home Directory: ${myHome}"
                }
                
                script {
                    def hosts = sh (
                        script: 'cat /etc/hosts',
                        returnStdout: true
                    )
                    echo 'Hosts:'
                    echo hosts
                }
                
                script {
                    def sshConfig = sh (
                        script: 'cat /home/jenkins/.ssh/config',
                        returnStdout: true
                    )
                    echo 'SSH Config:'
                    echo sshConfig
                }
                
                git branch: 'main', credentialsId: 'jenkins-gitlab-ssh', url: 'git@gitlab:lab/application-repo-01.git'
                
                script {
                    def listing = sh( 
                        script: 'pwd && echo && echo && ls -lahrt',
                        returnStdout: true
                    )
                    echo 'Listing: '
                    echo listing    
                }
                echo "Checkout CI Repo"
            }
        }
        stage('generate-helm-charts') {
            steps {
                updateGitlabCommitStatus name: 'generate-helm-charts', state: 'running'
                echo "Generate Helm Charts"
                
            }
        }
        stage('commit-helm-charts') {
            steps {
                updateGitlabCommitStatus name: 'commit-helm-charts', state: 'running'
                echo "Commit Helm Charts"
                /*
                sshagent (credentials: ['git-ssh-credentials-ID']) {
                    sh("git tag -a some_tag -m 'Jenkins'")
                    sh('git push <REPO> --tags')
                }
                */
            }
        }
        stage('cleanup') {
            steps {
                echo "DONE"
                updateGitlabCommitStatus name: 'build', state: 'success'
            }
        }
    }
}