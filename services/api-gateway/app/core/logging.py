import json
import logging
import sys
from datetime import datetime, time

logger = logging.getLogger("supportpilot")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)

# prevent duplicate logs
logger.propagate = False

if not logger.handlers:
    logger.addHandler(handler)


def format_log(level, message, request_id=None, latency_ms=None):
    return json.dumps({
        "timestamp": datetime.utcnow().isoformat(),
        "level": level,
        "service": "api-gateway",
        "request_id": request_id,
        "message": message,
        "latency_ms": latency_ms
    })


def log_info(message, request_id=None, latency_ms=None):
    logger.info(format_log("INFO", message, request_id, latency_ms))


def log_error(message, request_id=None):
    logger.error(format_log("ERROR", message, request_id))