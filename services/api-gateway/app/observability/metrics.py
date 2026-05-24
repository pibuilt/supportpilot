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