from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from app.audit import log_event
from app.db import get_session
from app.deps import get_current_user
from app.models import User
from app.rate_limit import SlidingWindowLimiter
from app.schemas import TokenOut, UserOut
from app.security import create_access_token, verify_password
from app.settings import settings


router = APIRouter(prefix="/auth", tags=["auth"])
login_limiter = SlidingWindowLimiter(
    max_requests=settings.login_rate_limit_max_attempts,
    window_seconds=settings.login_rate_limit_window_seconds,
)


def _request_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


@router.post("/login", response_model=TokenOut)
def login(request: Request, form: OAuth2PasswordRequestForm = Depends()):
    username = form.username.strip().lower()
    ip = _request_ip(request)

    allowed_ip, retry_ip = login_limiter.allow(f"login:ip:{ip}")
    if not allowed_ip:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Muitas tentativas de login. Tente novamente em {retry_ip}s.",
            headers={"Retry-After": str(retry_ip)},
        )

    allowed_user, retry_user = login_limiter.allow(f"login:user:{username}")
    if not allowed_user:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Muitas tentativas para este usuário. Tente novamente em {retry_user}s.",
            headers={"Retry-After": str(retry_user)},
        )

    with get_session() as session:
        user = session.scalar(select(User).where(User.username == username))
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

