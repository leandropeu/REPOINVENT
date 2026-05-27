from __future__ import annotations

import argparse

from sqlalchemy import select

from app.db import Base, engine, get_session
from app.models import User
from app.security import hash_password


def upsert_user(*, name: str, username: str, password: str, is_admin: bool) -> None:
    Base.metadata.create_all(bind=engine)
    with get_session() as session:
        existing = session.scalar(select(User).where(User.username == username))
        if existing:
            existing.name = name
            existing.password_hash = hash_password(password)
            existing.is_admin = is_admin
            existing.is_active = True
            session.commit()
            return

        user = User(
            name=name,
            username=username,
            password_hash=hash_password(password),
            is_admin=is_admin,
            is_active=True,
        )
        session.add(user)
        session.commit()


def main() -> None:
    parser = argparse.ArgumentParser(description="Create/update a user in REPOINVENT DB.")
    parser.add_argument("--name", default="Super Admin")
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--superadmin", action="store_true", help="Set is_admin=true.")
    args = parser.parse_args()

    upsert_user(
        name=args.name.strip(),
        username=args.username.strip(),
        password=args.password,
        is_admin=bool(args.superadmin),
    )
    print("OK")


if __name__ == "__main__":
    main()

