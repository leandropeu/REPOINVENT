from __future__ import annotations

import datetime as dt
import os
import shutil
from pathlib import Path


def backup_sqlite(*, src_db_path: Path, backup_dir: Path, keep_days: int = 14) -> Path:
    backup_dir.mkdir(parents=True, exist_ok=True)
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    dst = backup_dir / f"{src_db_path.stem}_{ts}{src_db_path.suffix}"
    shutil.copy2(src_db_path, dst)

    cutoff = dt.datetime.now() - dt.timedelta(days=keep_days)
    for p in backup_dir.glob(f"{src_db_path.stem}_*{src_db_path.suffix}"):
        try:
            mtime = dt.datetime.fromtimestamp(p.stat().st_mtime)
            if mtime < cutoff:
                p.unlink(missing_ok=True)
        except Exception:
            continue

    return dst

