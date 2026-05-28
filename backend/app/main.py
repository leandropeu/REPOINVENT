from __future__ import annotations

import logging
import warnings
from logging.handlers import RotatingFileHandler
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from sqlalchemy.exc import OperationalError
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.db import Base, engine, ensure_sqlite_schema
from app.instance_lock import InstanceLockError, acquire_instance_lock
from app.routers import auth, audit, equipment, reports, stats, units, users
from app.security import is_secret_key_weak
from app.settings import settings

logger = logging.getLogger("repoinvent.security")


def configure_security_logger() -> None:
    logs_dir = Path(__file__).resolve().parents[1] / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_file = logs_dir / "security.log"

    if any(isinstance(handler, RotatingFileHandler) for handler in logger.handlers):
        return

    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=10, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    logger.propagate = False


def create_app() -> FastAPI:
    app = FastAPI(title="REPOINVENT API")
    configure_security_logger()

    if settings.enforce_single_backend_instance:
        try:
            acquire_instance_lock(settings.instance_lock_file)
        except InstanceLockError as exc:
            raise RuntimeError(str(exc))

    if is_secret_key_weak(settings.secret_key, settings.min_secret_key_length):
        msg = f"SECRET_KEY fraca. Defina pelo menos {settings.min_secret_key_length} caracteres aleatórios."
        if settings.enforce_strong_secret_key:
            raise RuntimeError(msg)
        warnings.warn(msg)

    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.trusted_hosts_list or ["127.0.0.1", "localhost"])
    if settings.force_https:
        app.add_middleware(HTTPSRedirectMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        try:
            response: Response = await call_next(request)
        except OperationalError as exc:
            text = str(exc).lower()
            if "database is locked" in text or "database table is locked" in text:
                logger.warning("sqlite_locked path=%s method=%s", request.url.path, request.method)
                return JSONResponse(status_code=503, content={"detail": "Banco ocupado. Tente novamente em instantes."})
            raise
        if settings.secure_headers_enabled:
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
            response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
            response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "connect-src 'self' http://127.0.0.1:8010 http://localhost:8010; "
                "img-src 'self' data: blob:; "
                "style-src 'self' 'unsafe-inline'; "
                "script-src 'self'; "
                "frame-ancestors 'none'"
            )
        status_code = int(response.status_code)
        if status_code in (401, 403, 429) or status_code >= 500:
            logger.warning(
                "security_event status=%s method=%s path=%s ip=%s",
                status_code,
                request.method,
                request.url.path,
                (request.client.host if request.client else "unknown"),
            )
        return response

    Base.metadata.create_all(bind=engine)
    ensure_sqlite_schema()

    app.include_router(auth.router)
    app.include_router(audit.router)
    app.include_router(stats.router)
    app.include_router(units.router)
    app.include_router(equipment.router)
    app.include_router(users.router)
    app.include_router(reports.router)

    return app


app = create_app()
