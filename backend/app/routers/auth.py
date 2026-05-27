from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from app.db import get_session
from app.models import User
from app.schemas import TokenOut, UserOut
from app.security import create_access_token, verify_password
from app.deps import get_current_user
from app.audit import log_event


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenOut)
def login(request: Request, form: OAuth2PasswordRequestForm = Depends()):
    with get_session() as session:
        user = session.scalar(select(User).where(User.username == form.username))
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")
        if not verify_password(form.password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")
        token = create_access_token(subject=user.username)
        log_event(
            session=session,
            request=request,
            user=user,
            action="LOGIN",
            entity="auth",
            entity_id=user.id,
            summary="Login realizado",
        )
        session.commit()
        return TokenOut(access_token=token)


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return UserOut(
        id=user.id,
        name=user.name,
        username=user.username,
        is_admin=user.is_admin,
        is_active=user.is_active,
        created_at=user.created_at,
    )
