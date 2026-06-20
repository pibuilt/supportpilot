$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "Stopping existing environment..."
docker compose -f docker-compose.dev.yml down -v

Write-Host ""
Write-Host "Pruning Docker system..."
docker system prune -af --volumes

Write-Host ""
Write-Host "Starting infrastructure and dependency services..."
docker compose -f docker-compose.dev.yml up --build -d postgres redis llm-service ai-service

Write-Host ""
Write-Host "Running containerized migrations..."
docker compose -f docker-compose.dev.yml run --rm migrate

Write-Host ""
Write-Host "Starting application services..."
docker compose -f docker-compose.dev.yml up --build -d api-gateway celery-worker frontend prometheus grafana

Write-Host ""
Write-Host "Waiting for API readiness..."

$maxAttempts = 15
$attempt = 1
$apiReady = $false

while ($attempt -le $maxAttempts) {
    try {
        Invoke-WebRequest http://localhost:8000/health -UseBasicParsing | Out-Null
        $apiReady = $true
        break
    } catch {
        Write-Host "API not ready yet... attempt $attempt/$maxAttempts"
        Start-Sleep -Seconds 2
        $attempt++
    }
}

if (-not $apiReady) {
    Write-Error "API failed to become healthy."
    exit 1
}

Write-Host ""
Write-Host "SupportPilot bootstrap completed successfully."
Write-Host ""
