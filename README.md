## Overview
This project features an automated CI/CD pipeline using Harness Free Tier, deploying a Python-based Kubernetes controller to a local Minikube cluster. The pipeline implements a "Shift Left" security strategy and ensures environment consistency through immutable versioning.

---

## Pipeline Flow
1. **Build Stage (CI):**
    * **Git Clone:** Pulls source code from GitHub.
    * **Shift Left Security:** Performs SAST (Static Analysis) and SCA (Software Composition Analysis) on source code and dependencies *prior* to the build.
    * **Docker Build & Push:** Builds the image tagged with a unique `<+pipeline.sequenceId>` and pushes to DockerHub.
    * **Container Scanning:** Aqua Trivy scans the final image for vulnerabilities.
    * **Security Gate:** Pipeline terminates if any CRITICAL vulnerabilities are detected in any scan phase.
2. **Deploy Stage (Dev & Prod):**
    * **Manifest-driven Deployment:** Deploys to `dev-ns` and `prod-ns` using Go-template manifests (`{{ .Values }}`).
    * **Environment Mapping:** Utilizes a `values.yaml` file in GitHub to dynamically map Harness infrastructure variables to Kubernetes resources.
3. **Validation:**
    * Automated shell script verifies the `/health` endpoint via the Ingress path to ensure the application is reachable and functional.

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