from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import secrets

from jose import jwt
from passlib.context import CryptContext

from app.settings import settings


pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_access_token(*, subject: str, minutes: int | None = None) -> str:
    expire_minutes = minutes if minutes is not None else settings.access_token_expire_minutes
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=expire_minutes)
    payload = {
        "sub": subject,
        "typ": "access",
        "iat": now,
        "nbf": now,
        "exp": expire,
        "jti": secrets.token_urlsafe(16),
    }
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def create_refresh_token(*, subject: str, minutes: int | None = None) -> str:
    expire_minutes = minutes if minutes is not None else settings.refresh_token_expire_minutes
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=expire_minutes)
    payload = {
        "sub": subject,
        "typ": "refresh",
        "iat": now,
        "nbf": now,
        "exp": expire,
        "jti": secrets.token_urlsafe(24),
    }
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.secret_key, algorithms=["HS256"])


def hash_jti(jti: str) -> str:
    return hashlib.sha256(jti.encode("utf-8")).hexdigest()


def is_secret_key_weak(secret_key: str, min_length: int) -> bool:
    if not secret_key or len(secret_key) < min_length:
        return True
    lower = secret_key.lower()
    if lower.startswith("change_me") or lower in {"secret", "changeme", "password"}:
        return True
    return False
