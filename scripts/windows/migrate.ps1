$ErrorActionPreference = "Stop"

. .\scripts\windows\dev.ps1

Write-Host "Applying Alembic migrations..."
alembic upgrade head
Write-Host "Migrations complete."