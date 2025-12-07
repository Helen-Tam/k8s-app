pipeline {
    agent {
        kubernetes {
            label 'docker-agent'
            defaultContainer 'jnlp'
            yaml '''
apiVersion: v1
kind: Pod
metadata:
  labels:
    app: jenkins-docker-agent
spec:
  serviceAccountName: jenkins-admin
  containers:
  - name: jnlp
    image: jenkins/inbound-agent:latest
    args: ['$(JENKINS_SECRET)', '$(JENKINS_NAME)']
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
    volumeMounts:
      - name: docker-graph
        mountPath: /var/lib/docker
      - name: workspace-volume
        mountPath: /home/jenkins/agent

  - name: kubectl
    image: sashak9/pod-agent:latest
    tty: true
    volumeMounts:
      - name: kubeconfig
        mountPath: /home/jenkins/.kube
      - name: workspace-volume
        mountPath: /home/jenkins/agent

  volumes:
  - name: workspace-volume
    emptyDir: {}
  - name: docker-graph
    emptyDir: {}
  - name: kubeconfig
    configMap:
      name: jenkins-kubeconfig
      items:
        - key: config
          path: config
'''
        }
    }

    environment {
        DOCKER_IMAGE = 'docker.io/helentam93/k8s-app:latest'
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
                        credentialsId: 'dockerhub-creds',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )]) {
                        sh """
                        echo "Waiting for Docker daemon..."
                        until docker info >/dev/null 2>&1; do
                            sleep 2
                        done
                        echo "Logging into Docker Hub..."
                        echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                        echo "Building image..."
                        docker build -t ${DOCKER_IMAGE} .
                        echo "Pushing image..."
                        docker push ${DOCKER_IMAGE}
                        """
                    }
                }
            }
        }

        stage('Test') {
            steps {
                container('kubectl') {
                    sh 'kubectl version --client'
                    sh 'ls -R k8s/prod'
                }
            }
        }

        stage('Deploy to prod namespace') {
            steps {
                container('kubectl') {
                    sh '''
                    kubectl apply -f k8s/prod/app-deployment.yaml -n ${env.PROD_NAMESPACE}
                    kubectl apply -f k8s/prod/app-service.yaml -n ${env.PROD_NAMESPACE}
                    '''
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