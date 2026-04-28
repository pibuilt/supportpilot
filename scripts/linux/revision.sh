#!/bin/bash
set -e

if [ -z "$1" ]; then
  echo "Usage: ./revision.sh 'migration message'"
  exit 1
fi

source ./scripts/linux/dev.sh

echo "Generating Alembic revision..."
alembic revision --autogenerate -m "$1"
echo "Revision generated."