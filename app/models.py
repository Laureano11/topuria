from __future__ import annotations

from datetime import date
from typing import Optional

from sqlmodel import Field, SQLModel


class Habit(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    goal: Optional[str] = Field(default=None)
    active: bool = Field(default=True, index=True)


class HabitCheck(SQLModel, table=True):
    habit_id: int = Field(foreign_key="habit.id", primary_key=True)
    check_date: date = Field(primary_key=True)

    completed: bool = Field(default=False, index=True)
    notes: Optional[str] = Field(default=None)

