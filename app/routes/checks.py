from __future__ import annotations

from fastapi import APIRouter, Depends, Form
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

from app.dashboard import redirect_target
from app.dates import now_local_naive, today_local
from app.db import get_session
from app.models import Habit, HabitEvent


router = APIRouter(prefix="/checks")


@router.post("/daily-toggle")
def daily_toggle(
    habit_id: int = Form(...),
    redirect_tab_name: str = Form("weekly"),
    session: Session = Depends(get_session),
):
    today = today_local()
    existing = session.exec(
        select(HabitEvent).where(
            HabitEvent.habit_id == habit_id,
            HabitEvent.occurred_on == today,
            HabitEvent.event_type == "completion",
        )
    ).all()

    if existing:
        for event in existing:
            session.delete(event)
    else:
        now = now_local_naive()
        session.add(
            HabitEvent(
                habit_id=habit_id,
                occurred_on=today,
                occurred_at=now.isoformat(timespec="seconds"),
                event_type="completion",
            )
        )

    session.commit()
    return RedirectResponse(url=redirect_target(redirect_tab_name), status_code=303)


@router.post("/increment")
def increment_habit(
    habit_id: int = Form(...),
    redirect_tab_name: str = Form("weekly"),
    session: Session = Depends(get_session),
):
    now = now_local_naive()
    session.add(
        HabitEvent(
            habit_id=habit_id,
            occurred_on=now.date(),
            occurred_at=now.isoformat(timespec="seconds"),
            event_type="completion",
        )
    )
    session.commit()
    return RedirectResponse(url=redirect_target(redirect_tab_name), status_code=303)


@router.post("/streak-reset")
def reset_streak(
    habit_id: int = Form(...),
    redirect_tab_name: str = Form("weekly"),
    session: Session = Depends(get_session),
):
    habit = session.get(Habit, habit_id)
    if habit is None:
        return RedirectResponse(url=redirect_target(redirect_tab_name), status_code=303)

    now = now_local_naive()
    session.add(
        HabitEvent(
            habit_id=habit_id,
            occurred_on=now.date(),
            occurred_at=now.isoformat(timespec="seconds"),
            event_type="failure",
        )
    )
    habit.started_at = now.date()
    habit.started_at_text = now.isoformat(timespec="seconds")
    session.add(habit)
    session.commit()
    return RedirectResponse(url=redirect_target(redirect_tab_name), status_code=303)
