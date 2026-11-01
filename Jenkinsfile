pipeline {
    agent any
    options {
        skipDefaultCheckout(true)
        disableConcurrentBuilds()
    }
    triggers { pollSCM('H/5 * * * *') }
    parameters {
        booleanParam(name: 'DEPLOY', defaultValue: false,
                     description: 'Publish to GHCR and deploy to the configured cluster')
    }
    environment {
        IMAGE_REPO = 'ghcr.io/rishav23av/devops-lab-2'
    }
    stages {
        stage('Checkout') {
            steps { checkout scm }
        }
        stage('Test') {
            steps {
                sh 'python3 -m venv .venv'
                sh '.venv/bin/python -m pip install -r requirements-dev.txt'
                sh 'mkdir -p test-results'
                sh '.venv/bin/python -m pytest tests/ -v --junitxml=test-results/pytest.xml'
            }
            post { always { junit 'test-results/pytest.xml' } }
        }
        stage('Build image') {
            steps {
                sh 'docker build --build-arg APP_VERSION=2.0.${BUILD_NUMBER} -f docker/Dockerfile -t "$IMAGE_REPO:$BUILD_NUMBER" .'
            }
        }
        stage('Publish image') {
            when { expression { params.DEPLOY } }
            steps {
                withCredentials([usernamePassword(credentialsId: 'github-packages',
                                 usernameVariable: 'REGISTRY_USER', passwordVariable: 'REGISTRY_TOKEN')]) {
                    sh '''#!/usr/bin/env bash
set -euo pipefail
export DOCKER_CONFIG="$(mktemp -d)"
trap 'rm -rf "$DOCKER_CONFIG"' EXIT
printf '%s' "$REGISTRY_TOKEN" | docker login ghcr.io -u "$REGISTRY_USER" --password-stdin
docker push "$IMAGE_REPO:$BUILD_NUMBER"
'''
                }
            }
        }
        stage('Deploy') {
            when { expression { params.DEPLOY } }
            steps {
                sh '''#!/usr/bin/env bash
set -euo pipefail
kubectl apply -f k8s/configmap.yaml -f k8s/service.yaml
kubectl set image --local -f k8s/deployment.yaml lab2-app="$IMAGE_REPO:$BUILD_NUMBER" -o yaml > deployment-rendered.yaml
kubectl apply -f deployment-rendered.yaml
kubectl rollout status deployment/lab2-app --timeout=180s
'''
            }
        }
    }
}
