from __future__ import annotations

import datetime as dt

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError
from sqlalchemy import select

from app.audit import log_event
from app.db import get_session
from app.deps import get_current_user
from app.models import SessionToken, User
from app.rate_limit import SlidingWindowLimiter
from app.schemas import RefreshIn, TokenOut, UserOut
from app.security import create_access_token, create_refresh_token, decode_token, hash_jti, verify_password
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


def _is_locked(user: User, now: dt.datetime) -> bool:
    return bool(user.lockout_until and user.lockout_until > now)


def _persist_refresh_token(session, *, user_id: int, refresh_token: str) -> None:
    payload = decode_token(refresh_token)
    jti = payload.get("jti")
    exp = payload.get("exp")
    if not jti or not exp:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token invalido")
    expires_at = dt.datetime.fromtimestamp(exp, tz=dt.timezone.utc)
    session.add(
        SessionToken(
            user_id=user_id,
            token_type="refresh",
            jti_hash=hash_jti(jti),
            expires_at=expires_at,
            revoked_at=None,
        )
    )


@router.post("/login", response_model=TokenOut)
def login(request: Request, form: OAuth2PasswordRequestForm = Depends()):
    username = form.username.strip().lower()
    ip = _request_ip(request)
    now = dt.datetime.now(dt.timezone.utc)

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
            detail=f"Muitas tentativas para este usuario. Tente novamente em {retry_user}s.",
            headers={"Retry-After": str(retry_user)},
        )

    with get_session() as session:
        user = session.scalar(select(User).where(User.username == username))
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais invalidas")
        if _is_locked(user, now):
            seconds = int((user.lockout_until - now).total_seconds())
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Conta temporariamente bloqueada. Tente novamente em {max(1, seconds)}s.",
            )

        if not verify_password(form.password, user.password_hash):
            user.failed_login_attempts = int(user.failed_login_attempts or 0) + 1
            if user.failed_login_attempts >= settings.login_lockout_threshold:
                user.lockout_until = now + dt.timedelta(minutes=settings.login_lockout_minutes)
                user.failed_login_attempts = 0
            session.commit()
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais invalidas")

        user.failed_login_attempts = 0
        user.lockout_until = None
        access_token = create_access_token(subject=user.username)
        refresh_token = create_refresh_token(subject=user.username)
        _persist_refresh_token(session, user_id=user.id, refresh_token=refresh_token)
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
        return TokenOut(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenOut)
def refresh_token(payload: RefreshIn, request: Request):
    try:
        decoded = decode_token(payload.refresh_token)
        if decoded.get("typ") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token invalido")
        username = str(decoded.get("sub") or "").strip().lower()
        jti = decoded.get("jti")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token invalido")

    if not username or not jti:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token invalido")

    with get_session() as session:
        user = session.scalar(select(User).where(User.username == username))
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario invalido")
        token_row = session.scalar(
            select(SessionToken).where(
                SessionToken.jti_hash == hash_jti(jti),
                SessionToken.token_type == "refresh",
            )
        )
        now = dt.datetime.now(dt.timezone.utc)
        if not token_row or token_row.revoked_at is not None or token_row.expires_at <= now:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token invalido")

        # rotate refresh token
        token_row.revoked_at = now
        access_token = create_access_token(subject=user.username)
        new_refresh = create_refresh_token(subject=user.username)
        _persist_refresh_token(session, user_id=user.id, refresh_token=new_refresh)
        log_event(
            session=session,
            request=request,
            user=user,
            action="UPDATE",
            entity="auth",
            entity_id=user.id,
            summary="Refresh token rotacionado",
        )
        session.commit()
        return TokenOut(access_token=access_token, refresh_token=new_refresh)


@router.post("/logout")
def logout(payload: RefreshIn, request: Request):
    try:
        decoded = decode_token(payload.refresh_token)
        if decoded.get("typ") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token invalido")
        jti = decoded.get("jti")
        username = str(decoded.get("sub") or "").strip().lower()
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token invalido")

    if not jti:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token invalido")

    with get_session() as session:
        token_row = session.scalar(
            select(SessionToken).where(
                SessionToken.jti_hash == hash_jti(jti),
                SessionToken.token_type == "refresh",
            )
        )
        if token_row and token_row.revoked_at is None:
            token_row.revoked_at = dt.datetime.now(dt.timezone.utc)
        user = session.scalar(select(User).where(User.username == username)) if username else None
        log_event(
            session=session,
            request=request,
            user=user,
            action="UPDATE",
            entity="auth",
            entity_id=(user.id if user else None),
            summary="Logout realizado",
        )
        session.commit()
    return {"ok": True}


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

