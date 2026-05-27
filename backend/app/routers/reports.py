from __future__ import annotations

import csv
import io
from datetime import datetime, timezone
from xml.etree import ElementTree as ET

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select

from app.db import get_session
from app.deps import require_admin
from app.models import AuditEvent, Equipment, Unit, User


router = APIRouter(prefix="/reports", tags=["reports"])


def _attachment_response(*, filename: str, media_type: str, content: bytes | str) -> StreamingResponse:
    payload = content.encode("utf-8") if isinstance(content, str) else content
    return StreamingResponse(
        iter([payload]),
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


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
    return _attachment_response(filename=filename, media_type="text/csv; charset=utf-8", content=buf.getvalue())


def _xml_response(filename: str, rows: list[dict]) -> StreamingResponse:
    root = ET.Element("rows")
    for row in rows:
        el = ET.SubElement(root, "row")
        for k, v in row.items():
            child = ET.SubElement(el, str(k))
            child.text = "" if v is None else str(v)
    xml_bytes = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    return _attachment_response(filename=filename, media_type="application/xml; charset=utf-8", content=xml_bytes)


def _xlsx_response(filename: str, rows: list[dict]) -> StreamingResponse:
    try:
        from openpyxl import Workbook
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dependência ausente para XLSX: {e}")

    wb = Workbook()
    ws = wb.active
    ws.title = "export"

    if not rows:
        ws.append(["empty"])
    else:
        headers = list(rows[0].keys())
        ws.append(headers)
        for row in rows:
            ws.append([row.get(h, "") for h in headers])

    bio = io.BytesIO()
    wb.save(bio)
    bio.seek(0)
    return _attachment_response(
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        content=bio.getvalue(),
    )


def _pdf_response(filename: str, rows: list[dict], *, title: str) -> StreamingResponse:
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dependência ausente para PDF: {e}")

    bio = io.BytesIO()
    doc = SimpleDocTemplate(bio, pagesize=landscape(A4), title=title)
    styles = getSampleStyleSheet()

    story: list[object] = []
    story.append(Paragraph(title, styles["Title"]))
    story.append(Spacer(1, 8))
    story.append(Paragraph(f"Gerado em {datetime.now(timezone.utc).isoformat()}", styles["Normal"]))
    story.append(Spacer(1, 12))

    if not rows:
        data = [["empty"]]
    else:
        headers = list(rows[0].keys())
        data = [headers] + [[str(row.get(h, "") or "") for h in headers] for row in rows]

    table = Table(data, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cbd5e1")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    story.append(table)
    doc.build(story)
    bio.seek(0)
    return _attachment_response(filename=filename, media_type="application/pdf", content=bio.getvalue())


def _units_rows(session) -> list[dict]:
    units = session.scalars(select(Unit).order_by(Unit.name.asc())).all()
    return [
        {"id": u.id, "name": u.name, "external_id": u.external_id or "", "cnpj": u.cnpj or "", "address": u.address or ""}
        for u in units
    ]


def _equipment_rows(session) -> list[dict]:
    items = session.scalars(select(Equipment).order_by(Equipment.updated_at.desc())).all()
    return [
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
            "operator": getattr(e, "operator", "") or "",
            "contract": getattr(e, "contract", "") or "",
            "warranty": int(bool(getattr(e, "warranty", False))),
            "warranty_expires_at": (getattr(e, "warranty_expires_at", None).isoformat() if getattr(e, "warranty_expires_at", None) else ""),
            "notes": (e.notes or "").replace("\n", " ").strip(),
            "created_at": e.created_at.isoformat(),
            "updated_at": e.updated_at.isoformat(),
        }
        for e in items
    ]


def _users_rows(session) -> list[dict]:
    users = session.scalars(select(User).order_by(User.created_at.desc())).all()
    return [
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


def _audit_rows(session, *, limit: int) -> list[dict]:
    events = session.scalars(select(AuditEvent).order_by(AuditEvent.created_at.desc()).limit(limit)).all()
    return [
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


def _dispatch_export(*, resource: str, fmt: str, rows: list[dict]) -> StreamingResponse:
    res = resource.lower()
    ext = fmt.lower()
    filename = f"{res}.{ext}"
    if ext == "csv":
        return _csv_response(filename, rows)
    if ext == "xml":
        return _xml_response(filename, rows)
    if ext == "xlsx":
        return _xlsx_response(filename, rows)
    if ext == "pdf":
        title = f"Relatorio - {res}"
        return _pdf_response(filename, rows, title=title)
    raise HTTPException(status_code=400, detail="Formato inválido")


@router.get("/{resource}.{fmt}")
def export_generic(
    resource: str,
    fmt: str,
    limit: int = Query(default=2000, ge=1, le=10000),
    _: object = Depends(require_admin),
):
    resource = resource.lower()
    fmt = fmt.lower()
    if resource not in {"units", "equipment", "users", "audit"}:
        raise HTTPException(status_code=404, detail="Relatório não encontrado")
    with get_session() as session:
        if resource == "units":
            rows = _units_rows(session)
        elif resource == "equipment":
            rows = _equipment_rows(session)
        elif resource == "users":
            rows = _users_rows(session)
        else:
            rows = _audit_rows(session, limit=limit)
        return _dispatch_export(resource=resource, fmt=fmt, rows=rows)


# Starlette/FastAPI path params are greedy; the pattern `/{resource}.{fmt}` may not match as expected.
# Provide an explicit non-ambiguous alternative route.
@router.get("/{resource}/export/{fmt}")
def export_generic_alt(
    resource: str,
    fmt: str,
    limit: int = Query(default=2000, ge=1, le=10000),
    _: object = Depends(require_admin),
):
    resource = resource.lower()
    fmt = fmt.lower()
    if resource not in {"units", "equipment", "users", "audit"}:
        raise HTTPException(status_code=404, detail="Relatório não encontrado")
    with get_session() as session:
        if resource == "units":
            rows = _units_rows(session)
        elif resource == "equipment":
            rows = _equipment_rows(session)
        elif resource == "users":
            rows = _users_rows(session)
        else:
            rows = _audit_rows(session, limit=limit)
        return _dispatch_export(resource=resource, fmt=fmt, rows=rows)


@router.get("/units.csv")
def units_csv(_: object = Depends(require_admin)):
    with get_session() as session:
        rows = _units_rows(session)
        return _csv_response("units.csv", rows)


@router.get("/equipment.csv")
def equipment_csv(_: object = Depends(require_admin)):
    with get_session() as session:
        rows = _equipment_rows(session)
        return _csv_response("equipment.csv", rows)


@router.get("/users.csv")
def users_csv(_: object = Depends(require_admin)):
    with get_session() as session:
        rows = _users_rows(session)
        return _csv_response("users.csv", rows)


@router.get("/audit.csv")
def audit_csv(
    limit: int = Query(default=2000, ge=1, le=10000),
    _: object = Depends(require_admin),
):
    with get_session() as session:
        rows = _audit_rows(session, limit=limit)
        return _csv_response("audit.csv", rows)

