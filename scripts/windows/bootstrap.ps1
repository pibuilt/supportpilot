param(
    [Alias("Clear")]
    [switch]$Clean
)

$ErrorActionPreference = "Stop"
$MigrationHeadRevision = "d217bfef5851"
$MigrationContainerName = "supportpilot-migrate-bootstrap"

function Remove-ContainerIfPresent {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ContainerName
    )

    $containerId = docker ps -aq --filter "name=^${ContainerName}$"
    if ($LASTEXITCODE -eq 0 -and $containerId) {
        docker rm -f $ContainerName | Out-Null
    }
}

function Remove-MigrationRunContainers {
    $containerIds = docker ps -aq --filter "name=supportpilot-migrate-run"
    if ($LASTEXITCODE -eq 0 -and $containerIds) {
        foreach ($containerId in ($containerIds -split "`r?`n")) {
            if ($containerId.Trim()) {
                $trimmedContainerId = $containerId.Trim()
                docker rm -f $trimmedContainerId | Out-Null
            }
        }
    }
}

function Wait-ForMigrationHead {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Revision,
        [int]$TimeoutSeconds = 180
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)

    while ((Get-Date) -lt $deadline) {
        $tableExists = docker compose -f docker-compose.dev.yml exec -T postgres psql -U postgres -d supportpilot -t -A -c "select count(*) from information_schema.tables where table_schema = 'public' and table_name = 'alembic_version';" 2>$null
        if ($LASTEXITCODE -eq 0 -and $tableExists.Trim() -eq "1") {
            $currentRevision = docker compose -f docker-compose.dev.yml exec -T postgres psql -U postgres -d supportpilot -t -A -c "select version_num from alembic_version limit 1;" 2>$null
            if ($LASTEXITCODE -eq 0 -and $currentRevision.Trim() -eq $Revision) {
                return
            }
        }

        Start-Sleep -Seconds 2
    }

    throw "Timed out waiting for Alembic head revision '$Revision'."
}

Write-Host ""
Write-Host "Stopping existing environment..."
if ($Clean) {
    docker compose -f docker-compose.dev.yml down -v
} else {
    docker compose -f docker-compose.dev.yml down
}

if ($Clean) {
    Write-Host ""
    Write-Host "Pruning Docker system..."
    docker system prune -af --volumes
}

Write-Host ""
Write-Host "Cleaning up stale migration containers..."
Remove-ContainerIfPresent -ContainerName "sp_migrate"
Remove-ContainerIfPresent -ContainerName $MigrationContainerName
Remove-MigrationRunContainers

Write-Host ""
Write-Host "Starting infrastructure and dependency services..."
docker compose -f docker-compose.dev.yml up --build -d postgres redis llm-service ai-service

Write-Host ""
Write-Host "Running containerized migrations..."
docker compose -f docker-compose.dev.yml run -d --name $MigrationContainerName migrate | Out-Null
Wait-ForMigrationHead -Revision $MigrationHeadRevision
docker rm -f $MigrationContainerName | Out-Null

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
