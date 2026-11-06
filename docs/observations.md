# Lab 2 observations

Rishav | Roll no. 2301730245

- The image ran as appuser with UID 10001. Redis was reachable through its Compose service name.
- Compose needed an application health check and `--wait` before the next curl command.
- Redis kept the same counter value after both containers were removed and recreated without deleting the volume.
- An image push to the local registry succeeded. Docker Hub and GHCR commands are provided for an account with credentials.
- Jenkins build 2 loaded its tagged image into kind and completed the deployment with two ready replicas.
- Scaling produced four pods. The rolling update served version 2.0.3, and rollback restored 2.0.2.
- The manifests were exercised with kind on Docker Desktop; Minikube instructions remain in the README.

See [screenshots](screenshots/README.md), [command output](commands/) and [reports](../reports/README.md).
