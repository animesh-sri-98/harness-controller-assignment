## Overview

This project demonstrates an end-to-end CI/CD pipeline using Harness Free Tier with integrated security testing and deployment to a local Kubernetes cluster (Minikube).

The application is a Python-based Kubernetes controller that watches Deployment resources and automatically creates or deletes corresponding Services. It also exposes a `/health` endpoint for post-deployment validation.

---

## Controller Summary

### Functionality

* Watches Kubernetes Deployments in the `default` namespace
* Detects `ADDED` and `DELETED` events
* Creates a `LoadBalancer` Service when a Deployment is added
* Deletes the Service when a Deployment is removed
* Provides a `/health` endpoint for validation

### Health Endpoint

```text
GET /health
```

Response:

```json
{"status":"healthy"}
```

---

## Pipeline Flow

```text
GitHub
  ↓
Harness Trigger
  ↓
CI Stage
- Clone Repository
- Build Docker Image
- Push Image to DockerHub
- Trivy Container Scan
- Fail Pipeline on CRITICAL Vulnerabilities
  ↓
CD Stage
- Deploy to Kubernetes (Deployment + Service + Ingress + RBAC)
  ↓
Post Deployment Validation
- Port Forward Service
- Call /health
- Validate Healthy Response
```

---

## CI Stage

### Steps

1. Clone code from GitHub
2. Build Docker image using Dockerfile
3. Tag image (`latest`)
4. Push image to DockerHub
5. Vulnerability scanning with Aqua Trivy

Docker Image:

```text
animeshsri98/controller-watcher
```

---

### Security Gate

Pipeline fails if any **CRITICAL** vulnerabilities are detected.

This ensures vulnerable images are blocked before deployment.

---

## CD Stage

### Deployment Method

Harness Kubernetes Deployment using manifests.

### Resources Deployed

* Deployment
* Service
* Ingress
* RBAC

### Namespace

```text
dev-ns
```

### Strategy

Rolling deployment for safe updates without downtime.

---

## Post-Deployment Validation

After deployment, Harness runs a Shell Script step:

```bash
kubectl port-forward svc/controller-service 5000:5000 -n dev-ns &
sleep 10
curl http://localhost:5000/health
```

Expected response:

```json
{"status":"healthy"}
```

If the health check fails, the pipeline fails.

This ensures deployment success means the application is actually reachable and healthy.

---

## Local Verification

```bash
kubectl port-forward svc/controller-service 5000:5000 -n dev-ns
```

Then:

```bash
curl http://localhost:5000/health
```

Expected:

```json
{"status":"healthy"}
```

---

## Key Highlights

* CI builds and pushes the Docker image
* STO enforces security gating using Trivy
* CD performs rolling deployment to Kubernetes
* Post-deployment validation confirms application health
* Ingress + Service provide application access
* RBAC enables Kubernetes API access for the controller
