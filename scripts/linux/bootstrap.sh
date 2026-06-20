#!/bin/bash
set -e

echo ""
echo "Stopping existing environment..."
docker compose -f docker-compose.dev.yml down -v

echo ""
echo "Pruning Docker system..."
docker system prune -af --volumes

echo ""
echo "Starting infrastructure and dependency services..."
docker compose -f docker-compose.dev.yml up --build -d postgres redis llm-service ai-service

echo ""
echo "Running containerized migrations..."
docker compose -f docker-compose.dev.yml run --rm migrate

echo ""
echo "Starting application services..."
docker compose -f docker-compose.dev.yml up --build -d api-gateway celery-worker frontend prometheus grafana

echo ""
echo "Verifying API health..."
curl http://localhost:8000/health

echo ""
echo "SupportPilot bootstrap complete."
echo ""
