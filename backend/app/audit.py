from __future__ import annotations

import json
from typing import Any

from fastapi import Request
from sqlalchemy.orm import Session

from app.models import AuditEvent, User


def _safe_json(value: Any) -> str | None:
    if value is None:
        return None
    try:
        return json.dumps(value, ensure_ascii=False, default=str)
    except Exception:
        return None


def log_event(
    *,
    session: Session,
    request: Request | None,
    user: User | None,
    action: str,
    entity: str,
    entity_id: int | None = None,
    summary: str | None = None,
    before: Any | None = None,
    after: Any | None = None,
) -> None:
    ip = None
    if request is not None:
        ip = request.client.host if request.client else None

    ev = AuditEvent(
        user_id=user.id if user else None,
        username=user.username if user else None,
        ip=ip,
        action=action,
        entity=entity,
        entity_id=entity_id,
        summary=summary,
        before_json=_safe_json(before),
        after_json=_safe_json(after),
    )
    session.add(ev)

