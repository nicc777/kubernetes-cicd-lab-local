def REPO_APP_DIR = ''
def REPO_MAINT_DIR = ''
def skipRemainingStages = false
def APP_SOURCE_BRANCH = 'main'

pipeline {
    agent { node { label "docker-build-node" }}
    stages {
        stage('checkout-application-branch') {
            steps {
                updateGitlabCommitStatus name: 'pipeline-started', state: 'success'
                echo "Checkout Application Repo"
                script {
                    // These are variables set by the GitLab Plugin
                    try {
                        echo "gitlabBranch            : ${gitlabBranch}\n" +
                             "gitlabSourceBranch      : ${gitlabSourceBranch}\n" +
                             "gitlabSourceRepoName    : ${gitlabSourceRepoName}\n" +
                             "gitlabMergeRequestId    : ${gitlabMergeRequestId}\n" +
                             "gitlabTargetBranch      : ${gitlabTargetBranch}\n"
                        APP_SOURCE_BRANCH = gitlabSourceBranch
                    } catch (Exception e) {
                        skipRemainingStages = true
                        def sw = new StringWriter()
                        def pw = new PrintWriter(sw)
                        e.printStackTrace(pw)
                        echo sw.toString()
                    } 
                    try {
                        echo "gitlabTriggerPhrase     : ${gitlabTriggerPhrase}\n"
                    } catch (Exception e) {
                        echo "Does not seems like this build was triggered by a comment"
                    } 
                }
                
                script {
                    def ssh_dir_info = sh( 
                        script: 'ls -lahrt $HOME | grep .ssh && ls -lahrt $HOME/.ssh/*',
                        returnStdout: true
                    ).trim()
                    def whoami = sh( 
                        script: 'whoami',
                        returnStdout: true
                    ).trim()
                    def pwd1 = sh( 
                        script: 'pwd',
                        returnStdout: true
                    ).trim()
                    echo "Running as user ${whoami} in directory ${pwd1}"
                    echo "---------------------------------------------------------------------------------"
                    echo "${ssh_dir_info}"
                    echo "---------------------------------------------------------------------------------"
                    
                    def pwd2 = sh( 
                        script: 'mkdir app_dir && cd app_dir && pwd',
                        returnStdout: true
                    ).trim()
                    REPO_APP_DIR = pwd2
                    
                    def pub_key = sh( 
                        script: 'cat /home/jenkins/.ssh/config',
                        returnStdout: true
                    ).trim()
                    echo "${pub_key}"
                }
                
                dir(REPO_APP_DIR){
                    git branch: APP_SOURCE_BRANCH, credentialsId: 'jenkins-gitlab-ssh', url: 'git@gitlab:lab/application-repo-01.git'
                }
                
                script {
                    echo "REPO_APP_DIR: ${REPO_APP_DIR}"
                    echo "Checking branch ${APP_SOURCE_BRANCH}"
                    def actual_branch = sh(
                        script: 'git status| head -1',
                        returnStdout: true
                    ).trim()
                    echo "actual_branch: ${actual_branch}"
                }

            }
        }
        stage('checkout-maintenance-branch') {
            when {
                expression {
                    !skipRemainingStages
                }
            }
            steps {
                echo "Checkout Maintenance Repo"
                script {
                    def pwd = sh( 
                        script: 'mkdir maint_repo && cd maint_repo && pwd',
                        returnStdout: true
                    ).trim()
                    REPO_MAINT_DIR = pwd
                    echo "REPO_MAINT_DIR: ${REPO_MAINT_DIR}"
                }

                dir(REPO_MAINT_DIR){
                    git branch: 'main', credentialsId: 'jenkins-gitlab-ssh', url: 'git@gitlab:lab/deployment-maintenance.git'
                    script {
                        def config_txt = sh( 
                            script: 'cat .git/config',
                            returnStdout: true
                        ).trim()
                        
                        echo "--------------------- git config ---------------------"
                        echo "${config_txt}"
                        echo "------------------------------------------------------"
                    }
                }
                echo "Checkout CI Repo"
            }
        }
        stage('generate-helm-charts') {
            when {
                expression {
                    !skipRemainingStages
                }
            }
            steps {
                echo "Generate Helm Charts"
                echo "REPO_APP_DIR: ${REPO_APP_DIR}"
                echo "REPO_MAINT_DIR: ${REPO_MAINT_DIR}"
                script {
                    try {
                        dir(REPO_MAINT_DIR){
                            def output = sh( 
                                script: "sh run.sh application_helm_integration.py ${env.BUILD_NUMBER} ${REPO_APP_DIR} ${APP_SOURCE_BRANCH} ${REPO_MAINT_DIR} lab awesome-application 'http://gitlab:8080/lab/${gitlabSourceRepoName}.git' 'http://gitlab:8080/lab/deployment-maintenance.git'",
                                returnStdout: true
                            ).trim()
                            echo "output: ${output}"
                        }
                    } catch (Exception e) {
                        skipRemainingStages = true
                    }       
                }
            }
        }
        stage('commit-helm-charts') {
            when {
                expression {
                    !skipRemainingStages
                }
            }
            steps {
                echo "Commit Helm Charts"
                dir(REPO_MAINT_DIR){
                    sh(
                        script: "git config --local user.email 'jenkins@localhost'",
                        returnStdout: false
                    )
                    sh(
                        script: "git config --local user.name 'jenkins'",
                        returnStdout: false
                    )
                    sh( 
                        script: "eval `ssh-agent` && ssh-add /home/jenkins/.ssh/jenkins_gitlab && git add . && git commit -m 'deployment for Jenkins build ${env.BUILD_NUMBER}' && git push origin main",
                        returnStdout: false
                    )
                }
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