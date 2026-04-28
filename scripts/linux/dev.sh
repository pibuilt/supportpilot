#!/bin/bash
set -e

source .venv/bin/activate
export PYTHONPATH=services/api-gateway

echo ""
echo "SupportPilot Linux development environment ready."
echo "Venv activated + PYTHONPATH configured."
echo ""