pipeline {
    agent {
        kubernetes {
            yaml """
apiVersion: v1
kind: Pod
metadata:
  labels:
    app: cicd-pipeline
spec:
  containers:
  - name: node
    image: node:18-alpine
    command:
    - cat
    tty: true
  - name: python
    image: python:3.10-slim
    command:
    - cat
    tty: true
  - name: docker
    image: docker:20.10.16-dind
    command:
    - cat
    tty: true
    volumeMounts:
    - name: docker-socket
      mountPath: /var/run/docker.sock
  - name: terraform
    image: hashicorp/terraform:1.3.0
    command:
    - cat
    tty: true
  volumes:
  - name: docker-socket
    hostPath:
      path: /var/run/docker.sock
"""
        }
    }
    
    environment {
        DOCKER_REGISTRY = credentials('docker-registry')
        AWS_CREDENTIALS = credentials('aws-credentials')
        SONAR_TOKEN = credentials('sonar-token')
        SLACK_WEBHOOK = credentials('slack-webhook')
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Parallel: Code Quality & Security') {
            parallel {
                stage('Code Quality') {
                    steps {
                        container('node') {
                            dir('src/frontend') {
                                sh 'npm ci'
                                sh 'npm run lint'
                                sh 'npm run test:unit -- --coverage'
                            }
                        }
                        
                        container('python') {
                            dir('src/backend') {
                                sh 'pip install -r requirements.txt'
                                sh 'pylint --rcfile=../../.pylintrc src tests'
                                sh 'pytest tests/unit --cov=src --cov-report=xml'
                            }
                        }
                        
                        withSonarQubeEnv('SonarQube') {
                            sh 'sonar-scanner -Dsonar.projectKey=advanced-cicd -Dsonar.sources=src'
                        }
                        
                        timeout(time: 10, unit: 'MINUTES') {
                            waitForQualityGate abortPipeline: true
                        }
                    }
                    post {
                        always {
                            junit '**/test-results.xml'
                            publishCoverage adapters: [
                                istanbulCoberturaAdapter('src/backend/coverage.xml'),
                                istanbulCoberturaAdapter('src/frontend/coverage/cobertura-coverage.xml')
                            ]
                        }
                    }
                }
                
                stage('Security Scan') {
                    steps {
                        container('node') {
                            sh 'npm install -g snyk'
                            sh 'snyk test --severity-threshold=high || true'
                        }
                        
                        container('python') {
                            sh 'pip install safety'
                            sh 'safety check -r src/backend/requirements.txt || true'
                        }
                        
                        dependencyCheck additionalArguments: '--scan . --suppression suppression.xml --failOnCVSS 7', odcInstallation: 'OWASP-Dependency-Check'
                    }
                    post {
                        always {
                            dependencyCheckPublisher pattern: 'dependency-check-report.xml'
                        }
                    }
                }
            }
        }
        
        stage('Build & Push Images') {
            steps {
                container('docker') {
                    sh 'echo $DOCKER_REGISTRY_PSW | docker login -u $DOCKER_REGISTRY_USR --password-stdin'
                    
                    dir('src/backend') {
                        sh """
                        docker build -t $DOCKER_REGISTRY_USR/cicd-backend:${env.BUILD_NUMBER} .
                        docker push $DOCKER_REGISTRY_USR/cicd-backend:${env.BUILD_NUMBER}
                        """
                    }
                    
                    dir('src/frontend') {
                        sh """
                        docker build -t $DOCKER_REGISTRY_USR/cicd-frontend:${env.BUILD_NUMBER} .
                        docker push $DOCKER_REGISTRY_USR/cicd-frontend:${env.BUILD_NUMBER}
                        """
                    }
                }
            }
        }
        
        stage('Deploy to Staging') {
            steps {
                container('terraform') {
                    dir('infrastructure/terraform') {
                        sh """
                        export AWS_ACCESS_KEY_ID=$AWS_CREDENTIALS_USR
                        export AWS_SECRET_ACCESS_KEY=$AWS_CREDENTIALS_PSW
                        terraform init
                        terraform workspace select staging || terraform workspace new staging
                        terraform apply -auto-approve -var="image_tag=${env.BUILD_NUMBER}"
                        """
                    }
                }
                
                sh """
                curl -X POST -H 'Content-type: application/json' --data '{"text":"Deployment to staging completed for build ${env.BUILD_NUMBER}"}' $SLACK_WEBHOOK
                """
            }
        }
        
        stage('Parallel: Integration & E2E Tests') {
            parallel {
                stage('Integration Tests') {
                    steps {
                        container('python') {
                            dir('tests/integration') {
                                sh 'pip install -r requirements.txt'
                                sh 'pytest --base-url=https://staging.example.com'
                            }
                        }
                    }
                    post {
                        always {
                            junit 'tests/integration/reports/*.xml'
                        }
                    }
                }
                
                stage('E2E Tests') {
                    steps {
                        container('node') {
                            dir('tests/e2e') {
                                sh 'npm ci'
                                sh 'npx cypress run --config baseUrl=https://staging.example.com'
                            }
                        }
                    }
                    post {
                        always {
                            archiveArtifacts artifacts: 'tests/e2e/cypress/videos/**', allowEmptyArchive: true
                        }
                    }
                }
                
                stage('Performance Tests') {
                    steps {
                        container('node') {
                            dir('tests/performance') {
                                sh 'npm install -g k6'
                                sh 'k6 run load-test.js -e URL=https://staging.example.com'
                            }
                        }
                    }
                    post {
                        always {
                            archiveArtifacts artifacts: 'tests/performance/results/**', allowEmptyArchive: true
                        }
                    }
                }
            }
        }
        
        stage('Deploy to Production') {
            when {
                branch 'main'
            }
            steps {
                input message: 'Deploy to production?', ok: 'Deploy'
                
                container('terraform') {
                    dir('infrastructure/terraform') {
                        sh """
                        export AWS_ACCESS_KEY_ID=$AWS_CREDENTIALS_USR
                        export AWS_SECRET_ACCESS_KEY=$AWS_CREDENTIALS_PSW
                        terraform init
                        terraform workspace select production || terraform workspace new production
                        terraform apply -auto-approve -var="image_tag=${env.BUILD_NUMBER}" -var="deployment_percentage=20"
                        """
                    }
                }
                
                sh """
                curl -X POST -H 'Content-type: application/json' --data '{"text":"Canary deployment to production started for build ${env.BUILD_NUMBER}"}' $SLACK_WEBHOOK
                """
                
                timeout(time: 30, unit: 'MINUTES') {
                    script {
                        def canarySuccess = false
                        try {
                            sh 'cd scripts && ./monitor-canary.sh'
                            canarySuccess = true
                        } catch (Exception e) {
                            sh """
                            curl -X POST -H 'Content-type: application/json' --data '{"text":"Canary deployment failed, rolling back build ${env.BUILD_NUMBER}"}' $SLACK_WEBHOOK
                            """
                            error "Canary deployment failed: ${e.message}"
                        }
                        
                        if (canarySuccess) {
                            container('terraform') {
                                dir('infrastructure/terraform') {
                                    sh """
                                    export AWS_ACCESS_KEY_ID=$AWS_CREDENTIALS_USR
                                    export AWS_SECRET_ACCESS_KEY=$AWS_CREDENTIALS_PSW
                                    terraform apply -auto-approve -var="image_tag=${env.BUILD_NUMBER}" -var="deployment_percentage=100"
                                    """
                                }
                            }
                            
                            sh """
                            curl -X POST -H 'Content-type: application/json' --data '{"text":"Deployment to production completed for build ${env.BUILD_NUMBER}"}' $SLACK_WEBHOOK
                            """
                        }
                    }
                }
            }
        }
    }
    
    post {
        always {
            archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true
        }
        success {
            sh """
            curl -X POST -H 'Content-type: application/json' --data '{"text":"Pipeline succeeded for build ${env.BUILD_NUMBER}"}' $SLACK_WEBHOOK
            """
        }
        failure {
            sh """
            curl -X POST -H 'Content-type: application/json' --data '{"text":"Pipeline failed for build ${env.BUILD_NUMBER}"}' $SLACK_WEBHOOK
            """
        }
    }
} 