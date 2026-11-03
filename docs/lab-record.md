# Lab 2 record

Name: Rishav

Roll no.: 2301730245

**1. Containerize the app**

```bash
docker build -f docker/Dockerfile -t devops-lab2-app:2.0.0 .
docker run -d --name rishav-lab2-demo -p 127.0.0.1:5002:5000 devops-lab2-app:2.0.0
curl --fail http://localhost:5002/health
docker history devops-lab2-app:2.0.0
docker logs rishav-lab2-demo
docker exec rishav-lab2-demo id
```

Dependencies are copied before the source so Docker can reuse that layer after
a code change. The image runs Gunicorn as an unprivileged user. `.dockerignore`
is at the repository root, which is the build context.

**2. Containers, images and Compose**

```bash
docker stop rishav-lab2-demo
docker start rishav-lab2-demo
docker rm -f rishav-lab2-demo
docker compose -f docker/docker-compose.yml up -d --build
docker compose -f docker/docker-compose.yml ps
curl --fail http://localhost:5002/visits
```

The `web` and `redis` services share a network. The app connects using the service
name `redis`. Stop the standalone container before starting Compose on the same port.

To publish an image to Docker Hub, replace `YOUR_DOCKERHUB_ID` with your account:

```bash
docker login
docker tag devops-lab2-app:2.0.0 YOUR_DOCKERHUB_ID/devops-lab2-app:2.0.0
docker push YOUR_DOCKERHUB_ID/devops-lab2-app:2.0.0
```

**3. Storage**

Call `/visits` a few times, run `docker compose -f docker/docker-compose.yml down`,
then start the stack again. Redis uses append-only persistence on the `visits`
volume, so the counter survives container recreation.

These commands compare a container's writable layer and a bind mount:

```bash
docker run --name lab2-layer alpine sh -c 'echo temporary > /note.txt'
docker cp lab2-layer:/note.txt ./note.txt
docker rm lab2-layer
docker run --rm alpine sh -c 'test ! -f /note.txt'
mkdir -p storage-demo
docker run --rm -v "$PWD/storage-demo:/data" alpine sh -c 'echo persistent > /data/note.txt'
cat storage-demo/note.txt
```

**4. Networking**

```bash
docker network create lab2-network-demo
docker run -d --name lab2-peer --network lab2-network-demo alpine sleep 300
docker run --rm --network lab2-network-demo alpine ping -c 2 lab2-peer
docker rm -f lab2-peer
docker network rm lab2-network-demo
```

A user-created bridge provides container-name DNS. Compose creates its own bridge
and registers service names on it; Redis does not need a published host port.

**5. Kubernetes**

Follow the Minikube commands in the README. The ConfigMap supplies the message;
the Deployment maintains two replicas; the NodePort Service routes requests to
ready pods. Use port forwarding to access it consistently across host platforms.

```bash
kubectl get pods,deployments,services
kubectl describe deployment lab2-app
```

**6. Updates, rollback and scaling**

Keep the initial port-forward terminal open, and run these in another terminal:

```bash
docker build --build-arg APP_VERSION=2.0.1 -f docker/Dockerfile -t devops-lab2-app:2.0.1 .
minikube image load devops-lab2-app:2.0.1
kubectl set image deployment/lab2-app lab2-app=devops-lab2-app:2.0.1
kubectl rollout status deployment/lab2-app
curl --fail http://localhost:5002/health
kubectl rollout history deployment/lab2-app
kubectl rollout undo deployment/lab2-app
kubectl rollout status deployment/lab2-app
kubectl scale deployment/lab2-app --replicas=4
kubectl get pods
kubectl scale deployment/lab2-app --replicas=2
```

The rolling update allows one extra pod and keeps both existing replicas available
until replacements pass readiness checks. Version is baked into the image so a
rollback also restores the reported version.

**7. Continuous deployment**

Create a Jenkins Pipeline job using this repository's `Jenkinsfile`. The agent
needs Python, Docker and kubectl. Configure cluster access for the Jenkins user.
Add a username/password credential named `github-packages`: username
`Rishav23av`, password a GitHub token with package write access. Enable `DEPLOY`
when the job is ready to publish. Make the GHCR package public after the first
push or configure a Kubernetes image pull secret for a private package.

Each build gets a separate image tag. The deployment stage renders that tag into
the manifest before applying it, then waits for the rollout. The default build
only tests and builds the image.

**8–9. Record and explanation**

The files demonstrate image layers, container lifecycle, persistent storage,
service discovery, orchestration and continuous deployment. Docker manages the
individual containers; Kubernetes reconciles replicas and updates. The source
includes commands to repeat each exercise. A local Kubernetes rollout or Jenkins
deployment must be run against a configured cluster and agent.

Cleanup for this lab:

```bash
docker compose -f docker/docker-compose.yml down
kubectl delete -f k8s/
```
