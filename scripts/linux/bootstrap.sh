#!/bin/bash
set -e

clean_bootstrap="${SUPPORTPILOT_CLEAN_BOOTSTRAP:-0}"
migration_head_revision="d217bfef5851"
migration_container_name="supportpilot-migrate-bootstrap"

if [ "${1:-}" = "--clean" ]; then
  clean_bootstrap=1
fi

if [ "${1:-}" = "--clear" ]; then
  clean_bootstrap=1
fi

remove_container_if_present() {
  local container_name="$1"
  local container_id
  container_id=$(docker ps -aq --filter "name=^${container_name}$")
  if [ -n "$container_id" ]; then
    docker rm -f "$container_name" >/dev/null
  fi
}

remove_migration_run_containers() {
  local container_ids
  container_ids=$(docker ps -aq --filter "name=supportpilot-migrate-run")
  if [ -n "$container_ids" ]; then
    while IFS= read -r container_id; do
      if [ -n "$container_id" ]; then
        docker rm -f "$container_id" >/dev/null
      fi
    done <<EOF
$container_ids
EOF
  fi
}

wait_for_migration_head() {
  local revision="$1"
  local timeout_seconds="${2:-180}"
  local deadline=$((SECONDS + timeout_seconds))

  while [ "$SECONDS" -lt "$deadline" ]; do
    if table_exists=$(docker compose -f docker-compose.dev.yml exec -T postgres psql -U postgres -d supportpilot -t -A -c "select count(*) from information_schema.tables where table_schema = 'public' and table_name = 'alembic_version';" 2>/dev/null); then
      table_exists="$(printf "%s" "$table_exists" | tr -d '\r\n')"
      if [ "$table_exists" = "1" ]; then
        if current_revision=$(docker compose -f docker-compose.dev.yml exec -T postgres psql -U postgres -d supportpilot -t -A -c "select version_num from alembic_version limit 1;" 2>/dev/null); then
          current_revision="$(printf "%s" "$current_revision" | tr -d '\r\n')"
          if [ "$current_revision" = "$revision" ]; then
            return 0
          fi
        fi
      fi
    fi

    sleep 2
  done

  echo "Timed out waiting for Alembic head revision '$revision'."
  return 1
}

echo ""
echo "Stopping existing environment..."
if [ "$clean_bootstrap" = "1" ]; then
  docker compose -f docker-compose.dev.yml down -v
else
  docker compose -f docker-compose.dev.yml down
fi

if [ "$clean_bootstrap" = "1" ]; then
  echo ""
  echo "Pruning Docker system..."
  docker system prune -af --volumes
fi

echo ""
echo "Cleaning up stale migration containers..."
remove_container_if_present "sp_migrate"
remove_container_if_present "$migration_container_name"
remove_migration_run_containers

echo ""
echo "Starting infrastructure and dependency services..."
docker compose -f docker-compose.dev.yml up --build -d postgres redis llm-service ai-service

echo ""
echo "Running containerized migrations..."
docker compose -f docker-compose.dev.yml run -d --name "$migration_container_name" migrate >/dev/null
wait_for_migration_head "$migration_head_revision"
docker rm -f "$migration_container_name" >/dev/null

echo ""
echo "Starting application services..."
docker compose -f docker-compose.dev.yml up --build -d api-gateway celery-worker frontend prometheus grafana

echo ""
echo "Verifying API health..."
curl http://localhost:8000/health

echo ""
echo "SupportPilot bootstrap complete."
echo ""
