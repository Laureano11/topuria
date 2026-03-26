from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlmodel import Session

from app.db import get_session
from app.models import Habit


router = APIRouter()


@router.post("/habits/create")
def create_habit(
    name: str = Form(...),
    goal: Optional[str] = Form(None),
    date: Optional[str] = Form(None),
    session: Session = Depends(get_session),
):
    # Nota: por simplicidad usamos un create inmediato.
    # Más adelante podemos añadir validación/normalización.
    cleaned = name.strip()
    if not cleaned:
        # Volvemos a la vista sin romper el flujo.
        return RedirectResponse(url="/day")

    habit = Habit(name=cleaned, goal=goal, active=True)
    session.add(habit)
    session.commit()

    target = "/day"
    if date:
        target = f"/day?date={date}"
    return RedirectResponse(url=target)


@router.post("/habits/{habit_id}/update")
def update_habit(
    habit_id: int,
    name: str = Form(...),
    goal: Optional[str] = Form(None),
    date: Optional[str] = Form(None),
    session: Session = Depends(get_session),
):
    cleaned = name.strip()
    habit = session.get(Habit, habit_id)
    if not habit:
        return RedirectResponse(url="/day")

    habit.name = cleaned
    habit.goal = goal
    session.add(habit)
    session.commit()

    target = "/day"
    if date:
        target = f"/day?date={date}"
    return RedirectResponse(url=target)

