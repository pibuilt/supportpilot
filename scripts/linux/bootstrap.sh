#!/bin/bash
set -e

echo ""
echo "Stopping existing environment..."
docker compose -f docker-compose.dev.yml down -v

echo ""
echo "Pruning Docker system..."
docker system prune -af --volumes

echo ""
echo "Rebuilding SupportPilot..."
docker compose -f docker-compose.dev.yml up --build -d

echo ""
echo "Waiting for PostgreSQL initialization..."
sleep 15

source ./scripts/linux/dev.sh

echo ""
echo "Applying migrations..."
alembic upgrade head

echo ""
echo "Verifying API health..."
curl http://localhost:8000/health

echo ""
echo "SupportPilot bootstrap complete."
echo ""