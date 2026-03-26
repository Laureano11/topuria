from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Form
from fastapi.responses import RedirectResponse
from sqlmodel import Session, delete

from app.db import get_session
from app.models import Habit, HabitCheck


router = APIRouter()


@router.get("/habits/create")
def create_habit_get() -> RedirectResponse:
    # Algunos navegadores/controles pueden intentar precargar con GET.
    # El flujo correcto es POST desde el formulario.
    return RedirectResponse(url="/day")


@router.post("/habits/create")
def create_habit(
    name: str = Form(...),
    goal: Optional[str] = Form(None),
    category: str = Form("General"),
    cadence: str = Form("daily"),
    habit_kind: str = Form("positive"),
    date: Optional[str] = Form(None),
    session: Session = Depends(get_session),
):
    # Nota: por simplicidad usamos un create inmediato.
    # Más adelante podemos añadir validación/normalización.
    cleaned = name.strip()
    if not cleaned:
        # Volvemos a la vista sin romper el flujo.
        return RedirectResponse(url="/day")

    habit = Habit(
        name=cleaned,
        goal=goal,
        category=category,
        cadence=cadence,
        habit_kind=habit_kind,
        active=True,
    )
    session.add(habit)
    session.commit()

    target = "/day"
    if date:
        target = f"/day?date={date}"
    return RedirectResponse(url=target)


@router.get("/habits/{habit_id}/update")
def update_habit_get(habit_id: int) -> RedirectResponse:
    # Evita 405 si alguien intenta hacer GET a la URL del formulario de update.
    return RedirectResponse(url="/day")


@router.post("/habits/{habit_id}/update")
def update_habit(
    habit_id: int,
    name: str = Form(...),
    goal: Optional[str] = Form(None),
    category: str = Form("General"),
    cadence: str = Form("daily"),
    habit_kind: str = Form("positive"),
    date: Optional[str] = Form(None),
    session: Session = Depends(get_session),
):
    cleaned = name.strip()
    habit = session.get(Habit, habit_id)
    if not habit:
        return RedirectResponse(url="/day")

    habit.name = cleaned
    habit.goal = goal
    habit.category = category
    habit.cadence = cadence
    habit.habit_kind = habit_kind
    session.add(habit)
    session.commit()

    target = "/day"
    if date:
        target = f"/day?date={date}"
    return RedirectResponse(url=target)


@router.post("/habits/{habit_id}/delete")
def delete_habit(
    habit_id: int,
    session: Session = Depends(get_session),
):
    habit = session.get(Habit, habit_id)
    if not habit:
        return RedirectResponse(url="/day")

    # Limpieza explícita (sin cascade en el modelo).
    session.exec(delete(HabitCheck).where(HabitCheck.habit_id == habit_id))
    session.delete(habit)
    session.commit()
    return RedirectResponse(url="/day")

