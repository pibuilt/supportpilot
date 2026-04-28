$ErrorActionPreference = "Stop"

param(
    [Parameter(Mandatory=$true)]
    [string]$Message
)

. .\scripts\windows\dev.ps1

Write-Host "Generating Alembic revision..."
alembic revision --autogenerate -m $Message
Write-Host "Revision generated."