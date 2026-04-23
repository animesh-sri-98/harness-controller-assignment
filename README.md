## Overview
This project features an automated CI/CD pipeline using **Harness Free Tier**, deploying a Python-based Kubernetes controller to a local **Minikube** cluster. The pipeline transitions from security-gated builds to multi-environment deployments using immutable versioning.

---

## Pipeline Flow
1. **Build Stage:**
    * Builds Docker image tagged with unique `<+pipeline.sequenceId>`.
    * Pushes to DockerHub: `animeshsri98/controller-watcher:<tag>`.
    * **Security Gate:** Aqua Trivy scan fails the pipeline on **CRITICAL** vulnerabilities.
2. **Deploy Stage (Dev & Prod):**
    * Deploys to `dev-ns` and `prod-ns` using Go-template manifests (`{{ .Values }}`).
    * Manages environment-specific settings via Harness **Service Overrides**.
3. **Validation:**
    * Automated shell script verifies the `/health` endpoint via the Ingress path.

---

## Environment Configuration
| Feature | Development | Production |
| :--- | :--- | :--- |
| **Namespace** | `dev-ns` | `prod-ns` |
| **Ingress Host** | `Development.controller.local` | `Production.controller.local` |
| **Image Tag** | Immutable Build ID | Same Immutable Build ID |

---

## Post-Deployment Health Check
The pipeline validates the deployment by hitting the Ingress controller:

```bash
# Executed within Harness Stage
curl -H "Host: <+env.name>.controller.local" http://<MINIKUBE_IP>/health
```

**Expected Response:** ```json
{"status":"healthy"}
```