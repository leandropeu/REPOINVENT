from __future__ import annotations

import datetime as dt
from typing import Optional

from pydantic import BaseModel, Field


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    name: str
    username: str
    is_admin: bool
    is_active: bool
    created_at: dt.datetime


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    username: str = Field(min_length=3, max_length=80)
    password: str = Field(min_length=8, max_length=128)
    is_admin: bool = False
    is_active: bool = True


class UserUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=120)
    username: Optional[str] = Field(default=None, min_length=3, max_length=80)
    password: Optional[str] = Field(default=None, min_length=8, max_length=128)
    is_admin: Optional[bool] = None
    is_active: Optional[bool] = None


class UnitOut(BaseModel):
    id: int
    name: str
    external_id: Optional[str] = None
    cnpj: Optional[str] = None
    address: Optional[str] = None
    created_at: dt.datetime


class UnitCreate(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    external_id: Optional[str] = Field(default=None, max_length=80)
    cnpj: Optional[str] = Field(default=None, max_length=32)
    address: Optional[str] = Field(default=None, max_length=255)


class UnitUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=160)
    external_id: Optional[str] = Field(default=None, max_length=80)
    cnpj: Optional[str] = Field(default=None, max_length=32)
    address: Optional[str] = Field(default=None, max_length=255)


class EquipmentOut(BaseModel):
    id: int
    unit_id: int
    type: str
    name: str
    brand: Optional[str] = None
    asset_tag: Optional[str] = None
    serial: Optional[str] = None
    imei: Optional[str] = None
    phone_number: Optional[str] = None
    operator: Optional[str] = None
    contract: Optional[str] = None
    warranty: bool = False
    warranty_expires_at: Optional[dt.date] = None
    notes: Optional[str] = None
    created_at: dt.datetime
    updated_at: dt.datetime


class EquipmentCreate(BaseModel):
    unit_id: int
    type: str = Field(min_length=2, max_length=40)
    name: str = Field(min_length=1, max_length=160)
    brand: Optional[str] = Field(default=None, max_length=120)
    asset_tag: Optional[str] = Field(default=None, max_length=80)
    serial: Optional[str] = Field(default=None, max_length=120)
    imei: Optional[str] = Field(default=None, max_length=32)
    phone_number: Optional[str] = Field(default=None, max_length=32)
    operator: Optional[str] = Field(default=None, max_length=80)
    contract: Optional[str] = Field(default=None, max_length=120)
    warranty: bool = False
    warranty_expires_at: Optional[dt.date] = None
    notes: Optional[str] = None


class EquipmentUpdate(BaseModel):
    unit_id: Optional[int] = None
    type: Optional[str] = Field(default=None, min_length=2, max_length=40)
    name: Optional[str] = Field(default=None, min_length=1, max_length=160)
    brand: Optional[str] = Field(default=None, max_length=120)
    asset_tag: Optional[str] = Field(default=None, max_length=80)
    serial: Optional[str] = Field(default=None, max_length=120)
    imei: Optional[str] = Field(default=None, max_length=32)
    phone_number: Optional[str] = Field(default=None, max_length=32)
    operator: Optional[str] = Field(default=None, max_length=80)
    contract: Optional[str] = Field(default=None, max_length=120)
    warranty: Optional[bool] = None
    warranty_expires_at: Optional[dt.date] = None
    notes: Optional[str] = None


class StatsOut(BaseModel):
    total_equipment: int
    total_units: int
    by_type: dict[str, int]


class AuditOut(BaseModel):
    id: int
    created_at: dt.datetime
    user_id: Optional[int] = None
    username: Optional[str] = None
    ip: Optional[str] = None
    action: str
    entity: str
    entity_id: Optional[int] = None
    summary: Optional[str] = None
    before_json: Optional[str] = None
    after_json: Optional[str] = None
