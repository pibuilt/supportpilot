from prometheus_client import (
    Counter,
    Histogram,
)

REQUEST_COUNT = Counter(
    "supportpilot_requests_total",
    "Total API requests",
    ["method", "endpoint"],
)

REQUEST_LATENCY = Histogram(
    "supportpilot_request_duration_seconds",
    "Request latency",
    ["endpoint"],
)

INGESTION_COUNT = Counter(
    "supportpilot_ingestions_total",
    "Documents successfully ingested",
)

ANALYSIS_COUNT = Counter(
    "supportpilot_contract_analyses_total",
    "Contract analyses executed",
)

ORCHESTRATION_COUNT = Counter(
    "supportpilot_orchestrations_total",
    "Orchestration requests executed",
)

RETRIEVAL_COUNT = Counter(
    "supportpilot_retrievals_total",
    "Vector retrieval executions",
)

LLM_COUNT = Counter(
    "supportpilot_llm_calls_total",
    "LLM requests executed",
)