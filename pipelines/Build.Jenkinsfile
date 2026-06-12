def sendBuildEmail(String status) {
    withCredentials([
        string(credentialsId: 'EmailToSend', variable: 'NOTIFY_TO'),
        usernamePassword(
            credentialsId: 'smtp-credentials',
            usernameVariable: 'SMTP_USER',
            passwordVariable: 'SMTP_PASSWORD'
        )
    ]) {
        sh """
            docker run --rm -i \\
                -e NOTIFY_TO \\
                -e SMTP_USER \\
                -e SMTP_PASSWORD \\
                -e SMTP_HOST=\${SMTP_HOST} \\
                -e SMTP_PORT=\${SMTP_PORT} \\
                -e BUILD_STATUS=${status} \\
                -e JOB_NAME=\${JOB_NAME} \\
                -e BUILD_NUMBER=\${BUILD_NUMBER} \\
                -e BUILD_URL=\${BUILD_URL} \\
                -e DOCKER_IMAGE_NAME=\${DOCKER_IMAGE_NAME} \\
                python:3.11-slim python - < notify.py
        """
    }
}

pipeline {
    agent {
        label 'general'
    }

    environment {
        DOCKER_REGISTRY_HOST = 'docker.io'
        DOCKER_IMAGE_NAME = 'majedsaade/xo-game'
        DOCKER_CREDENTIALS_ID = 'dockerhub-registry-Credentials'

        CONTAINER_NAME = 'xo-game'
        HOST_PORT = '5000'
        IMAGE_TAG = "${env.BUILD_NUMBER}"

        SMTP_HOST = 'smtp.gmail.com'
        SMTP_PORT = '587'
    }

    triggers {
        githubPush()
    }

    stages {
        stage('Test') {
            steps {
                sh '''
                    mkdir -p reports
                    docker build --target builder -t xo-game-test .
                    cid=$(docker create xo-game-test)
                    docker cp "$cid:/build/reports/." reports/
                    docker rm "$cid"
                '''
            }
        }

        stage('Security Scan') {
            steps {
                sh '''
                    mkdir -p reports
                    docker build -t xo-game-scan .
                    docker run --rm \
                        -v /var/run/docker.sock:/var/run/docker.sock \
                        -v "$PWD/reports:/reports" \
                        aquasec/trivy:latest image \
                        --format table \
                        --output /reports/trivy-report.txt \
                        xo-game-scan
                '''
            }
        }

        stage('Build and Push') {
            steps {
                script {
                    env.FULL_IMAGE = "${DOCKER_IMAGE_NAME}:${IMAGE_TAG}"
                    env.FULL_IMAGE_LATEST = "${DOCKER_IMAGE_NAME}:latest"
                }
                withCredentials([
                    usernamePassword(
                        credentialsId: "${DOCKER_CREDENTIALS_ID}",
                        usernameVariable: 'DOCKER_USERNAME',
                        passwordVariable: 'DOCKER_PASSWORD'
                    )
                ]) {
                    sh '''
                        echo "$DOCKER_PASSWORD" | docker login "$DOCKER_REGISTRY_HOST" \
                            -u "$DOCKER_USERNAME" --password-stdin

                        docker build -t "$FULL_IMAGE" -t "$FULL_IMAGE_LATEST" .
                        docker push "$FULL_IMAGE"
                        docker push "$FULL_IMAGE_LATEST"
                    '''
                }
            }
        }

        stage('Deploy') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: "${DOCKER_CREDENTIALS_ID}",
                        usernameVariable: 'DOCKER_USERNAME',
                        passwordVariable: 'DOCKER_PASSWORD'
                    )
                ]) {
                    sh '''
                        chmod +x deploy.sh
                        DOCKER_REGISTRY_HOST="$DOCKER_REGISTRY_HOST" \
                        DOCKER_USERNAME="$DOCKER_USERNAME" \
                        DOCKER_PASSWORD="$DOCKER_PASSWORD" \
                        IMAGE_NAME="$FULL_IMAGE_LATEST" \
                        CONTAINER_NAME="$CONTAINER_NAME" \
                        HOST_PORT="$HOST_PORT" \
                        ./deploy.sh
                    '''
                }
            }
        }
    }

    post {
        success {
            script {
                sendBuildEmail('SUCCESS')
            }
        }
        failure {
            script {
                sendBuildEmail('FAILURE')
            }
        }
        always {
            junit testResults: 'reports/junit-report.xml', allowEmptyResults: true
            archiveArtifacts artifacts: 'reports/**/*', allowEmptyArchive: true
            sh '''
                docker logout "$DOCKER_REGISTRY_HOST" 2>/dev/null || true
                docker image prune -f --filter "dangling=true" || true
            '''
        }
        cleanup {
            cleanWs()
        }
    }
}
