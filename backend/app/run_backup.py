from __future__ import annotations

import argparse
from pathlib import Path

from app.backup import backup_sqlite
from app.db import normalized_database_url


def _db_path_from_url(database_url: str) -> Path:
    if not database_url.startswith("sqlite:///"):
        raise SystemExit("Somente SQLite suportado para backup automático.")
    path = database_url.removeprefix("sqlite:///")
    return Path(path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Backup do SQLite do REPOINVENT.")
    parser.add_argument("--backup-dir", default="backups", help="Diretório de backups (relativo a backend/).")
    parser.add_argument("--keep-days", type=int, default=14)
    args = parser.parse_args()

    db_path = _db_path_from_url(normalized_database_url)
    if not db_path.exists():
        raise SystemExit(f"DB não encontrado: {db_path}")

    backup_dir = (Path(__file__).resolve().parents[1] / args.backup_dir).resolve()
    out = backup_sqlite(src_db_path=db_path, backup_dir=backup_dir, keep_days=args.keep_days)
    print(str(out))


if __name__ == "__main__":
    main()

