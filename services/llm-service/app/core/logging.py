import json
import logging
import sys
from datetime import datetime


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "service": "llm-service",
            "message": record.getMessage(),
        }

        if hasattr(record, "request_id"):
            log_record["request_id"] = record.request_id

        if hasattr(record, "latency_ms"):
            log_record["latency_ms"] = record.latency_ms

        return json.dumps(log_record)


logger = logging.getLogger("llm-service")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JsonFormatter())

logger.handlers.clear()
logger.addHandler(handler)
logger.propagate = False


def configure_logging() -> None:
    """
    Initializes structured JSON logging for service startup.
    Logger is already configured globally above.
    """
    return None