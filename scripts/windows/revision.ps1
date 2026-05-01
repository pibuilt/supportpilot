param(
    [Parameter(Mandatory=$true)]
    [string]$Message
)

$ErrorActionPreference = "Stop"

. .\scripts\windows\dev.ps1

Write-Host ""
Write-Host "Generating Alembic revision..."
alembic revision --autogenerate -m $Message
Write-Host "Revision generated."
Write-Host ""