from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select

from app.db import get_session
from app.deps import require_admin
from app.models import User
from app.schemas import UserCreate, UserOut, UserUpdate
from app.security import hash_password
from app.audit import log_event


router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserOut])
def list_users(
    q: str | None = Query(default=None, max_length=120),
    limit: int = Query(default=500, ge=1, le=5000),
    _: object = Depends(require_admin),
):
    with get_session() as session:
        stmt = select(User).order_by(User.created_at.desc()).limit(limit)
        if q:
            stmt = stmt.where(User.name.ilike(f"%{q}%") | User.username.ilike(f"%{q}%"))
        items = session.scalars(stmt).all()
        return [
            UserOut(
                id=u.id,
                name=u.name,
                username=u.username,
                is_admin=u.is_admin,
                is_active=u.is_active,
                created_at=u.created_at,
            )
            for u in items
        ]


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, request: Request, admin=Depends(require_admin)):
    with get_session() as session:
        user = User(
            name=payload.name.strip(),
            username=payload.username.strip(),
            password_hash=hash_password(payload.password),
            is_admin=payload.is_admin,
            is_active=payload.is_active,
        )
        session.add(user)
        try:
            session.commit()
        except Exception:
            session.rollback()
            raise HTTPException(status_code=400, detail="Não foi possível criar (usuário duplicado?)")
        session.refresh(user)
        log_event(
            session=session,
            request=request,
            user=admin,
            action="CREATE",
            entity="users",
            entity_id=user.id,
            summary=f'Criou usuário "{user.username}"',
            after={"id": user.id, "username": user.username, "name": user.name, "is_admin": user.is_admin, "is_active": user.is_active},
        )
        session.commit()
        return UserOut(
            id=user.id,
            name=user.name,
            username=user.username,
            is_admin=user.is_admin,
            is_active=user.is_active,
            created_at=user.created_at,
        )


@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: int, payload: UserUpdate, request: Request, admin=Depends(require_admin)):
    with get_session() as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        before = {"id": user.id, "username": user.username, "name": user.name, "is_admin": user.is_admin, "is_active": user.is_active}
        if payload.name is not None:
            user.name = payload.name.strip()
        if payload.username is not None:
            user.username = payload.username.strip()
        if payload.password is not None:
            user.password_hash = hash_password(payload.password)
        if payload.is_admin is not None:
            user.is_admin = payload.is_admin
        if payload.is_active is not None:
            user.is_active = payload.is_active
        try:
            session.commit()
        except Exception:
            session.rollback()
            raise HTTPException(status_code=400, detail="Não foi possível atualizar")
        session.refresh(user)
        after = {"id": user.id, "username": user.username, "name": user.name, "is_admin": user.is_admin, "is_active": user.is_active}
        log_event(
            session=session,
            request=request,
            user=admin,
            action="UPDATE",
            entity="users",
            entity_id=user.id,
            summary=f'Atualizou usuário "{user.username}"',
            before=before,
            after=after,
        )
        session.commit()
        return UserOut(
            id=user.id,
            name=user.name,
            username=user.username,
            is_admin=user.is_admin,
            is_active=user.is_active,
            created_at=user.created_at,
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, request: Request, admin=Depends(require_admin)):
    with get_session() as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        before = {"id": user.id, "username": user.username, "name": user.name, "is_admin": user.is_admin, "is_active": user.is_active}
        session.delete(user)
        session.commit()
        log_event(
            session=session,
            request=request,
            user=admin,
            action="DELETE",
            entity="users",
            entity_id=user_id,
            summary=f'Removeu usuário "{before.get("username")}"',
            before=before,
        )
        session.commit()
        return None
