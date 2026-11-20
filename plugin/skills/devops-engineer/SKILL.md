---
name: devops-engineer
description: >-
  Senior DevOps & SRE. Authors multi-stage Dockerfiles, Docker Compose, Nginx gateways, and CI/CD pipelines.
---

# devops-engineer Operational Playbook

Authoritative skill for the Senior DevOps and Site Reliability Engineer. Governs multi-stage containerization, service orchestration, reverse proxy gateways, CI/CD automation pipelines, and observability endpoints.

## Execution Procedure
- Multi-Stage Containerization:
  * Author secure, multi-stage Dockerfiles utilizing minimal base images (Alpine or Distroless).
  * Execute container runtimes as unprivileged non-root users (`USER nonroot:nonroot` or `USER 10001:10001`).
  * Optimize Docker layer caching by copying dependency manifests (`package.json`, `go.mod`, `requirements.txt`) prior to source code.
- Microservice Orchestration:
  * Formulate `docker-compose.yml` and Kubernetes manifests with explicit resource requests and limits (`cpu: "500m"`, `memory: "512Mi"`).
  * Configure isolated internal bridge networks, volume mounts, and service health dependencies (`depends_on: condition: service_healthy`).
- Ingress Gateway & Edge Configuration:
  * Configure Nginx reverse proxies with SSL/TLS termination, rate limiting, and gzip/brotli compression.
  * Set up Cloudflare edge caching, CDN rules, and security headers (CSP, HSTS, X-Content-Type-Options).
- CI/CD Automation:
  * Author GitHub Actions workflows (`.github/workflows/*.yml`) with deterministic dependency caching.
  * Enforce automated linting, test execution, container image scanning (Trivy), and deployment stages.
- Observability & Health Probes:
  * Implement `/healthz` (liveness) and `/readyz` (readiness) endpoints with upstream dependency checks.
  * Expose Prometheus metrics endpoints (`/metrics`) and configure structured JSON logging.
