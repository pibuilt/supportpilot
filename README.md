# SupportPilot

SupportPilot is a multi-service AI support operations platform that combines document ingestion, semantic retrieval, contract analysis, async orchestration, chat session persistence, and tenant-aware access control in one stack.

The repository is built around practical product and platform concerns rather than a single demo endpoint:

- API-key protected product workflows for ingestion, retrieval, analysis, tickets, and orchestration
- JWT-based user auth for signup, login, and admin controls
- Async job execution with Celery + Redis for ingestion and assistant orchestration
- Document chunk storage and semantic search using PostgreSQL + `pgvector`
- Separate AI and LLM services so orchestration logic is decoupled from provider access
- Frontend dashboards for documents, assistant sessions, admin actions, tickets, and API-key based product usage
- Observability through Prometheus, Grafana, request IDs, and usage logging

---

## Table of Contents

1. [What This Project Solves](#what-this-project-solves)
2. [High-Level Architecture](#high-level-architecture)
3. [Tech Stack and Why Each Part Exists](#tech-stack-and-why-each-part-exists)
4. [Repository Layout](#repository-layout)
5. [Core Product Workflows](#core-product-workflows)
6. [Authentication, RBAC, and Tenant Isolation](#authentication-rbac-and-tenant-isolation)
7. [Document Ingestion and Retrieval Pipeline](#document-ingestion-and-retrieval-pipeline)
8. [Contract Analysis Flow](#contract-analysis-flow)
9. [AI Orchestration Design](#ai-orchestration-design)
10. [Frontend Behavior](#frontend-behavior)
11. [Database and Migration Model](#database-and-migration-model)
12. [Environment and Secrets](#environment-and-secrets)
13. [Local Development Guide](#local-development-guide)
14. [API Reference](#api-reference)
15. [Observability and Operations](#observability-and-operations)
16. [Operational Troubleshooting](#operational-troubleshooting)
17. [Known Trade-offs and Future Hardening](#known-trade-offs-and-future-hardening)

---

## What This Project Solves

Support operations platforms usually need more than a chatbot. Real systems also need:

- scoped document knowledge that can be uploaded and searched later
- async execution for heavier workflows such as ingestion and orchestration
- persistent session history for support interactions
- tenant separation so one customer's data cannot leak into another tenant
- multiple access models: user login for dashboards and API keys for product APIs
- auditability, admin actions, usage tracking, and operational health signals

This repository addresses those needs with a split architecture:

- `api-gateway` owns product APIs, persistence, auth, jobs, exports, and observability
- `ai-service` owns orchestration logic, agent flow, tool decisions, and response shaping
- `llm-service` owns provider-facing generation and embeddings access
- `frontend` owns the operator dashboard and product workflows
- `postgres`, `redis`, `prometheus`, and `grafana` provide infrastructure support

---

## High-Level Architecture

```text
Browser
  |
  | HTTP :8080
  v
Frontend (Vite build served by nginx)
  |
  | /api/*
  v
API Gateway (FastAPI)
  |- auth + API key validation
  |- JWT-backed admin/user routes
  |- ingestion, search, documents, analysis
  |- orchestration job creation
  |- session + export APIs
  |- Prometheus metrics
  |
  +--> Redis
  |     '- Celery broker / async queue state
  |
  +--> Celery Worker
  |     |- process_ingestion_job
  |     '- process_orchestration_job
  |
  +--> PostgreSQL + pgvector
  |     |- users / api_keys / usage_logs / audit_logs
  |     |- async_jobs / tickets / chat_sessions / chat_messages
  |     '- embeddings / clause_analyses
  |
  +--> AI Service (FastAPI + LangGraph)
  |     |- triage node
  |     |- tool decision node
  |     |- retrieval tool execution
  |     |- specialist node
  |     '- tone node
  |
  '--> LLM Service (FastAPI)
        |- provider abstraction
        |- Ollama generation / embeddings
        '- OpenAI-compatible generation / embeddings
```

### Compose topology

`docker-compose.dev.yml` starts:

- `frontend` on `localhost:8080`
- `api-gateway` on `localhost:8000`
- `llm-service` on `localhost:8001`
- `ai-service` on `localhost:8002`
- `postgres` on `localhost:5432`
- `redis` on `localhost:6379`
- `prometheus` on `localhost:9090`
- `grafana` on `localhost:3000`

### Important routing behavior

The frontend is built with `VITE_API_BASE_URL=/api`, so browser calls stay same-origin and are proxied to the API gateway by nginx inside the frontend container. That keeps frontend code free from hardcoded container hostnames.

---

## Tech Stack and Why Each Part Exists

### Core application services

- FastAPI: typed REST services across gateway, AI service, and LLM service
- SQLAlchemy + Alembic: schema definition and repeatable database migration flow
- Celery + Redis: async execution for ingestion and orchestration jobs

### AI and orchestration

- LangGraph: multi-step orchestration workflow
- LangChain ecosystem: provider integrations and LLM-oriented utilities
- Ollama: local inference target for generation and embeddings
- OpenAI-compatible client: alternate provider path through `OPENAI_BASE_URL`
- LangSmith: optional tracing for node-level and provider-level execution

### Retrieval and storage

- PostgreSQL: transactional system of record
- `pgvector`: vector similarity search over document chunks
- custom document processors: PDF, DOCX, TXT, Markdown, HTML, and CSV extraction

### Frontend

- React 18 + TypeScript + Vite: operator-facing SPA
- TanStack Query: server-state management with live job updates and polling fallback
- React Router: authenticated route structure
- Tailwind CSS: component styling

### Operations

- Prometheus: scrapeable metrics
- Grafana: dashboarding
- request ID middleware + usage logs + audit logs: basic operational traceability

---

## Repository Layout

```text
supportpilot/
|- alembic/
|  '- versions/                  # schema evolution for users, tickets, sessions, embeddings, jobs, audits, RBAC
|
|- docker/
|  |- postgres/init/01-init-pgvector.sql
|  '- prometheus.yml
|
|- frontend/
|  |- Dockerfile
|  |- nginx.conf
|  |- package.json
|  '- src/
|     |- app/router.tsx
|     |- features/auth/
|     |- hooks/use-job-polling.ts
|     |- lib/api.ts
|     '- pages/
|        |- dashboard-page.tsx
|        |- documents-page.tsx
|        |- assistant-page.tsx
|        |- tickets-page.tsx
|        |- api-keys-page.tsx
|        '- admin-page.tsx
|
|- scripts/
|  |- linux/
|  |  |- bootstrap.sh
|  |  |- dev.sh
|  |  '- migrate.sh
|  '- windows/
|     |- bootstrap.ps1
|     |- dev.ps1
|     '- migrate.ps1
|
|- services/
|  |- api-gateway/
|  |  |- Dockerfile
|  |  |- requirements.txt
|  |  '- app/
|  |     |- api/v1/              # auth, tickets, ingestion, jobs, search, analyze, export, sessions, admin
|  |     |- db/models/           # users, api_keys, usage_logs, embeddings, tickets, sessions, async_jobs, analyses
|  |     |- middleware/          # auth, request context, rate limiting, Prometheus
|  |     |- repositories/
|  |     |- services/
|  |     |  |- document_processing/
|  |     |  |- ingestion_service.py
|  |     |  |- retrieval_service.py
|  |     |  |- contract_analysis_service.py
|  |     |  '- async_job_service.py
|  |     '- tasks/
|  |        |- ingestion_tasks.py
|  |        '- orchestration_tasks.py
|  |
|  |- ai-service/
|  |  |- requirements.txt
|  |  '- app/
|  |     |- agents/
|  |     |- api/v1/
|  |     |- graph/               # LangGraph workflow, nodes, state
|  |     |- prompts/
|  |     |- services/
|  |     '- tools/
|  |
|  '- llm-service/
|     |- requirements.txt
|     '- app/
|        |- api/v1/
|        |- providers/           # Ollama + OpenAI-compatible adapters
|        '- services/
|
|- docker-compose.dev.yml
|- .env.example
'- README.md
```

### Key ownership boundaries

- `services/api-gateway` owns platform APIs and persistence logic
- `services/ai-service` owns orchestration and tool-aware reasoning flow
- `services/llm-service` owns provider-facing model access
- `frontend` owns dashboard and operator experience
- `alembic` owns schema history and platform evolution

---

## Core Product Workflows

### 1. User onboarding and access bootstrap

- `POST /v1/auth/signup` creates a user, assigns a role, issues a JWT, and also creates an initial product API key
- the first user on the platform becomes `root_admin`
- the first admin-like user for a tenant becomes `admin`
- later users in that tenant become `user`

### 2. Document ingestion

- operator uploads a file or raw text
- gateway creates an async job record
- Celery worker extracts/processes text and writes chunk embeddings into PostgreSQL
- frontend follows job status through live updates with polling fallback

### 3. Semantic search

- operator submits a query, optionally scoped to one `document_id`
- query is embedded
- `pgvector` nearest-neighbor search finds candidate chunks
- reranking narrows results before returning the top matches

### 4. Contract analysis

- operator selects a document
- backend loads all stored chunks for that document
- clause detection runs over chunk text
- findings are deduplicated, summarized, and persisted

### 5. Assistant orchestration

- operator sends a prompt, optionally scoped to a document and session
- gateway creates an orchestration job
- worker invokes the AI service orchestration graph
- final assistant response is saved into chat sessions/messages
- frontend follows the job to completion through live updates with polling fallback

### 6. Export and admin workflows

- sessions, documents, and analysis results can be exported as JSON or CSV
- admins can suspend/activate users and revoke/regenerate API keys
- root admins can promote and demote tenant users

---

## Authentication, RBAC, and Tenant Isolation

SupportPilot uses JWT bearer auth for dashboard identity and supports API keys for explicit product credentials and external-style access.

### JWT user auth

Used for:

- signup
- login
- `/v1/auth/me`
- admin operations under `/v1/admin/*`

Behavior:

- signup/login returns a JWT access token
- the frontend uses bearer auth for current-user and admin calls
- the frontend can also use the same bearer session for product routes when no browser-pinned API key is present
- inactive users cannot log in

### API key auth

Used for:

- ingestion
- document listing
- semantic search
- analysis
- orchestration
- ticket APIs
- session and export APIs

Behavior:

- `AuthMiddleware` accepts `x-api-key` and falls back to bearer auth for signed-in product traffic
- validated key context is placed into `request.state`
- request state carries `owner`, `user_id`, `role`, `tenant_id`, and `api_key_id`
- API-key-authenticated product requests log usage into `usage_logs`

### Tenant isolation

Tenant and owner scoping are enforced throughout repositories and services:

- document existence checks include `owner_id` and `tenant_id`
- vector search filters on `owner_id` and `tenant_id`
- session reads and writes are tenant-scoped
- admin operations are constrained to the acting user's tenant

This means the same database can hold multiple tenants while still preserving application-level isolation.

---

## Document Ingestion and Retrieval Pipeline

The ingestion path is implemented across `app/api/v1/ingestion.py`, `document_processing/*`, `tasks/ingestion_tasks.py`, and the embedding repository/services.

### Supported ingestion paths

- `POST /v1/ingest`
  - accepts structured text payloads
- `POST /v1/ingest/file`
  - accepts uploaded files plus `document_id`

### Supported file formats

Processor selection is based on extension:

- `.txt`
- `.md`
- `.html` / `.htm`
- `.csv`
- `.pdf`
- `.docx`

### Ingestion lifecycle

1. Client uploads a file or sends raw text.
2. Gateway creates an `async_jobs` row with type `DOCUMENT_INGESTION`.
3. Celery worker marks job `PROCESSING`.
4. Text is chunked and embedded.
5. Embeddings are stored in PostgreSQL with:
   - `owner_id`
   - `tenant_id`
   - `document_id`
   - `chunk_id`
   - `chunk_text`
   - embedding metadata
6. Job result JSON is saved and status becomes `COMPLETED`.

### Retry and dead-letter behavior

Both ingestion and orchestration tasks use:

- max retries: `3`
- exponential backoff: `2 ** retries`
- terminal status: `DEAD_LETTER`

That gives the platform a minimal but real async failure model instead of only fire-and-forget behavior.

### Retrieval flow

Search logic in `retrieval_service.py` does:

1. create query embedding
2. pull a larger candidate set from `pgvector`
3. rerank candidates
4. return final `top_k` results

The repository returns:

- `document_id`
- `chunk_id`
- `chunk_text`
- numeric similarity score
- short preview

---

## Contract Analysis Flow

Contract analysis is separate from semantic retrieval even though both rely on the same stored chunk corpus.

### Route behavior

`POST /v1/analyze`

- verifies the requested document belongs to the authenticated owner and tenant
- loads all chunks for that document
- runs clause detection against each chunk
- persists clause analyses
- returns raw clauses plus summary output

### Output structure

The analysis response includes:

- `document_id`
- `clauses`
- `summary`
  - `total_clauses`
  - `by_type`
- `executive_summary`
  - `overall_risk`
  - `high_risk_count`
  - `medium_risk_count`
  - `low_risk_count`
  - `critical_clauses`

### Why this matters

This design lets the same ingested knowledge base support:

- search-oriented retrieval
- structured contract review
- downstream export of analyses for reporting or audit

---

## AI Orchestration Design

The orchestration graph is built in `services/ai-service/app/graph/workflow.py`.

### Graph structure

```text
START
  |
  v
triage
  |
  v
tool_decision
  |----------------------.
  | use_tool = true      | use_tool = false
  v                      v
tool_execution       specialist
  |                      |
  '----------->----------'
               |
               v
              tone
               |
               v
              END
```

### Node responsibilities

- `triage`
  - classifies the user request and captures high-level intent
- `tool_decision`
  - decides whether external tool usage is needed
  - automatically chooses retrieval when a `document_id` is present
- `tool_execution`
  - executes registered tools
  - injects `owner_id`, `tenant_id`, `api_key`, and optional `document_id`
- `specialist`
  - drafts the substantive response using query context, triage output, and optional tool output
- `tone`
  - rewrites/adjusts the answer into the final assistant response

### Why the orchestration runs asynchronously

The API gateway does not block on full LLM execution. Instead it:

- creates a job
- dispatches to Celery
- persists messages only after the final result is ready

That is a better fit for:

- long-running model calls
- tool-driven workflows
- live job-status UX with polling fallback
- operational retries

---

## Frontend Behavior

The frontend route tree is centered on authenticated application use rather than a single landing page.

### Primary pages

- `/`
  - dashboard summary using health, documents, sessions, and analysis export preview
- `/documents`
  - upload, live ingestion status, document listing, chunk inspection, delete, export
- `/assistant`
  - chat, semantic search, and contract analysis in one workspace
- `/tickets`
  - support ticket creation and listing
- `/api-keys`
  - self-service API key issue, validation, revoke, regenerate, and local browser pinning
- `/admin`
  - tenant user management and tenant API key admin actions
- `/login` and `/signup`
  - JWT user flows

### Important frontend design choices

- the assistant page merges three workflows into one shell:
  - chat
  - search
  - analyze
- TanStack Query is used heavily for:
  - data fetching
  - mutation lifecycle
  - streaming-first async job updates with polling fallback
  - invalidation after completion
- browser session storage is used to preserve:
  - active session selection
  - pending jobs
  - upload progress context

### User experience implications

If a user has a valid JWT but no browser-pinned product API key, product workflows still work through bearer fallback. The API Keys page is mainly for explicit credential management, browser pinning, and integration-style usage.

---

## Database and Migration Model

Alembic history shows this repo has evolved beyond a toy schema. The database includes at least these functional areas:

- identity and security
  - `users`
  - `api_keys`
  - `usage_logs`
  - `audit_logs`
- support and conversation state
  - `tickets`
  - `chat_sessions`
  - `chat_messages`
- retrieval and analysis
  - `embeddings`
  - `clause_analyses`
- async platform workflows
  - `async_jobs`

### Why `pgvector` initialization matters

The Postgres container mounts `docker/postgres/init/01-init-pgvector.sql`, so a clean database bootstraps the vector extension automatically. Without that extension, embedding storage and similarity search will fail.

### Migration startup behavior

The Compose file includes a one-shot `migrate` service for explicit runs:

- waits for Postgres health
- runs `alembic upgrade head`
- can be launched manually when you need an explicit migration container run

The bootstrap scripts launch that migration container explicitly, watch Postgres until the Alembic head revision is present, and then continue application startup. This avoids relying on Docker Compose's `service_completed_successfully` lifecycle handling and also works around local Docker states where the migration container reaches head but never transitions cleanly to `exited`.

---

## Environment and Secrets

`.env.example` documents the main runtime variables.

### Core platform variables

```env
ENV=dev
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=supportpilot
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/supportpilot
REDIS_URL=redis://redis:6379/0
JWT_SECRET_KEY=your_jwt_secret_key
```

### LLM provider variables

```env
LLM_PROVIDER=ollama
OLLAMA_URL=http://host.docker.internal:11434
OLLAMA_LLM_MODEL=qwen2.5:1.5b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

OPENAI_API_KEY=
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_MODEL=openrouter/free
```

### Observability variables

```env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langchain_api_key
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_PROJECT=supportpilot-dev

GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=<password>
```

### Setup notes

- copy `.env.example` to `.env`
- if using Ollama locally, make sure the host machine has the configured model pulled
- if using an OpenAI-compatible backend, set `OPENAI_API_KEY` and related base/model variables
- do not commit real secrets

---

## Local Development Guide

### Prerequisites

- Docker Desktop or Docker Engine with Compose
- Python environment if you want to run backend services manually outside Docker
- Node.js 18+ if you want to run the frontend manually outside Docker
- optional Ollama instance on the host if `LLM_PROVIDER=ollama`

### Path A: bootstrap the full local stack

Windows:

```powershell
.\scripts\windows\bootstrap.ps1
```

Linux:

```bash
./scripts/linux/bootstrap.sh
```

What the bootstrap scripts do:

1. stop the previous Compose environment
2. optionally prune Docker state only when you request a clean bootstrap
3. start Postgres, Redis, and the supporting AI/LLM services
4. run the migration container and wait for the database to reach Alembic head
5. start the API, worker, frontend, and observability services
6. verify API health

Windows clean reset:

```powershell
.\scripts\windows\bootstrap.ps1 -Clean
```

Linux clean reset:

```bash
SUPPORTPILOT_CLEAN_BOOTSTRAP=1 ./scripts/linux/bootstrap.sh
```

The scripts also accept `-Clear` on Windows and `--clear` on Linux as clean-reset aliases.

### Restart containers without bootstrap

Use this when the environment has already been bootstrapped and you just want to stop or restart the running stack without resetting Docker state or rerunning migrations.

Stop the stack:

```bash
docker compose -f docker-compose.dev.yml stop
```

Start it again:

```bash
docker compose -f docker-compose.dev.yml start
```

Shut it down completely but keep volumes:

```bash
docker compose -f docker-compose.dev.yml down
```

Use bootstrap again when you want a full rebuild flow, and add the clean flag only when you explicitly want the aggressive reset path.

### Path B: run selected services manually

API gateway:

```bash
pip install -r services/api-gateway/requirements.txt
set PYTHONPATH=services/api-gateway
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

AI service:

```bash
pip install -r services/ai-service/requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8002
```

LLM service:

```bash
pip install -r services/llm-service/requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

### Local endpoints

- frontend: `http://localhost:8080`
- API gateway docs: `http://localhost:8000/docs`
- AI service docs: `http://localhost:8002/docs`
- LLM service docs: `http://localhost:8001/docs`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000`

---

## API Reference

This is not a full OpenAPI dump, but it covers the main platform routes.

### Health and metrics

#### `GET /health`

Gateway health response is wrapped in the project's success envelope:

```json
{
  "data": {
    "status": "ok",
    "timestamp": 1710000000.0
  },
  "request_id": "uuid"
}
```

#### `GET /metrics`

Returns Prometheus scrape output from the API gateway.

### Auth

#### `POST /v1/auth/signup`

Creates a user and returns:

- `access_token`
- `api_key`
- `key_prefix`
- `user_id`
- `email`
- `full_name`
- `role`
- `tenant_id`

#### `POST /v1/auth/login`

Returns the same response envelope as signup, but login now issues only the bearer session by default. The `api_key` field is empty on normal login, and API key lifecycle is handled through the API Keys management flows.

#### `GET /v1/auth/me`

Bearer-token route for current user information.

### API keys

#### `GET /v1/api-keys/validate`

Validates an explicit API key and returns:

- `valid`
- `owner`
- `user_id`
- `role`
- `tenant_id`
- `api_key_id`

#### `GET /v1/api-keys/mine`

Lists the current user's API keys.

#### `POST /v1/api-keys/mine`

Issues a new API key for the current user and returns:

- `api_key_id`
- `api_key`
- `key_prefix`

#### `PATCH /v1/api-keys/mine/{api_key_id}/revoke`

Revokes one of the current user's API keys.

#### `PATCH /v1/api-keys/mine/{api_key_id}/regenerate`

Regenerates one of the current user's API keys and returns a fresh raw key.

### Documents and ingestion

#### `POST /v1/ingest`

Queues raw text ingestion.

#### `POST /v1/ingest/file`

Multipart upload:

- `document_id`
- `file`

Returns job metadata for async tracking.

#### `GET /v1/documents`

Lists document collections available to the authenticated owner/tenant.

#### `GET /v1/documents/{document_id}`

Returns chunk metadata and stored chunk text for one document.

#### `DELETE /v1/documents/{document_id}`

Deletes all stored chunks for that document within the caller's scope.

### Jobs

#### `GET /jobs/{job_id}`

Returns:

- `job_id`
- `job_type`
- `status`
- `retry_count`
- `error_message`
- `result`
- `started_at`
- `completed_at`

#### `GET /jobs/{job_id}/stream`

Streams job lifecycle updates as server-sent events.

### Retrieval and analysis

#### `POST /v1/search`

Request shape:

```json
{
  "query": "termination clause",
  "document_id": "msa-2026-001",
  "top_k": 5
}
```

#### `POST /v1/analyze`

Request shape:

```json
{
  "document_id": "msa-2026-001"
}
```

### Orchestration

#### `POST /v1/orchestrate`

Request fields include:

- `query`
- optional `document_id`
- optional `session_id`
- `context_limit`

Returns queued job metadata rather than the final answer.

### Sessions and exports

#### `GET /v1/sessions`

Lists persisted assistant sessions for the current owner/tenant.

#### `GET /v1/sessions/{session_id}`

Returns session metadata and message history.

#### `GET /v1/export/documents`
#### `GET /v1/export/sessions`
#### `GET /v1/export/analyses`

Each supports `format=json|csv`.

### Admin

#### `GET /v1/admin/users`
#### `GET /v1/admin/api-keys`
#### `PATCH /v1/admin/users/{user_id}/suspend`
#### `PATCH /v1/admin/users/{user_id}/activate`
#### `PATCH /v1/admin/users/{user_id}/promote`
#### `PATCH /v1/admin/users/{user_id}/demote`
#### `PATCH /v1/admin/api-keys/{api_key_id}/revoke`
#### `PATCH /v1/admin/api-keys/{api_key_id}/regenerate`

Promotion and demotion are root-admin only.

---

## Observability and Operations

### Built-in instrumentation

- request context middleware adds request IDs
- Prometheus middleware exports metrics from the API gateway
- usage logging records endpoint usage by API key
- audit logging records auth and admin events
- LangSmith tracing can wrap orchestration nodes and provider calls

### Job observability model

Async jobs persist lifecycle fields:

- status
- retry count
- error message
- start time
- completion time
- structured result JSON

That is especially useful for frontend live status updates, polling fallback, and operator debugging.

### Practical ops note

The current repo includes Prometheus and Grafana in Compose, but it does not include CI/CD workflow files in this snapshot, so deployment automation is not documented here as an implemented feature.

---

## Operational Troubleshooting

### Product route returns `401`

Cause:

- request hit a product route protected by `AuthMiddleware`
- neither a valid bearer session nor a valid API key was available

Fix:

- sign in again if your bearer session expired
- or include `x-api-key`
- confirm the key is active and belongs to the correct tenant/user

### Signup/login works but product pages are still blocked

Cause:

- the browser session is stale
- or a manually pinned product API key is invalid and overriding bearer fallback
- or the current user no longer has access to the requested tenant-scoped data

Fix:

- clear the locally stored API key on the API Keys page if you want to fall back to bearer auth
- open the API Keys page to issue or rotate a new product API key if needed
- confirm `/v1/api-keys/validate` succeeds

### Ingestion job stays `FAILED` or reaches `DEAD_LETTER`

Likely causes:

- unsupported file type
- extraction failure in a document processor
- embedding provider failure
- PostgreSQL / Redis connectivity issue

Checks:

```bash
curl http://localhost:8000/jobs/<job_id>
docker logs sp_celery_worker
docker logs sp_api_gateway
```

### Search returns `Document not found`

Cause:

- requested `document_id` does not exist for the current owner/tenant

Fix:

- verify the document was ingested successfully
- verify you are using the same authenticated API key scope

### Ollama requests fail

Likely causes:

- Ollama is not running on the host
- configured models are missing
- `OLLAMA_URL` is incorrect for the current environment

Checks:

```bash
curl http://localhost:11434/api/tags
docker logs sp_llm_service
docker logs sp_ai_service
```

### `pgvector` errors on startup or search

Cause:

- database was not initialized with the extension

Fix:

- rebuild from a clean Postgres volume so `01-init-pgvector.sql` runs
- reapply migrations after reset

### Admin routes fail for non-admin users

Cause:

- expected behavior

Rules:

- `admin` and `root_admin` can perform tenant admin operations
- only `root_admin` can promote or demote roles

---

## Known Trade-offs and Future Hardening

This codebase already goes beyond a demo, but there are still visible trade-offs in the current implementation.

1. CI/CD, production nginx, and cloud deployment automation are not present in this repo snapshot.
   - Those would be natural next steps if this platform were being pushed toward a fuller production story.

2. Retrieval, analysis, and orchestration all depend on a healthy embeddings/model path.
   - Adding more explicit readiness checks around provider availability would make failures easier to diagnose earlier.

3. The LLM service and AI service are both present, but some embedding generation in the gateway still calls Ollama directly.
   - Unifying all model access behind one internal boundary would simplify operational reasoning.
