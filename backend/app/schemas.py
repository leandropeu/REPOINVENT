from __future__ import annotations

import datetime as dt
import re
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshIn(BaseModel):
    refresh_token: str = Field(min_length=20, max_length=4096)


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

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        value = value.strip().lower()
        if not re.fullmatch(r"[a-z0-9._-]{3,80}", value):
            raise ValueError("Usuário inválido")
        return value


class UserUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=120)
    username: Optional[str] = Field(default=None, min_length=3, max_length=80)
    password: Optional[str] = Field(default=None, min_length=8, max_length=128)
    is_admin: Optional[bool] = None
    is_active: Optional[bool] = None

    @field_validator("username")
    @classmethod
    def normalize_username_optional(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        value = value.strip().lower()
        if not re.fullmatch(r"[a-z0-9._-]{3,80}", value):
            raise ValueError("Usuário inválido")
        return value


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

    @field_validator("cnpj")
    @classmethod
    def validate_cnpj(cls, value: Optional[str]) -> Optional[str]:
        if not value:
            return None
        digits = re.sub(r"\D+", "", value)
        if len(digits) != 14:
            raise ValueError("CNPJ deve ter 14 dígitos")
        return digits


class UnitUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=160)
    external_id: Optional[str] = Field(default=None, max_length=80)
    cnpj: Optional[str] = Field(default=None, max_length=32)
    address: Optional[str] = Field(default=None, max_length=255)

    @field_validator("cnpj")
    @classmethod
    def validate_cnpj_optional(cls, value: Optional[str]) -> Optional[str]:
        if value is None or value == "":
            return None if value == "" else value
        digits = re.sub(r"\D+", "", value)
        if len(digits) != 14:
            raise ValueError("CNPJ deve ter 14 dígitos")
        return digits


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

    @field_validator("type")
    @classmethod
    def normalize_type(cls, value: str) -> str:
        return value.strip().upper()

    @field_validator("imei")
    @classmethod
    def validate_imei(cls, value: Optional[str]) -> Optional[str]:
        if not value:
            return None
        digits = re.sub(r"\D+", "", value)
        if len(digits) not in (14, 15, 16):
            raise ValueError("IMEI inválido")
        return digits

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value: Optional[str]) -> Optional[str]:
        if not value:
            return None
        digits = re.sub(r"\D+", "", value)
        if len(digits) < 10 or len(digits) > 15:
            raise ValueError("Telefone inválido")
        return digits


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

    @field_validator("type")
    @classmethod
    def normalize_type_optional(cls, value: Optional[str]) -> Optional[str]:
        return value.strip().upper() if value is not None else value

    @field_validator("imei")
    @classmethod
    def validate_imei_optional(cls, value: Optional[str]) -> Optional[str]:
        if value is None or value == "":
            return None if value == "" else value
        digits = re.sub(r"\D+", "", value)
        if len(digits) not in (14, 15, 16):
            raise ValueError("IMEI inválido")
        return digits

    @field_validator("phone_number")
    @classmethod
    def validate_phone_optional(cls, value: Optional[str]) -> Optional[str]:
        if value is None or value == "":
            return None if value == "" else value
        digits = re.sub(r"\D+", "", value)
        if len(digits) < 10 or len(digits) > 15:
            raise ValueError("Telefone inválido")
        return digits


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
