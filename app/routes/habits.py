from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Form
from fastapi.responses import RedirectResponse
from sqlmodel import Session, delete

from app.dashboard import (
    default_target_for_cadence,
    normalize_cadence,
    normalize_category,
    parse_started_at_text,
    redirect_target,
)
from app.db import get_session
from app.models import Habit, HabitCheck, HabitEvent


router = APIRouter(prefix="/habits")


def normalize_habit_kind(value: str | None) -> str:
    allowed = {"positive", "negative", "avoid"}
    return value if value in allowed else "positive"


@router.get("/create")
def create_habit_get() -> RedirectResponse:
    return RedirectResponse(url="/", status_code=303)


@router.post("/create")
def create_habit(
    name: str = Form(...),
    goal: Optional[str] = Form(None),
    category: str = Form("Salud"),
    cadence: str = Form("daily"),
    habit_kind: str = Form("positive"),
    target_count: Optional[int] = Form(None),
    started_at_text: Optional[str] = Form(None),
    redirect_tab_name: str = Form("weekly"),
    session: Session = Depends(get_session),
):
    cleaned_name = name.strip()
    if not cleaned_name:
        return RedirectResponse(url=redirect_target(redirect_tab_name), status_code=303)

    normalized_kind = normalize_habit_kind(habit_kind)
    normalized_cadence = normalize_cadence(cadence)
    if normalized_kind == "avoid":
        normalized_cadence = "streak"
    elif normalized_kind == "negative":
        normalized_cadence = "daily"

    started_at, started_text = parse_started_at_text(started_at_text)
    habit = Habit(
        name=cleaned_name,
        goal=goal.strip() if goal and goal.strip() else None,
        category=normalize_category(category),
        cadence=normalized_cadence,
        habit_kind=normalized_kind,
        target_count=target_count or default_target_for_cadence(normalized_cadence),
        started_at=started_at,
        started_at_text=started_text,
        active=True,
    )
    session.add(habit)
    session.commit()
    return RedirectResponse(url=redirect_target(redirect_tab_name), status_code=303)


@router.get("/{habit_id}/update")
def update_habit_get(habit_id: int) -> RedirectResponse:
    return RedirectResponse(url="/", status_code=303)


@router.post("/{habit_id}/update")
def update_habit(
    habit_id: int,
    name: str = Form(...),
    goal: Optional[str] = Form(None),
    category: str = Form("Salud"),
    cadence: str = Form("daily"),
    target_count: Optional[int] = Form(None),
    started_at_text: Optional[str] = Form(None),
    redirect_tab_name: str = Form("weekly"),
    session: Session = Depends(get_session),
):
    habit = session.get(Habit, habit_id)
    if habit is None:
        return RedirectResponse(url=redirect_target(redirect_tab_name), status_code=303)

    cleaned_name = name.strip()
    if cleaned_name:
        habit.name = cleaned_name
    habit.goal = goal.strip() if goal and goal.strip() else None
    habit.category = normalize_category(category)

    if habit.habit_kind == "avoid":
        habit.cadence = "streak"
        started_at, started_text = parse_started_at_text(started_at_text)
        if started_at is not None and started_text is not None:
            habit.started_at = started_at
            habit.started_at_text = started_text
        habit.target_count = target_count or habit.target_count or default_target_for_cadence("streak")
    elif habit.habit_kind == "negative":
        habit.cadence = "daily"
        habit.target_count = 1
    else:
        habit.cadence = normalize_cadence(cadence)
        habit.target_count = target_count or default_target_for_cadence(habit.cadence)

    session.add(habit)
    session.commit()
    return RedirectResponse(url=redirect_target(redirect_tab_name), status_code=303)


@router.post("/{habit_id}/delete")
def delete_habit(
    habit_id: int,
    redirect_tab_name: str = Form("weekly"),
    session: Session = Depends(get_session),
):
    habit = session.get(Habit, habit_id)
    if habit is None:
        return RedirectResponse(url=redirect_target(redirect_tab_name), status_code=303)

    session.exec(delete(HabitEvent).where(HabitEvent.habit_id == habit_id))
    session.exec(delete(HabitCheck).where(HabitCheck.habit_id == habit_id))
    session.delete(habit)
    session.commit()
    return RedirectResponse(url=redirect_target(redirect_tab_name), status_code=303)
