# Docker Deployment Guide

This guide explains how to run the Vietnamese Translation service using Docker.

## Prerequisites

- Docker installed ([Download](https://www.docker.com/products/docker-desktop))
- Docker Compose (included with Docker Desktop)
- OpenAI API key

## Quick Start with Docker Compose

### 1. Create `.env` file
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 2. Build and run
```bash
docker-compose up --build
```

### 3. Access the application
- Web UI: http://localhost:8000
- API: http://localhost:8000/api/health

### 4. Stop the application
```bash
docker-compose down
```

---

## Manual Docker Commands

### Build the image
```bash
docker build -t vietnamese-translation:latest .
```

### Run the container
```bash
docker run -p 8000:8000 \
  -e OPENAI_API_KEY="your-api-key-here" \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/translations.db:/app/translations.db \
  vietnamese-translation:latest
```

### Run with all environment variables
```bash
docker run -p 8000:8000 \
  -e OPENAI_API_KEY="your-api-key-here" \
  -e SOURCE_LANGUAGE=vi \
  -e TARGET_LANGUAGE=en \
  -e WHISPER_MODEL_SIZE=small \
  -e AUDIO_SAMPLE_RATE=16000 \
  -e AUDIO_CHUNK_DURATION=10 \
  -e DB_PATH=/app/translations.db \
  -e LOG_LEVEL=INFO \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/translations.db:/app/translations.db \
  vietnamese-translation:latest
```

---

## Development Mode

### With auto-reload
```bash
docker-compose -f docker-compose.yml exec app python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Or uncomment the command in `docker-compose.yml`:
```yaml
command: python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### Access container shell
```bash
docker-compose exec app bash
```

### View logs
```bash
docker-compose logs -f app
```

---

## Production Deployment

### Using Docker Registry (Docker Hub)

1. **Build and tag image**
```bash
docker build -t your-username/vietnamese-translation:1.0 .
```

2. **Push to registry**
```bash
docker login
docker push your-username/vietnamese-translation:1.0
```

3. **Deploy on any server**
```bash
docker run -d \
  --name vietnamese-translation \
  -p 80:8000 \
  -e OPENAI_API_KEY="your-key" \
  -v /data/translations.db:/app/translations.db \
  -v /data/logs:/app/logs \
  your-username/vietnamese-translation:1.0
```

### Using Docker Compose in Production

Create `docker-compose.prod.yml`:
```yaml
version: '3.8'

services:
  app:
    image: your-username/vietnamese-translation:1.0
    container_name: vietnamese-translation-prod
    restart: always
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - LOG_LEVEL=WARNING
      - WHISPER_MODEL_SIZE=small
    volumes:
      - /data/translations.db:/app/translations.db
      - /data/logs:/app/logs
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

networks:
  app-network:
    driver: bridge
```

Deploy:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

## Kubernetes Deployment

### Create Kubernetes manifests

**deployment.yaml**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vietnamese-translation
spec:
  replicas: 2
  selector:
    matchLabels:
      app: vietnamese-translation
  template:
    metadata:
      labels:
        app: vietnamese-translation
    spec:
      containers:
      - name: app
        image: your-username/vietnamese-translation:1.0
        ports:
        - containerPort: 8000
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: translation-secrets
              key: openai-api-key
        - name: LOG_LEVEL
          value: "WARNING"
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /api/health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: vietnamese-translation-service
spec:
  type: LoadBalancer
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  selector:
    app: vietnamese-translation
```

Deploy:
```bash
# Create secret
kubectl create secret generic translation-secrets \
  --from-literal=openai-api-key="your-api-key"

# Deploy
kubectl apply -f deployment.yaml

# Check status
kubectl get pods
kubectl get services
```

---

## Docker Best Practices

### Security
- ✅ Never hardcode API keys (use secrets/environment variables)
- ✅ Run as non-root user (optional, requires Dockerfile changes)
- ✅ Scan image for vulnerabilities: `docker scan vietnamese-translation`
- ✅ Keep base image updated

### Performance
- ✅ Use multi-stage builds for smaller images (optional)
- ✅ Cache layers efficiently
- ✅ Use slim base images (python:3.11-slim)

### Reliability
- ✅ Include health checks
- ✅ Use restart policies
- ✅ Set resource limits
- ✅ Implement logging

---

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs app

# Or
docker logs container_name
```

### API key not recognized
```bash
# Verify environment variables
docker-compose config | grep OPENAI_API_KEY

# Or manually set
docker run -e OPENAI_API_KEY="your-key" ...
```

### Port already in use
```bash
# Change port mapping
docker run -p 8001:8000 ...

# Or find what's using port 8000
lsof -i :8000
```

### Database file issues
```bash
# Ensure permissions
chmod 755 translations.db

# Or reset
rm translations.db
docker-compose up
```

### Memory issues
```bash
# Increase memory limit in docker-compose.yml
mem_limit: 2g
memswap_limit: 2g
```

---

## Useful Docker Commands

```bash
# List running containers
docker ps

# List all containers
docker ps -a

# View container logs
docker logs container_name
docker logs -f container_name  # Follow logs

# Stop container
docker stop container_name

# Remove container
docker rm container_name

# Remove image
docker rmi image_name

# Exec command in running container
docker exec -it container_name bash

# Inspect container
docker inspect container_name

# View resource usage
docker stats

# Clean up unused resources
docker system prune
```

---

## Publishing to Docker Hub

```bash
# 1. Create account on Docker Hub
# 2. Create repository

# 3. Build with proper tag
docker build -t your-username/vietnamese-translation:latest .

# 4. Login
docker login

# 5. Push
docker push your-username/vietnamese-translation:latest

# 6. Anyone can now deploy
docker run -e OPENAI_API_KEY="key" your-username/vietnamese-translation
```

---

## Next Steps

- Deploy to Docker Hub for sharing
- Set up CI/CD pipeline with GitHub Actions
- Deploy to production with Docker Compose or Kubernetes
- Monitor with tools like Prometheus/Grafana

---

**Ready to containerize? Let's go! 🐳**
