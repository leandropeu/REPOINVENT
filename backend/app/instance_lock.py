from __future__ import annotations

import atexit
import os
from pathlib import Path


class InstanceLockError(RuntimeError):
    pass


_lock_path: Path | None = None


def _pid_is_running(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def acquire_instance_lock(path_str: str) -> None:
    global _lock_path
    path = Path(path_str)
    if not path.is_absolute():
        path = (Path(__file__).resolve().parents[1] / path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        fd = os.open(str(path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(str(os.getpid()))
    except FileExistsError:
        try:
            raw = path.read_text(encoding="utf-8").strip()
            old_pid = int(raw) if raw else 0
        except Exception:
            old_pid = 0

        if old_pid and not _pid_is_running(old_pid):
            path.unlink(missing_ok=True)
            fd = os.open(str(path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(str(os.getpid()))
        else:
            raise InstanceLockError(f"Backend ja em execucao (lock: {path})")

    _lock_path = path
    atexit.register(release_instance_lock)


def release_instance_lock() -> None:
    global _lock_path
    if _lock_path is None:
        return
    try:
        _lock_path.unlink(missing_ok=True)
    finally:
        _lock_path = None
