from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select

from app.db import get_session
from app.deps import get_current_user, require_admin
from app.models import Unit
from app.schemas import UnitCreate, UnitOut, UnitUpdate
from app.audit import log_event


router = APIRouter(prefix="/units", tags=["units"])


@router.get("", response_model=list[UnitOut])
def list_units(
    q: str | None = Query(default=None, max_length=120),
    _: object = Depends(get_current_user),
):
    with get_session() as session:
        stmt = select(Unit).order_by(Unit.name.asc())
        if q:
            stmt = stmt.where(Unit.name.ilike(f"%{q}%"))
        items = session.scalars(stmt).all()
        return [
            UnitOut(
                id=u.id,
                name=u.name,
                external_id=u.external_id,
                cnpj=u.cnpj,
                address=u.address,
                created_at=u.created_at,
            )
            for u in items
        ]


@router.post("", response_model=UnitOut, status_code=status.HTTP_201_CREATED)
def create_unit(payload: UnitCreate, request: Request, user=Depends(get_current_user)):
    with get_session() as session:
        unit = Unit(
            name=payload.name.strip(),
            external_id=(payload.external_id.strip() if payload.external_id else None),
            cnpj=(payload.cnpj.strip() if payload.cnpj else None),
            address=(payload.address.strip() if payload.address else None),
        )
        session.add(unit)
        try:
            session.commit()
        except Exception:
            session.rollback()
            raise HTTPException(status_code=400, detail="Não foi possível criar a unidade (nome duplicado?)")
        session.refresh(unit)
        log_event(
            session=session,
            request=request,
            user=user,
            action="CREATE",
            entity="units",
            entity_id=unit.id,
            summary=f'Criou unidade "{unit.name}"',
            after={"id": unit.id, "name": unit.name, "external_id": unit.external_id, "cnpj": unit.cnpj, "address": unit.address},
        )
        session.commit()
        return UnitOut(
            id=unit.id,
            name=unit.name,
            external_id=unit.external_id,
            cnpj=unit.cnpj,
            address=unit.address,
            created_at=unit.created_at,
        )


@router.put("/{unit_id}", response_model=UnitOut)
def update_unit(unit_id: int, payload: UnitUpdate, request: Request, user=Depends(require_admin)):
    with get_session() as session:
        unit = session.get(Unit, unit_id)
        if not unit:
            raise HTTPException(status_code=404, detail="Unidade não encontrada")
        before = {"id": unit.id, "name": unit.name, "external_id": unit.external_id, "cnpj": unit.cnpj, "address": unit.address}
        if payload.name is not None:
            unit.name = payload.name.strip()
        if payload.external_id is not None:
            unit.external_id = payload.external_id.strip() if payload.external_id else None
        if payload.cnpj is not None:
            unit.cnpj = payload.cnpj.strip() if payload.cnpj else None
        if payload.address is not None:
            unit.address = payload.address.strip() if payload.address else None
        try:
            session.commit()
        except Exception:
            session.rollback()
            raise HTTPException(status_code=400, detail="Não foi possível atualizar a unidade")
        session.refresh(unit)
        after = {"id": unit.id, "name": unit.name, "external_id": unit.external_id, "cnpj": unit.cnpj, "address": unit.address}
        log_event(
            session=session,
            request=request,
            user=user,
            action="UPDATE",
            entity="units",
            entity_id=unit.id,
            summary=f'Atualizou unidade "{unit.name}"',
            before=before,
            after=after,
        )
        session.commit()
        return UnitOut(
            id=unit.id,
            name=unit.name,
            external_id=unit.external_id,
            cnpj=unit.cnpj,
            address=unit.address,
            created_at=unit.created_at,
        )


@router.delete("/{unit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_unit(unit_id: int, request: Request, user=Depends(require_admin)):
    with get_session() as session:
        unit = session.get(Unit, unit_id)
        if not unit:
            raise HTTPException(status_code=404, detail="Unidade não encontrada")
        before = {"id": unit.id, "name": unit.name, "external_id": unit.external_id, "cnpj": unit.cnpj, "address": unit.address}
        session.delete(unit)
        session.commit()
        log_event(
            session=session,
            request=request,
            user=user,
            action="DELETE",
            entity="units",
            entity_id=unit_id,
            summary=f'Removeu unidade "{before.get("name")}"',
            before=before,
        )
        session.commit()
        return None
