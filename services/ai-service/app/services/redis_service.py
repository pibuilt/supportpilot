import json
import redis
from typing import Optional, Any

from app.core.logging import log_info, log_error


class RedisService:
    def __init__(
        self,
        host: str = "redis",
        port: int = 6379,
        db: int = 0,
        ttl: int = 86400,
    ):
        self.ttl = ttl

        try:
            self.client = redis.Redis(
                host=host,
                port=port,
                db=db,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
            )

            self.client.ping()
            log_info("Redis connection established successfully.")

        except Exception as e:
            log_error(f"Redis connection failed: {str(e)}")
            self.client = None

    def is_available(self) -> bool:
        return self.client is not None

    def _format_key(self, key: str) -> str:
        return f"supportpilot:{key}"

    def set_data(self, key: str, value: Any) -> bool:
        if not self.client:
            return False

        try:
            formatted_key = self._format_key(key)
            serialized = json.dumps(value)

            self.client.setex(
                formatted_key,
                self.ttl,
                serialized,
            )

            return True

        except Exception as e:
            log_error(f"Redis set failed for key {key}: {str(e)}")
            return False

    def get_data(self, key: str) -> Optional[Any]:
        if not self.client:
            return None

        try:
            formatted_key = self._format_key(key)
            data = self.client.get(formatted_key)

            if not data:
                return None

            return json.loads(data)

        except Exception as e:
            log_error(f"Redis get failed for key {key}: {str(e)}")
            return None

    def delete_data(self, key: str) -> bool:
        if not self.client:
            return False

        try:
            formatted_key = self._format_key(key)
            self.client.delete(formatted_key)
            return True

        except Exception as e:
            log_error(f"Redis delete failed for key {key}: {str(e)}")
            return False

    def ping(self) -> bool:
        if not self.client:
            return False

        try:
            return self.client.ping()

        except Exception:
            return False