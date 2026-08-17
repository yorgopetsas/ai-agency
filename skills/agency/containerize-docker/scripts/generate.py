#!/usr/bin/env python3
"""
Docker Configuration Generator
===============================
Generates Dockerfiles, docker-compose.yml, and .dockerignore
for React, Flask, or full-stack projects.

Usage:
    python3 generate.py --type react --name "my-site" --port 3000 --output .
    python3 generate.py --type flask --name "api" --port 5001 --output .
    python3 generate.py --type fullstack --name "my-app" --output .
"""

import argparse
import sys
from pathlib import Path


# ── Dockerignore ─────────────────────────────────────────────────────

DOCKERIGNORE = """\
.git
.github
.venv
.env
.env.local
__pycache__
*.pyc
*.pyo
node_modules
dist
build
*.md
tests/
docs/
.coverage
htmlcov/
.pytest_cache/
.mypy_cache/
.DS_Store
"""

# ── React Templates ──────────────────────────────────────────────────

REACT_DOCKERFILE = """\
# Stage 1: Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Serve
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
RUN addgroup -g 1001 appgroup && adduser -u 1001 -G appgroup -s /bin/sh -D appuser
USER appuser
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
"""

REACT_NGINX = """\
server {{
    listen 80;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    # Gzip
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml text/javascript;

    # Cache static assets
    location /assets/ {{
        expires 1y;
        add_header Cache-Control "public, immutable";
    }}

    # SPA fallback
    location / {{
        try_files $uri $uri/ /index.html;
    }}
}}
"""

REACT_COMPOSE = """\
services:
  frontend:
    build: .
    ports:
      - "{port}:80"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:80"]
      interval: 30s
      timeout: 5s
      retries: 3
"""

# ── Flask Templates ──────────────────────────────────────────────────

FLASK_DOCKERFILE = """\
# Stage 1: Build
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Runtime
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /install /usr/local
COPY . .
RUN addgroup --system --gid 1001 appgroup && \\
    adduser --system --uid 1001 appuser --ingroup appgroup
USER appuser
EXPOSE {port}
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \\
  CMD curl -f http://localhost:{port}/health || exit 1
CMD ["gunicorn", "--bind", "0.0.0.0:{port}", "--workers", "4", "app:app"]
"""

FLASK_REQUIREMENTS = """\
flask>=3.0
gunicorn>=22.0
python-dotenv>=1.0
"""

FLASK_COMPOSE = """\
services:
  backend:
    build: .
    ports:
      - "{port}:{port}"
    env_file:
      - .env
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:{port}/health"]
      interval: 30s
      timeout: 5s
      retries: 3
"""

# ── Full-Stack Templates ─────────────────────────────────────────────

FULLSTACK_DOCKERFILE_FRONTEND = """\
# Stage 1: Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# Stage 2: Serve
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
RUN addgroup -g 1001 appgroup && adduser -u 1001 -G appgroup -s /bin/sh -D appuser
USER appuser
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
"""

FULLSTACK_DOCKERFILE_BACKEND = """\
# Stage 1: Build
FROM python:3.12-slim AS builder
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Runtime
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /install /usr/local
COPY backend/ .
RUN addgroup --system --gid 1001 appgroup && \\
    adduser --system --uid 1001 appuser --ingroup appgroup
USER appuser
EXPOSE 5001
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \\
  CMD curl -f http://localhost:5001/health || exit 1
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "4", "app:app"]
"""

FULLSTACK_NGINX = """\
server {{
    listen 80;
    server_name _;

    # Frontend
    location / {{
        proxy_pass http://frontend:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }}

    # Backend API
    location /api/ {{
        proxy_pass http://backend:5001/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}
"""

FULLSTACK_COMPOSE = """\
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      frontend:
        condition: service_started
      backend:
        condition: service_healthy
    restart: unless-stopped

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:80"]
      interval: 30s
      timeout: 5s
      retries: 3

  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    env_file:
      - .env
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/app
      - REDIS_URL=redis://cache:6379
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_started
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5001/health"]
      interval: 30s
      timeout: 5s
      retries: 3
    restart: unless-stopped

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: app
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 10s
      timeout: 5s
      retries: 5

  cache:
    image: redis:7-alpine
    command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru

volumes:
  pgdata:
"""


# ── Generator ────────────────────────────────────────────────────────

def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def generate_react(name: str, port: int, output: Path):
    write_file(output / "Dockerfile", REACT_DOCKERFILE)
    write_file(output / "nginx.conf", REACT_NGINX)
    write_file(output / "docker-compose.yml", REACT_COMPOSE.format(port=port))
    write_file(output / ".dockerignore", DOCKERIGNORE)


def generate_flask(name: str, port: int, output: Path):
    write_file(output / "Dockerfile", FLASK_DOCKERFILE.format(port=port))
    write_file(output / "requirements.txt", FLASK_REQUIREMENTS)
    write_file(output / "docker-compose.yml", FLASK_COMPOSE.format(port=port))
    write_file(output / ".dockerignore", DOCKERIGNORE)


def generate_fullstack(name: str, port: int, output: Path):
    write_file(output / "Dockerfile.frontend", FULLSTACK_DOCKERFILE_FRONTEND)
    write_file(output / "Dockerfile.backend", FULLSTACK_DOCKERFILE_BACKEND)
    write_file(output / "nginx.conf", FULLSTACK_NGINX)
    write_file(output / "docker-compose.yml", FULLSTACK_COMPOSE)
    write_file(output / ".dockerignore", DOCKERIGNORE)


GENERATORS = {
    "react": generate_react,
    "flask": generate_flask,
    "fullstack": generate_fullstack,
}


def main():
    parser = argparse.ArgumentParser(description="Generate Docker configurations")
    parser.add_argument("--type", required=True, choices=sorted(GENERATORS.keys()),
                        help="Project type: react, flask, or fullstack")
    parser.add_argument("--name", required=True, help="Project name")
    parser.add_argument("--port", type=int, default=None,
                        help="Port number (default: 3000 for react, 5001 for flask)")
    parser.add_argument("--output", default=".", help="Output directory")
    args = parser.parse_args()

    port = args.port or (3000 if args.type == "react" else 5001)
    output = Path(args.output)

    GENERATORS[args.type](args.name, port, output)
    print("Generated {} Docker config for '{}' at {}".format(args.type, args.name, output))
    print("  Files: Dockerfile, docker-compose.yml, .dockerignore")
    if args.type == "react":
        print("  nginx.conf (SPA routing)")
    if args.type == "fullstack":
        print("  Dockerfile.frontend, Dockerfile.backend, nginx.conf (reverse proxy)")
    print("  Run: docker compose up --build")


if __name__ == "__main__":
    main()
