from __future__ import annotations

from datetime import date
from typing import Optional

from sqlmodel import Field, SQLModel


class Habit(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    goal: Optional[str] = Field(default=None)
    # Ej: Dinero, Salud, Fitness, Desarrollo personal, Adicciones, Estudio
    category: str = Field(default="General", index=True)
    # Ej: daily/weekly/monthly/yearly (UI soporta semanal/mensual/anual)
    cadence: str = Field(default="daily", index=True)
    # positive => marca "logrado"; negative => marca una recaída; avoid => marca "falló" para racha
    habit_kind: str = Field(default="positive", index=True)
    active: bool = Field(default=True, index=True)
    # Fecha desde la que se empieza a trackear (para hábitos históricos)
    started_at: Optional[date] = Field(default=None)
    # Timestamp ISO de inicio, útil para rachas con horas y minutos.
    started_at_text: Optional[str] = Field(default=None)
    # Objetivo numérico para hábitos de conteo (ej: 12 libros al año)
    target_count: Optional[int] = Field(default=None)


class HabitCheck(SQLModel, table=True):
    habit_id: int = Field(foreign_key="habit.id", primary_key=True)
    check_date: date = Field(primary_key=True)

    completed: bool = Field(default=False, index=True)
    # Guardamos el timestamp en texto para poder mostrar días/horas/minutos desde la última marca.
    # Formato: ISO 8601 sin zona horaria (ej: "2026-03-26T21:08:34").
    check_at: Optional[str] = Field(default=None)
    notes: Optional[str] = Field(default=None)


class HabitEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    habit_id: int = Field(foreign_key="habit.id", index=True)
    occurred_on: date = Field(index=True)
    occurred_at: str = Field(index=True)
    event_type: str = Field(default="completion", index=True)

