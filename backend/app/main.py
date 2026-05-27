from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import Base, engine, ensure_sqlite_schema
from app.routers import auth, audit, equipment, reports, stats, units, users
from app.settings import settings


def create_app() -> FastAPI:
    app = FastAPI(title="REPOINVENT API")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

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
