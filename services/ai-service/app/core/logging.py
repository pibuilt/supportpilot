import json
import logging
import sys
from datetime import datetime


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "service": "ai-service",
            "message": record.getMessage(),
        }

        if hasattr(record, "request_id"):
            log_record["request_id"] = record.request_id

        if hasattr(record, "latency_ms"):
            log_record["latency_ms"] = record.latency_ms

        return json.dumps(log_record)


logger = logging.getLogger("ai-service")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JsonFormatter())

logger.handlers.clear()
logger.addHandler(handler)
logger.propagate = False


def log_info(message, request_id=None, latency_ms=None):
    logger.info(
        message,
        extra={
            "request_id": request_id,
            "latency_ms": latency_ms,
        },
    )


def log_error(message, request_id=None):
    logger.error(
        message,
        extra={
            "request_id": request_id,
        },
    )