$ErrorActionPreference = "Stop"

. .venv\Scripts\Activate.ps1
$env:PYTHONPATH = "services/api-gateway"

Write-Host ""
Write-Host "SupportPilot Windows development environment ready."
Write-Host "Venv activated + PYTHONPATH configured."
Write-Host ""