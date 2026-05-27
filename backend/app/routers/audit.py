from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select

from app.db import get_session
from app.deps import require_admin
from app.models import AuditEvent
from app.schemas import AuditOut


router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("", response_model=list[AuditOut])
def list_audit(
    q: str | None = Query(default=None, max_length=120),
    entity: str | None = None,
    action: str | None = None,
    username: str | None = None,
    limit: int = Query(default=200, ge=1, le=2000),
    _: object = Depends(require_admin),
):
    with get_session() as session:
        stmt = select(AuditEvent).order_by(AuditEvent.created_at.desc()).limit(limit)
        if entity:
            stmt = stmt.where(AuditEvent.entity == entity)
        if action:
            stmt = stmt.where(AuditEvent.action == action)
        if username:
            stmt = stmt.where(AuditEvent.username == username)
        if q:
            stmt = stmt.where(AuditEvent.summary.ilike(f"%{q}%"))
        rows = session.scalars(stmt).all()
        return [
            AuditOut(
                id=r.id,
                created_at=r.created_at,
                user_id=r.user_id,
                username=r.username,
                ip=r.ip,
                action=r.action,
                entity=r.entity,
                entity_id=r.entity_id,
                summary=r.summary,
                before_json=r.before_json,
                after_json=r.after_json,
            )
            for r in rows
        ]

