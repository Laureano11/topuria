from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from sqlmodel import Session, select

from app.db import get_session
from app.models import HabitCheck
from app.dates import parse_date_yyyy_mm_dd


router = APIRouter()


@router.post("/checks/set")
def set_check(
    request: Request,
    habit_id: int = Form(...),
    date: str = Form(...),
    completed: int = Form(...),
    session: Session = Depends(get_session),
):
    # Nota: `completed` llega como 0/1 desde hx-vals.
    check_date = parse_date_yyyy_mm_dd(date)
    completed_bool = completed == 1

    templates = request.app.state.templates

    existing = session.exec(
        select(HabitCheck).where(
            HabitCheck.habit_id == habit_id, HabitCheck.check_date == check_date
        )
    ).one_or_none()

    if existing is None:
        existing = HabitCheck(habit_id=habit_id, check_date=check_date, completed=completed_bool)
    else:
        existing.completed = completed_bool

    session.add(existing)
    session.commit()

    return templates.TemplateResponse(
        "partials/check_button.html",
        {
            "request": request,
            "habit_id": habit_id,
            "date_str": check_date.isoformat(),
            "checked": completed_bool,
        },
        media_type="text/html",
    )

