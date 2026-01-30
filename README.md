# Ledger App

Ledger App is a minimal transactional ledger service built as a **reference portfolio project** to demonstrate an end‑to‑end CI/CD workflow on Kubernetes. The focus of the project is not business complexity, but **clean separation of concerns**, **reproducible builds**, and **production‑grade delivery practices** using Jenkins, Helm, ArgoCD, and container security tooling.

The application consists of a small Python web service backed by a SQL database. It supports basic CRUD operations and is intentionally kept simple so the infrastructure and pipeline design remain the primary point of interest.

<img width="1140" height="311" alt="image" src="https://github.com/user-attachments/assets/818d81d7-6be7-406d-89cf-d750162c0a9d" />

## Directory Layout

assets/        Runtime artifacts
cicd/          Build & deploy logic
cloudformation Infrastructure as Code
services/      Application source

---

## High‑Level Architecture

* **Web Service**: Python Flask application providing CRUD endpoints and HTML views
* **Database**: SQL server initialized via Kubernetes Job
* **Containerization**: Separate images for web and SQL components
* **CI**: Jenkins running on Kubernetes
* **CD**: ArgoCD with Helm charts
* **Security & Quality**: Unit/integration tests, Bandit, Trivy

```
Developer -> GitHub -> Jenkins (CI) -> Container Registry -> GitHub (Helm values) -> ArgoCD -> Kubernetes
```

<img width="4142" height="1917" alt="cicd-diagram" src="https://github.com/user-attachments/assets/0578e6a7-eda7-4735-a6f7-ef7e53eeafd1" />

<img width="2943" height="1237" alt="kubernetes-diagram" src="https://github.com/user-attachments/assets/f02e9f1d-7506-4b2b-8dc5-6a19cccc77bf" />

---

## Repository Structure

```
.
├── charts/                 # Helm chart for Kubernetes deployment
│   ├── templates/          # Deployments and Jobs
│   ├── values-dev.yaml     # Dev environment values
│   └── values-prod.yaml    # Prod environment values
├── compose/                # Local development setup
│   └── docker-compose.yml
├── Jenkinsfile             # CI pipeline definition
├── sql/                    # SQL image and initialization
│   ├── Dockerfile
│   └── init.sql
└── web/                    # Web application
    ├── app/                # Application source
    ├── tests/              # Python unittest suite
    ├── Dockerfile          # Production image (tests excluded)
    └── requirements.txt
```

---

## Application Design Notes

* Tests live under `web/tests` and are **not included** in the runtime image
* The production image only contains what is required to run the service
* Database credentials are injected via Kubernetes Secrets
* SQL schema is initialized through a Kubernetes Job

---

## CI Pipeline (Jenkins)

The Jenkins pipeline is designed to be **branch‑aware** and **Kubernetes‑native**.

### Environment Resolution

```groovy
def APP_NAME = "ledger-app-${env.BRANCH_NAME == 'main' ? 'prod' : env.BRANCH_NAME}"
```

* `main` branch maps to **prod**
* Any other branch maps to its own environment name
* Image names and Helm values are derived from this logic

---

### Jenkins Agent Model

The pipeline runs entirely on Kubernetes using ephemeral Pods with multiple containers:

* **ledger-app-web-codeless**: Executes tests
* **ledger-app-sql-test**: Provides a SQL backend for integration tests
* **bandit**: Static security analysis for Python code
* **kaniko**: Container image builder (Dockerless)
* **trivy**: Container image vulnerability scanner

This design avoids privileged containers and keeps each responsibility isolated.

---

### Pipeline Stages Overview

#### 1. Init

* Resolves runtime environment (dev / prod)
* Constructs registry image names

#### 2. Checkout

* Pulls source code from GitHub

#### 3. Integration Tests

* Runs Python `unittest` suite
* Executes full CRUD flows against a real SQL service
* Ensures database connectivity and schema correctness

```bash
python -m unittest discover -s tests -t .
```

#### 4. Bandit

* Static analysis of Python source
* Fails pipeline on high‑severity findings

```bash
bandit -r . -lll
```

#### 5. Build Image (Kaniko)

* Builds the production web image
* Pushes versioned and `latest` tags
* Does not require Docker daemon

#### 6. Trivy Image Scan

* Scans the built image for HIGH and CRITICAL vulnerabilities
* Pipeline fails if thresholds are exceeded

#### 7. Update Helm Values

* Automatically updates the image tag in the corresponding Helm values file
* Commits and pushes the change back to GitHub
* This acts as the **handoff point** to CD

---

## Continuous Delivery (ArgoCD)

* ArgoCD monitors the Helm chart repository
* Any change to `values-dev.yaml` or `values-prod.yaml` triggers a sync
* Kubernetes manifests are applied declaratively
* No direct `kubectl apply` is performed from CI

This enforces a clean **CI / CD separation**:

* Jenkins: build, test, scan, publish
* ArgoCD: deploy and reconcile

---

## Local Development

For local testing and iteration, Docker Compose is provided:

```bash
docker-compose up --build
```

This setup mirrors the production topology closely enough to validate behavior before pushing changes.

---

## Secrets & Configuration

* Kubernetes Secrets are created **out of band** using `kubectl`
* No external secret manager (Vault, SSM, etc.) is used in this project
* TLS certificates and database credentials must exist before deployment

This choice is intentional to keep the project focused on CI/CD mechanics rather than secret backends.

---

## Purpose of This Project

This repository is intentionally designed as a **showcase project**:

* Demonstrates real‑world CI/CD patterns
* Uses production‑grade tools and workflows
* Keeps application logic simple and auditable
* Emphasizes reproducibility, security, and clarity

It is not a framework or a product, but a **reference implementation** for Kubernetes‑based delivery pipelines.
