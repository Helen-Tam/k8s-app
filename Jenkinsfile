pipeline {
    agent {
        kubernetes {
            label 'k8s-agent'
             defaultContainer 'jnlp'
        }
    }

    environment {
        DOCKER_HUB_CREDENTIALS = 'dockerhub-credentials'
        DOCKER_IMAGE = 'helentam93/k8s-app:latest'
        DEV_NAMESPACE = 'devops'
        PROD_NAMESPACE = 'prod'
    }

    stages {
        stage('Clone the repo') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/Helen-Tam/k8s-app.git'
            }
        }

        stage('Build Docker image') {
            steps {
                script {
                    docker.build(env.DOCKER_IMAGE)
                }
            }
        }

        stage('Push the image to Docker Hub') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: env.DOCKER_HUB_CREDENTIALS,
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    script {
                        sh """
                        echo \$DOCKER_PASS | docker login -u \$DOCKER_USER --password-stdin
                        docker push ${env.DOCKER_IMAGE}
                        """
                    }
                }
            }
        }

        stage('Deploy to prod namespace') {
            steps {
                sh """
                kubectl apply -f k8s/prod/app-deployment.yaml -n ${env.PROD_NAMESPACE}
                kubectl apply -f k8s/prod/app-service.yaml} -n ${env.PROD_NAMESPACE}
                """
            }
        }

        stage('Get the web-app URL') {
            steps {
                sh """
                kubectl get svc -n ${env.PROD_NAMESPACE}
                """
            }
        }
    }

    post {
        success { echo "The pipeline completed successfully!"}
        failure { echo "The pipeline failed!"}
    }
}