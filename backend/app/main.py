from __future__ import annotations

import warnings

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.db import Base, engine, ensure_sqlite_schema
from app.routers import auth, audit, equipment, reports, stats, units, users
from app.security import is_secret_key_weak
from app.settings import settings


def create_app() -> FastAPI:
    app = FastAPI(title="REPOINVENT API")

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
        response: Response = await call_next(request)
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
