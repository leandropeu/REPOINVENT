from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func, select

from app.db import get_session
from app.deps import get_current_user
from app.models import Equipment, Unit
from app.schemas import StatsOut


router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("", response_model=StatsOut)
def get_stats(_: object = Depends(get_current_user)):
    with get_session() as session:
        total_equipment = session.scalar(select(func.count()).select_from(Equipment)) or 0
        total_units = session.scalar(select(func.count()).select_from(Unit)) or 0
        rows = session.execute(select(Equipment.type, func.count()).group_by(Equipment.type)).all()
        by_type = {t: int(c) for (t, c) in rows if t}
        return StatsOut(total_equipment=int(total_equipment), total_units=int(total_units), by_type=by_type)

