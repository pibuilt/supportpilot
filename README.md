# SupportPilot

SupportPilot is an AI-driven, highly scalable customer support operations platform. It integrates agentic workflow pipelines using LangGraph and Ollama with a robust FastAPI + Celery architecture to automate ticket triage, provide RAG-enhanced conversational support, and monitor platform metrics in real time.

## 🚀 Key Features

- **Intelligent Ticketing**: Automated triage, prioritization, and categorization using asynchronous LLM pipelines.
- **RAG-Powered Chat**: Next-generation conversational sessions backed by `pgvector` nearest-neighbor semantic search.
- **Agentic Workflows**: Multi-step reasoning loops orchestrated with LangGraph, delegating complex queries to local models.
- **Metrics & Observability**: Out-of-the-box Prometheus/Grafana stack and optional LangSmith instrumentation for analyzing LLM chain traces.
- **Enterprise Auth & Quotas**: Full RBAC tiering, tenant tracking, and API key issuance with usage logs.

## 🏛 Architecture Overview

SupportPilot adopts a microservice-oriented design where heavy machine learning inference is decoupled via Celery and an isolated AI service.

```text
      +-------------------+
      |                   |
      |   Web Frontend    |
      |  (React/Tailwind) |
      |                   |
      +--------+----------+
               | (REST API)
               v
      +--------+----------+      +----------------+
      |                   |      |                |
      |   API Gateway     +----->+  Celery Worker |
      |    (FastAPI)      |      |                |
      |                   |      +-------+--------+
      +--+-----------+----+              |
         |           |                   |
 (Sync)  |           v (Async)           | (Execute Job)
         |     +-----+-------------+     |
         |     |                   |<----+
         +---->|    AI Service     |
               | (LangGraph/Agents)|
               |                   |
               +--+-------------+--+
                  |             |
           (Uses) |             | (RPC/Inference)
                  v             v
       +----------+--+       +--+----------+
       |             |       |             |
       |  Postgres   |       | LLM Service |
       | (pgvector)  |       |   (Ollama)  |
       |             |       |             |
       +-------------+       +-------------+
```

## 🛠 Tech Stack Map

| Component         | Technology                             | Description                                                                         |
| :---------------- | :------------------------------------- | :---------------------------------------------------------------------------------- |
| **Frontend**      | React, Vite, TS, Tailwind, React Query | Interactive Dashboards, API Key Management, Admin Panels, and Chat interface.       |
| **API Gateway**   | FastAPI, Celery, Redis                 | High-concurrency entrypoint mapping REST calls to internal domains / async jobs.    |
| **AI Subsystem**  | LangChain, LangGraph, Ollama           | LLM pipelines for embeddings, document chunking, categorization, and drafting.      |
| **Persistence**   | PostgreSQL, pgvector, Alembic          | Relational data, user sessions, audit logs, and highly dimensional vector searches. |
| **Observability** | Prometheus, Grafana, LangSmith         | Application/hardware metrics, node tracking, and inference cost monitoring.         |

## 🗄 Core Database Schema

The persistence layer uses a unified Postgres database with specialized Alembic migrations:

- **`users` / `api_keys` / `usage_logs`**: Identity management, API tenancy routing, usage analysis, and role-based access control.
- **`tickets`**: Customer support tickets decorated with metadata (`ticket_category`, `priority`, etc.).
- **`chat_sessions` & `chat_messages`**: Persistent conversational context, allowing users to return to multi-turn interactions.
- **`embeddings`**: Highly-optimized `pgvector` store for document chunks used asynchronously in the Langchain RAG retrievers.
- **`async_jobs`**: Job status states mapped directly into Celery payloads for frontend tracking and polling.

## 💻 Local Development Setup

The repository is built to spin up fully containerized via Docker Compose.

### Prerequisites

- Docker & Docker Compose
- PowerShell (Windows) or Bash (Linux)

### 1. Bootstrap

Initialize environment configurations and prepare volumes.
**Windows:**
`.\scripts\windows\bootstrap.ps1`
**Linux:**
`./scripts/linux\bootstrap.sh`

### 2. Run the Stack

Start the local development stack (builds Docker images and mounts local volumes).
**Windows:**
`.\scripts\windows\dev.ps1`
**Linux:**
`./scripts/linux\dev.sh`

### 3. Database Migrations

Migrations run automatically via the `sp_migrate` container, but you can manually trigger them if necessary.
**Windows:**
`.\scripts\windows\migrate.ps1`
**Linux:**
`./scripts/linux\migrate.sh`

### Essential Endpoints

- **Frontend UI**: http://localhost:8080
- **API Gateway docs**: http://localhost:8000/docs
- **Grafana Dashboards**: http://localhost:3000
- **Prometheus Targets**: http://localhost:9090

## 🔧 Environment Configuration

Copy `.env.example` to `.env`. Key variables to tune:

- `POSTGRES_USER` / `POSTGRES_PASSWORD`: Target DB credentials.
- `OLLAMA_URL`: Local LLM pointer (defaults to `http://sp_llm_service:11434`).
- `LANGCHAIN_API_KEY`: Required if LangSmith tracing is preferred. Set `LANGCHAIN_TRACING_V2=true`.
- `CELERY_BROKER_URL`: Local Redis cluster URL for the gateway-worker queues.

## 🚨 Troubleshooting

- **Missing Ollama Models:** If the LangGraph nodes raise `ModelNotFoundError`, verify that the model was successfully pulled. You can manually execute: `docker exec -it sp_llm_service ollama pull <model_name>`.
- **Dimension Mismatch / pgvector Errors:** This generally means your Postgres volume did not initialize with vector extensions. Stop containers, remove the postgres volume, and redeploy. The `01-init-pgvector.sql` script relies on a clean initialization.
- **Async Tasks Pending Forever:** Ensure the `sp_celery_worker` and `supportpilot-redis` containers are healthy. The UI relies on `use-job-polling.ts` to fetch async results. Check gateway logs to worker connectivity.

---

## Running Services Individually (No Docker)

Use this quickstart when you want to run only the API gateway and the frontend locally. These steps assume Windows PowerShell. Adjust activation steps for other shells.

1. Start the API gateway

```powershell
cd api-gateway
python -m venv .venv
. .venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn api_gateway.main:app --reload --host 0.0.0.0 --port 8000
```

2. Start the frontend dev server

```powershell
cd frontend
npm install
# Optional: point dev frontend at the running gateway
$env:REACT_APP_API_URL = "http://localhost:8000"
npm run dev
```

3. Verify the stack

```bash
curl http://localhost:8000/api/health
# Open the frontend URL shown by npm run dev
```
