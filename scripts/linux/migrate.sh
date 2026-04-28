#!/bin/bash
set -e

source ./scripts/linux/dev.sh

echo "Applying Alembic migrations..."
alembic upgrade head
echo "Migrations complete."