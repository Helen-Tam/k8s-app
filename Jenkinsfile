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
    image: jenkins/inbound-agent:latest
    args: ['\$(JENKINS_SECRET)', '\$(JENKINS_NAME)']
    volumeMounts:
    - name: workspace-volume
      mountPath: /home/jenkins/agent
  - name: docker
    image: docker:24-dind
    securityContext:
      privileged: true
    env:
      - name: DOCKER_TLS_CERTDIR
        value: ""
    ports:
      - containerPort: 2375
    volumeMounts:
      - name: docker-graph
        mountPath: /var/lib/docker
      - name: workspace-volume
        mountPath: /home/jenkins/agent
    - name: kubectl
      image: bitnami/kubectl:latest
      command:
     -cat
     tty: true
     volumeMounts:
       - name: workspace-volume
         mountPath: /home/jenkins/agent

  volumes:
  - name: workspace-volume
    emptyDir: {}
  - name: docker-graph
    emptyDir: {}
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
                container('docker') {
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
                container('docker') {
                    sh """
                    until docker info >/dev/null 2>&1; do
                        echo "Waiting for Docker daemon"
                        sleep 2
                    done

                    docker build -t ${DOCKER_IMAGE} .
                    docker push ${DOCKER_IMAGE}
                    """
                }
            }
        }

        stage('Deploy to prod namespace') {
            steps {
                container('kubectl') {
                    sh """
                    kubectl apply -f k8s/prod/app-deployment.yaml -n ${env.PROD_NAMESPACE}
                    kubectl apply -f k8s/prod/app-service.yaml -n ${env.PROD_NAMESPACE}
                    """
                }
            }
        }

        stage('Get the web-app URL') {
            steps {
                container('kubectl') {
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