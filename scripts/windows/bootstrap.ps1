$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "Stopping existing environment..."
docker compose -f docker-compose.dev.yml down -v

Write-Host ""
Write-Host "Pruning Docker system..."
docker system prune -af --volumes

Write-Host ""
Write-Host "Rebuilding SupportPilot..."
docker compose -f docker-compose.dev.yml up --build -d

Write-Host ""
Write-Host "Waiting for PostgreSQL initialization..."
Start-Sleep -Seconds 15

. .\scripts\windows\dev.ps1

Write-Host ""
Write-Host "Applying migrations..."
alembic upgrade head

Write-Host ""
Write-Host "Verifying API health..."
Invoke-WebRequest http://localhost:8000/health -UseBasicParsing

Write-Host ""
Write-Host "SupportPilot bootstrap complete."
Write-Host ""