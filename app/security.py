import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from typing import Any, Dict

from app.config import settings

HASH_ITERATIONS = 100_000


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        HASH_ITERATIONS,
    )
    return f"{_b64url_encode(salt)}${_b64url_encode(password_hash)}"


def verify_password(password: str, hashed_password: str) -> bool:
    try:
        salt_part, hash_part = hashed_password.split("$", 1)
    except ValueError:
        return False

    salt = _b64url_decode(salt_part)
    expected_hash = _b64url_decode(hash_part)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        HASH_ITERATIONS,
    )
    return hmac.compare_digest(password_hash, expected_hash)


def create_access_token(payload: Dict[str, Any], expires_seconds: int = settings.access_token_expire_seconds) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    token_payload = payload.copy()
    token_payload["exp"] = int(time.time()) + expires_seconds

    header_part = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_part = _b64url_encode(json.dumps(token_payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_part}.{payload_part}".encode("utf-8")
    signature = hmac.new(
        settings.secret_key.encode("utf-8"),
        signing_input,
        hashlib.sha256,
    ).digest()
    signature_part = _b64url_encode(signature)
    return f"{header_part}.{payload_part}.{signature_part}"


def create_refresh_token() -> str:
    return secrets.token_urlsafe(48)


def decode_access_token(token: str) -> Dict[str, Any]:
    try:
        header_part, payload_part, signature_part = token.split(".")
    except ValueError as exc:
        raise ValueError("Invalid token") from exc

    signing_input = f"{header_part}.{payload_part}".encode("utf-8")
    expected_signature = hmac.new(
        settings.secret_key.encode("utf-8"),
        signing_input,
        hashlib.sha256,
    ).digest()
    received_signature = _b64url_decode(signature_part)
    if not hmac.compare_digest(expected_signature, received_signature):
        raise ValueError("Invalid token signature")

    payload_bytes = _b64url_decode(payload_part)
    payload = json.loads(payload_bytes.decode("utf-8"))
    exp = int(payload.get("exp", 0))
    if exp < int(time.time()):
        raise ValueError("Token expired")

    return payload
