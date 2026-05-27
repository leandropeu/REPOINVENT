from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import func, select

from app.db import get_session
from app.deps import get_current_user, require_admin
from app.models import Equipment, Unit
from app.schemas import EquipmentCreate, EquipmentOut, EquipmentUpdate
from app.audit import log_event


router = APIRouter(prefix="/equipment", tags=["equipment"])


@router.get("", response_model=list[EquipmentOut])
def list_equipment(
    q: str | None = Query(default=None, max_length=120),
    unit_id: int | None = None,
    type: str | None = None,
    limit: int = Query(default=500, ge=1, le=5000),
    _: object = Depends(get_current_user),
):
    with get_session() as session:
        stmt = select(Equipment).order_by(Equipment.updated_at.desc()).limit(limit)
        if q:
            like = f"%{q}%"
            stmt = stmt.where(
                Equipment.name.ilike(like)
                | Equipment.brand.ilike(like)
                | Equipment.asset_tag.ilike(like)
                | Equipment.serial.ilike(like)
                | Equipment.imei.ilike(like)
                | Equipment.phone_number.ilike(like)
            )
        if unit_id:
            stmt = stmt.where(Equipment.unit_id == unit_id)
        if type:
            stmt = stmt.where(Equipment.type == type)
        items = session.scalars(stmt).all()
        return [
            EquipmentOut(
                id=e.id,
                unit_id=e.unit_id,
                type=e.type,
                name=e.name,
                brand=e.brand,
                asset_tag=e.asset_tag,
                serial=e.serial,
                imei=e.imei,
                phone_number=e.phone_number,
                operator=getattr(e, "operator", None),
                contract=getattr(e, "contract", None),
                warranty=e.warranty,
                warranty_expires_at=e.warranty_expires_at,
                notes=e.notes,
                created_at=e.created_at,
                updated_at=e.updated_at,
            )
            for e in items
        ]


@router.post("", response_model=EquipmentOut, status_code=status.HTTP_201_CREATED)
def create_equipment(payload: EquipmentCreate, request: Request, user=Depends(get_current_user)):
    with get_session() as session:
        unit = session.get(Unit, payload.unit_id)
        if not unit:
            raise HTTPException(status_code=400, detail="Unidade inválida")
        if payload.warranty_expires_at and not payload.warranty:
            raise HTTPException(status_code=400, detail="Não é possível definir vencimento sem garantia")
        item = Equipment(
            unit_id=payload.unit_id,
            type=payload.type.strip().upper(),
            name=payload.name.strip(),
            brand=(payload.brand.strip() if payload.brand else None),
            asset_tag=(payload.asset_tag.strip() if payload.asset_tag else None),
            serial=(payload.serial.strip() if payload.serial else None),
            imei=(payload.imei.strip() if payload.imei else None),
            phone_number=(payload.phone_number.strip() if payload.phone_number else None),
            operator=(payload.operator.strip() if payload.operator else None),
            contract=(payload.contract.strip() if payload.contract else None),
            warranty=bool(payload.warranty),
            warranty_expires_at=(payload.warranty_expires_at if payload.warranty else None),
            notes=(payload.notes.strip() if payload.notes else None),
        )
        session.add(item)
        try:
            session.commit()
        except Exception:
            session.rollback()
            raise HTTPException(status_code=400, detail="Não foi possível salvar (patrimônio duplicado?)")
        session.refresh(item)
        log_event(
            session=session,
            request=request,
            user=user,
            action="CREATE",
            entity="equipment",
            entity_id=item.id,
            summary=f'Criou equipamento "{item.name}" ({item.type})',
            after={
                "id": item.id,
                "unit_id": item.unit_id,
                "type": item.type,
                "name": item.name,
                "brand": item.brand,
                "asset_tag": item.asset_tag,
                "serial": item.serial,
                "imei": item.imei,
                "phone_number": item.phone_number,
                "operator": item.operator,
                "contract": item.contract,
                "warranty": item.warranty,
                "warranty_expires_at": str(item.warranty_expires_at) if item.warranty_expires_at else None,
                "notes": item.notes,
            },
        )
        session.commit()
        return EquipmentOut(
            id=item.id,
            unit_id=item.unit_id,
            type=item.type,
            name=item.name,
            brand=item.brand,
            asset_tag=item.asset_tag,
            serial=item.serial,
            imei=item.imei,
            phone_number=item.phone_number,
            operator=item.operator,
            contract=item.contract,
            warranty=item.warranty,
            warranty_expires_at=item.warranty_expires_at,
            notes=item.notes,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )


@router.put("/{equipment_id}", response_model=EquipmentOut)
def update_equipment(equipment_id: int, payload: EquipmentUpdate, request: Request, user=Depends(require_admin)):
    with get_session() as session:
        item = session.get(Equipment, equipment_id)
        if not item:
            raise HTTPException(status_code=404, detail="Equipamento não encontrado")
        before = {
            "id": item.id,
            "unit_id": item.unit_id,
            "type": item.type,
            "name": item.name,
            "brand": item.brand,
            "asset_tag": item.asset_tag,
            "serial": item.serial,
            "imei": item.imei,
            "phone_number": item.phone_number,
            "operator": getattr(item, "operator", None),
            "contract": getattr(item, "contract", None),
            "warranty": item.warranty,
            "warranty_expires_at": str(item.warranty_expires_at) if item.warranty_expires_at else None,
            "notes": item.notes,
        }
        if payload.unit_id is not None:
            unit = session.get(Unit, payload.unit_id)
            if not unit:
                raise HTTPException(status_code=400, detail="Unidade inválida")
            item.unit_id = payload.unit_id
        if payload.type is not None:
            item.type = payload.type.strip().upper()
        if payload.name is not None:
            item.name = payload.name.strip()
        if payload.brand is not None:
            item.brand = payload.brand.strip() if payload.brand else None
        if payload.asset_tag is not None:
            item.asset_tag = payload.asset_tag.strip() if payload.asset_tag else None
        if payload.serial is not None:
            item.serial = payload.serial.strip() if payload.serial else None
        if payload.imei is not None:
            item.imei = payload.imei.strip() if payload.imei else None
        if payload.phone_number is not None:
            item.phone_number = payload.phone_number.strip() if payload.phone_number else None
        if payload.operator is not None:
            item.operator = payload.operator.strip() if payload.operator else None
        if payload.contract is not None:
            item.contract = payload.contract.strip() if payload.contract else None
        if payload.warranty is not None:
            item.warranty = bool(payload.warranty)
            if not item.warranty:
                item.warranty_expires_at = None
        if payload.warranty_expires_at is not None:
            if not item.warranty:
                raise HTTPException(status_code=400, detail="Não é possível definir vencimento sem garantia")
            item.warranty_expires_at = payload.warranty_expires_at
        if payload.notes is not None:
            item.notes = payload.notes.strip() if payload.notes else None
        try:
            session.commit()
        except Exception:
            session.rollback()
            raise HTTPException(status_code=400, detail="Não foi possível atualizar")
        session.refresh(item)
        after = {
            "id": item.id,
            "unit_id": item.unit_id,
            "type": item.type,
            "name": item.name,
            "brand": item.brand,
            "asset_tag": item.asset_tag,
            "serial": item.serial,
            "imei": item.imei,
            "phone_number": item.phone_number,
            "operator": getattr(item, "operator", None),
            "contract": getattr(item, "contract", None),
            "warranty": item.warranty,
            "warranty_expires_at": str(item.warranty_expires_at) if item.warranty_expires_at else None,
            "notes": item.notes,
        }
        log_event(
            session=session,
            request=request,
            user=user,
            action="UPDATE",
            entity="equipment",
            entity_id=item.id,
            summary=f'Atualizou equipamento "{item.name}" ({item.type})',
            before=before,
            after=after,
        )
        session.commit()
        return EquipmentOut(
            id=item.id,
            unit_id=item.unit_id,
            type=item.type,
            name=item.name,
            brand=item.brand,
            asset_tag=item.asset_tag,
            serial=item.serial,
            imei=item.imei,
            phone_number=item.phone_number,
            operator=getattr(item, "operator", None),
            contract=getattr(item, "contract", None),
            warranty=item.warranty,
            warranty_expires_at=item.warranty_expires_at,
            notes=item.notes,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )


@router.delete("/{equipment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_equipment(equipment_id: int, request: Request, user=Depends(require_admin)):
    with get_session() as session:
        item = session.get(Equipment, equipment_id)
        if not item:
            raise HTTPException(status_code=404, detail="Equipamento não encontrado")
        before = {
            "id": item.id,
            "unit_id": item.unit_id,
            "type": item.type,
            "name": item.name,
            "brand": item.brand,
            "asset_tag": item.asset_tag,
            "serial": item.serial,
            "imei": item.imei,
            "phone_number": item.phone_number,
            "operator": getattr(item, "operator", None),
            "contract": getattr(item, "contract", None),
            "warranty": item.warranty,
            "warranty_expires_at": str(item.warranty_expires_at) if item.warranty_expires_at else None,
            "notes": item.notes,
        }
        session.delete(item)
        session.commit()
        log_event(
            session=session,
            request=request,
            user=user,
            action="DELETE",
            entity="equipment",
            entity_id=equipment_id,
            summary=f'Removeu equipamento "{before.get("name")}" ({before.get("type")})',
            before=before,
        )
        session.commit()
        return None
