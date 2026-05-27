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


def ensure_sqlite_schema() -> None:
    """
    Minimal forward-only schema patching for SQLite deployments.
    `Base.metadata.create_all()` does not add new columns to existing tables.
    """
    if not normalized_database_url.startswith("sqlite"):
        return

    import sqlite3

    db_path = normalized_database_url.removeprefix("sqlite:///")
    con = sqlite3.connect(db_path)
    try:
        cur = con.cursor()
        tables = {r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        if "equipment" in tables:
            cols = {r[1] for r in cur.execute("PRAGMA table_info(equipment)").fetchall()}
            if "warranty" not in cols:
                cur.execute("ALTER TABLE equipment ADD COLUMN warranty INTEGER NOT NULL DEFAULT 0")
            if "warranty_expires_at" not in cols:
                cur.execute("ALTER TABLE equipment ADD COLUMN warranty_expires_at DATE NULL")
            if "operator" not in cols:
                cur.execute("ALTER TABLE equipment ADD COLUMN operator TEXT NULL")
            if "contract" not in cols:
                cur.execute("ALTER TABLE equipment ADD COLUMN contract TEXT NULL")
        con.commit()
    finally:
        con.close()


@contextmanager
def get_session() -> Session:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
