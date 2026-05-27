from __future__ import annotations

from sqlalchemy import select

from app.db import Base, engine, get_session
from app.models import User


def main() -> None:
    Base.metadata.create_all(bind=engine)
    with get_session() as session:
        users = session.scalars(select(User).order_by(User.id.asc())).all()
        if not users:
            print("NO_USERS")
            return
        for u in users:
            print(f"{u.id}\t{u.username}\tadmin={bool(u.is_admin)}\tactive={bool(u.is_active)}\tname={u.name}")


if __name__ == "__main__":
    main()

