## Overview
This project features an automated CI/CD pipeline using Harness Free Tier, deploying a Python-based Kubernetes controller to a local Minikube cluster. The pipeline transitions from security-gated builds to multi-environment deployments using immutable versioning and a "Shift Left" security approach.

---

## Pipeline Flow
1. **Build Stage (CI):**
    * **Git Clone:** Pulls source code from GitHub.
    * **Shift Left Security:** Performs **SAST** (Static Analysis) and **SCA** (Software Composition Analysis) scans in parallel on source code and dependencies before the build.
    * **Docker Build & Push:** Builds image tagged with unique `<+pipeline.sequenceId>` and pushes to DockerHub.
    * **Container Scanning:** Aqua Trivy scans the final image.
    * **Security Gate:** Pipeline fails on any **CRITICAL** vulnerabilities found in any scan phase.
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
| **Ingress Host** | `harnessdevenv.controller.local` | `harnessprodenv.controller.local` |
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