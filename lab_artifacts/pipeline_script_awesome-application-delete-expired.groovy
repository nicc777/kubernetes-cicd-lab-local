def REPO_MAINT_DIR = ''

pipeline {
    agent { node { label "docker-build-node" }}
    stages {
        stage('checkout-maintenance-branch') {
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
                }
                echo "Checkout CI Repo"
            }
        }
        stage('cleanup-expired-deployments') {
            steps {
                script {
                    try {
                        dir(REPO_MAINT_DIR){
                            def output = sh( 
                                script: "python3 application_cleanup.py ${REPO_MAINT_DIR}",
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
    }
}