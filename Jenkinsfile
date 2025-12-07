pipeline {
    agent {
        kubernetes {
            label 'kaniko-agent'
            defaultContainer 'jnlp'
            yaml """
apiVersion: v1
kind: Pod
metadata:
  labels:
    app: kaniko-agent
spec:
  containers:
  - name: jnlp
    image: jenkins/inbound-agent:latest
    volumeMounts:
    - name: workspace-volume
      mountPath: /home/jenkins/agent
  - name: kaniko
    image: gcr.io/kaniko-project/executor:latest
    command:
    - cat
    tty: true
    volumeMounts:
    - name: workspace-volume
      mountPath: /workspace
    - name: kaniko-secret
      mountPath: /kaniko/.docker
  volumes:
  - name: workspace-volume
    emptyDir: {}
  - name: kaniko-secret
    secret:
      secretName: docker-config
"""
        }
    }

    environment {
        DOCKER_HUB_CREDS = 'dockerhub-credentials'
        DOCKER_IMAGE = 'helentam93/k8s-app:latest'
        DEV_NAMESPACE = 'devops'
        PROD_NAMESPACE = 'prod'
    }

    stages {
        stage('Clone the repo') {
            steps {
                git branch: 'main', url: 'https://github.com/Helen-Tam/k8s-app.git'
            }
        }

        stage('Create Docker registry secret') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: env.DOCKER_HUB_CREDS,
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    container('jnlp') {
                        sh """
                        kubectl create secret docker-registry docker-config \
                          --docker-username=$DOCKER_USER \
                          --docker-password=$DOCKER_PASS \
                          --docker-server=http://index.docker.io/v1/ \
                          -n ${DEV_NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -
                        """
                    }
                }
            }
        }

        stage('Build and push Docker image') {
            steps {
                container('kaniko') {
                    sh """
                    /kaniko/executor \
                      --dockerfile=/workspace/Dockerfile \
                      --context=/workspace \
                      --destination=${DOCKER_IMAGE} \
                      --insecure \
                      --skip-tls-verify
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