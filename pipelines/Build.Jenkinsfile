pipeline {
    agent {
        label 'general'
    }

    environment {
        // Update these for your registry (or override in the Jenkins job UI).
        DOCKER_REGISTRY_HOST = 'docker.io'
        DOCKER_IMAGE_NAME = 'majedsaade/xo-game'
        DOCKER_CREDENTIALS_ID = 'dockerhub-registry-Credentials'

        CONTAINER_NAME = 'xo-game'
        HOST_PORT = '5000'
        IMAGE_TAG = "${env.BUILD_NUMBER}"
    }

    triggers {
        githubPush()
    }

    stages {
        stage('Test') {
            steps {
                sh '''
                    docker run --rm \
                        -v "$PWD:/workspace" \
                        -w /workspace \
                        python:3.11-slim \
                        sh -c "pip install --quiet -r requirements.txt && PYTHONPATH=. pytest"
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
        always {
            sh '''
                docker logout "$DOCKER_REGISTRY_HOST" 2>/dev/null || true
                docker image prune -f --filter "dangling=true" || true
            '''
            cleanWs()
        }
    }
}
