from __future__ import annotations

import csv
import io
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select

from app.db import get_session
from app.deps import require_admin
from app.models import AuditEvent, Equipment, Unit, User


router = APIRouter(prefix="/reports", tags=["reports"])


def _csv_response(filename: str, rows: list[dict]) -> StreamingResponse:
    buf = io.StringIO()
    if not rows:
        writer = csv.writer(buf)
        writer.writerow(["empty"])
    else:
        fieldnames = list(rows[0].keys())
        writer = csv.DictWriter(buf, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/units.csv")
def units_csv(_: object = Depends(require_admin)):
    with get_session() as session:
        units = session.scalars(select(Unit).order_by(Unit.name.asc())).all()
        rows = [
            {"id": u.id, "name": u.name, "external_id": u.external_id or "", "cnpj": u.cnpj or "", "address": u.address or ""}
            for u in units
        ]
        return _csv_response("units.csv", rows)


@router.get("/equipment.csv")
def equipment_csv(_: object = Depends(require_admin)):
    with get_session() as session:
        items = session.scalars(select(Equipment).order_by(Equipment.updated_at.desc())).all()
        rows = [
            {
                "id": e.id,
                "unit_id": e.unit_id,
                "type": e.type,
                "name": e.name,
                "brand": e.brand or "",
                "asset_tag": e.asset_tag or "",
                "serial": e.serial or "",
                "imei": e.imei or "",
                "phone_number": e.phone_number or "",
                "notes": (e.notes or "").replace("\n", " ").strip(),
                "created_at": e.created_at.isoformat(),
                "updated_at": e.updated_at.isoformat(),
            }
            for e in items
        ]
        return _csv_response("equipment.csv", rows)


@router.get("/users.csv")
def users_csv(_: object = Depends(require_admin)):
    with get_session() as session:
        users = session.scalars(select(User).order_by(User.created_at.desc())).all()
        rows = [
            {
                "id": u.id,
                "name": u.name,
                "username": u.username,
                "is_admin": int(bool(u.is_admin)),
                "is_active": int(bool(u.is_active)),
                "created_at": u.created_at.isoformat(),
            }
            for u in users
        ]
        return _csv_response("users.csv", rows)


@router.get("/audit.csv")
def audit_csv(
    limit: int = Query(default=2000, ge=1, le=10000),
    _: object = Depends(require_admin),
):
    with get_session() as session:
        events = session.scalars(select(AuditEvent).order_by(AuditEvent.created_at.desc()).limit(limit)).all()
        rows = [
            {
                "id": e.id,
                "created_at": e.created_at.isoformat(),
                "username": e.username or "",
                "ip": e.ip or "",
                "action": e.action,
                "entity": e.entity,
                "entity_id": e.entity_id or "",
                "summary": e.summary or "",
            }
            for e in events
        ]
        return _csv_response("audit.csv", rows)

