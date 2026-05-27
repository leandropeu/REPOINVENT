from __future__ import annotations

import os
from pathlib import Path
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.settings import settings


class Base(DeclarativeBase):
    pass


def _ensure_sqlite_dir(database_url: str) -> None:
    if not database_url.startswith("sqlite:///"):
        return
    path = database_url.removeprefix("sqlite:///")
    dirpath = str(Path(path).parent)
    if dirpath and dirpath not in (".", ""):
        os.makedirs(dirpath, exist_ok=True)

def _normalize_sqlite_url(database_url: str) -> str:
    if not database_url.startswith("sqlite:///"):
        return database_url
    path = database_url.removeprefix("sqlite:///")
    # If relative path, pin it to the backend directory (not the process CWD)
    p = Path(path)
    if not p.is_absolute():
        backend_dir = Path(__file__).resolve().parents[1]  # .../backend
        p = (backend_dir / p).resolve()
        return "sqlite:///" + p.as_posix()
    return database_url


normalized_database_url = _normalize_sqlite_url(settings.database_url)
_ensure_sqlite_dir(normalized_database_url)

engine = create_engine(
    normalized_database_url,
    connect_args={"check_same_thread": False} if normalized_database_url.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@contextmanager
def get_session() -> Session:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
