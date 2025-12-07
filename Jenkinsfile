pipeline {
    agent {
        kubernetes {
            label 'kaniko'
             defaultContainer 'kaniko'
        }
    }

    environment {
        DOCKER_IMAGE = 'helentam93/k8s-app:latest'
        PROD_NAMESPACE = 'prod'
    }

    stages {
        stage('Clone the repo') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/Helen-Tam/k8s-app.git'
            }
        }

        stage('Build and push Docker image') {
            steps {
                sh """
                /kaniko/executor \
                  --dockerfile=Dockerfile \
                  --context=\$(pwd) \
                  --destination=${DOCKER_IMAGE}
                  """
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