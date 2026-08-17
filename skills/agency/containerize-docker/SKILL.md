---
name: containerize-docker
description: Generate production-ready Dockerfiles and docker-compose.yml for React, Flask, or full-stack projects. Multi-stage builds, non-root users, health checks, and dev/prod configs. Use after scaffolding a website to containerize it for deployment.
license: MIT
metadata:
  author: ai-agency
  category: devops
  version: "1.0.0"
governance_phases: [build, ship]
organ_affinity: [organ-iii]
triggers: [user-asks-about-docker, user-asks-about-container, context:containerization]
complements: [scaffold-react-app, deployment-cicd, docker-containerization]
inputs: [project_type, project_name, port, services]
outputs: [Dockerfile, docker-compose.yml, .dockerignore]
tier: core
---

# Containerize Docker

Generate production-ready Docker configurations for client websites.

## Quick Start

```bash
# React frontend only
python3 skills/agency/containerize-docker/scripts/generate.py \
    --type react --name "my-site" --port 3000 --output .

# Flask backend only
python3 skills/agency/containerize-docker/scripts/generate.py \
    --type flask --name "api" --port 5001 --output .

# Full-stack (React + Flask + PostgreSQL)
python3 skills/agency/containerize-docker/scripts/generate.py \
    --type fullstack --name "my-app" --output .
```

## What Gets Generated

### React project
```
├── Dockerfile            # Multi-stage: build → nginx serve
├── docker-compose.yml    # Single service
├── .dockerignore
└── nginx.conf            # SPA routing config
```

### Flask project
```
├── Dockerfile            # Multi-stage: build → gunicorn
├── docker-compose.yml    # Single service
└── .dockerignore
```

### Full-stack
```
├── Dockerfile.frontend   # React build
├── Dockerfile.backend    # Flask/gunicorn
├── docker-compose.yml    # frontend + backend + postgres + redis
├── .dockerignore
└── nginx.conf            # Reverse proxy config
```

## Generated Files Detail

### React Dockerfile (multi-stage)
- **Stage 1 (build):** node:20-alpine, npm ci, npm run build
- **Stage 2 (serve):** nginx:alpine, copies dist/, serves on port 80
- Non-root user, gzip, caching headers, SPA fallback

### Flask Dockerfile (multi-stage)
- **Stage 1 (build):** python:3.12-slim, pip install
- **Stage 2 (runtime):** python:3.12-slim, gunicorn
- Non-root user, health check, .env support

### docker-compose.yml
- Health checks on all services
- Named volumes for persistence
- Environment variable configuration
- Network isolation

## Usage in Website Generation Workflow

1. Scaffold project with `scaffold-react-app`
2. Build pages with `create-component`
3. Containerize with this skill
4. Deploy with `deployment-cicd` patterns
