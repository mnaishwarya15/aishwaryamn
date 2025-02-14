pipeline {
    agent any
    environment {
        DOCKER_IMAGE = 'flask-app'
        REGISTRY_URL = 'icr.io/ibmproject/flask-form-app'
        CLUSTER_NAME = 'minikube'
        DOCKER_CLI = 'docker:latest'
        DOCKER_CONFIG = '/var/jenkins_home/workspace/.docker'
    }
    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/anagha-ananth/devops_flask_project.git'
            }
        }
        stage('Prepare Workspace') {
            steps {
                script {
                    sh '''
                    mkdir -p $DOCKER_CONFIG
                    chmod 700 $DOCKER_CONFIG
                    '''
                }
            }
        }
        stage('Lint Dockerfile') {
            steps {
                script {
                    sh '''
                    docker run --rm -i hadolint/hadolint < Dockerfile
                    '''
                }
            }
        }
        stage('Build Docker Image') {
            steps {
                script {
                    sh '''
                    docker build -t $REGISTRY_URL/$DOCKER_IMAGE .
                    '''
                }
            }
        }
        stage('Push Docker Image') {
            steps {
                withCredentials([string(credentialsId: 'ibm-cloud-api-key', variable: 'IBMCLOUD_API_KEY')]) {
                    script {
                        sh '''
                        # Install IBM Cloud CLI if it's not already installed
                        curl -sL https://ibm.biz/idt-installer | bash

                        # Log in to IBM Cloud
                        ibmcloud login --apikey "$IBMCLOUD_API_KEY" -r in-che || exit 1

                        # Install IBM Cloud Container Registry plugin if not installed
                        ibmcloud plugin install container-registry || echo "Plugin already installed"

                        # Log in to IBM Cloud Container Registry
                        ibmcloud cr login || exit 1

                        # Verify authentication before pushing
                        ibmcloud cr info

                        # Push the Docker image to IBM Cloud Registry
                        docker push $REGISTRY_URL/$DOCKER_IMAGE
                        '''
                    }
                }
            }
        }
        stage('Deploy to Kubernetes') {
            steps {
                script {
                    sh '''
                # Check if kubectl is installed
                if ! command -v kubectl &> /dev/null; then
                    echo "kubectl not found, installing..."
                    curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
                    chmod +x kubectl
                
                    # Ensure the directory exists before moving
                    mkdir -p /var/jenkins_home/.local/bin
                
                    # Move kubectl to the local bin directory
                    mv kubectl /var/jenkins_home/.local/bin/kubectl
                fi
                
                # Add the new path to PATH if needed
                export PATH=$PATH:/var/jenkins_home/.local/bin
                kubectl version --client
                '''
                }
            }
        }
    }
    post {
        success {
            echo 'Pipeline executed successfully!'
        }
        failure {
            echo 'Pipeline failed. Check logs.'
        }
    }
}
