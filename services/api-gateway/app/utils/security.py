import hashlib
import secrets


def generate_api_key() -> str:
    return f"sp_{secrets.token_urlsafe(32)}"


def hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode()).hexdigest()


def get_key_prefix(api_key: str) -> str:
    return api_key[:12]