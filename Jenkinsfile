pipeline {
    agent {
        kubernetes {
            label 'docker-agent'
            defaultContainer 'jnlp'
            yaml """
apiVersion: v1
kind: Pod
metadata:
  labels:
    app: jenkins-docker-agent
spec:
  containers:
  - name: jnlp
    image: docker:24
    command:
    - cat
    tty: true
    volumeMounts:
    - name: workspace-volume
      mountPath: /home/jenkins/agent
    - name: docker-sock
      mountPath: /var/run/docker.sock
  volumes:
  - name: workspace-volume
    emptyDir: {}
  - name: docker-sock
    hostPath:
      path: /var/run/docker.sock
      type: File
"""
        }
    }

    environment {
        DOCKER_HUB_CREDS = 'dockerhub-credentials'
        DOCKER_IMAGE = 'helentam93/k8s-app:latest'
        PROD_NAMESPACE = 'prod'
    }

    stages {
        stage('Clone the repo') {
            steps {
                git branch: 'main', url: 'https://github.com/Helen-Tam/k8s-app.git'
            }
        }

        stage('Login to Docker Hub') {
            steps {
                container('jnlp') {
                    withCredentials([usernamePassword(
                        credentialsId: env.DOCKER_HUB_CREDS,
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )]) {
                        sh 'docker login -u $DOCKER_USER -p $DOCKER_PASS'
                    }
                }
            }
        }

        stage('Build and push the image') {
            steps {
                container('jnlp') {
                    sh """
                    docker build -t ${DOCKER_IMAGE} .
                    docker push ${DOCKER_IMAGE}
                    """
                }
            }
        }

        stage('Deploy to prod namespace') {
            steps {
                container('jnlp') {
                    sh """
                    kubectl apply -f k8s/prod/app-deployment.yaml -n ${env.PROD_NAMESPACE}
                    kubectl apply -f k8s/prod/app-service.yaml -n ${env.PROD_NAMESPACE}
                    """
                }
            }
        }

        stage('Get the web-app URL') {
            steps {
                container('jnlp') {
                    sh "kubectl get svc -n ${env.PROD_NAMESPACE}"
                }
            }
        }
    }

    post {
        success { echo "The pipeline completed successfully!"}
        failure { echo "The pipeline failed!"}
    }
}