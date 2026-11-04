# devops-lab-2

Rishav | Roll no. 2301730245

DevOps and Automation — Lab 2: Docker and Kubernetes.

This lab packages the Flask app in a Docker image. Compose runs it with Redis,
and the Kubernetes manifests run two app replicas with health probes.

**Run with Docker**

```bash
docker compose -f docker/docker-compose.yml up -d --build --wait
curl http://localhost:5002/
curl http://localhost:5002/visits
docker compose -f docker/docker-compose.yml down
```

The visit counter is stored in a Redis volume. Stopping and recreating the
containers keeps the count; `down -v` removes that data.

**Run on Minikube**

```bash
minikube start
docker build -f docker/Dockerfile -t devops-lab2-app:2.0.0 .
minikube image load devops-lab2-app:2.0.0
kubectl apply -f k8s/
kubectl rollout status deployment/lab2-app
kubectl port-forward service/lab2-app-service 5002:5000
```

Redis is part of the Compose exercise. The Kubernetes app provides `/` and
`/health`; `/visits` returns 503 when no Redis URL is configured.

**Tests and pipeline**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python -m pytest tests/ -v
```

The Jenkinsfile tests and builds the image. Enable `DEPLOY` after adding the
registry credential and cluster access described in [docs/lab-record.md](docs/lab-record.md).
GitHub Actions runs tests and builds the Docker image on each push.

The same manifests also work with kind. Create a cluster named `rishav-devops`
and choose `DEPLOY_TARGET=kind` in Jenkins to load the image locally, without
a registry push. The agent needs kind, Docker and a kubeconfig for that cluster.
