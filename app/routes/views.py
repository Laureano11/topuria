from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Dict, List, Tuple

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

from app.dates import add_days, iso_week_start, parse_date_yyyy_mm_dd, today_local
from app.db import get_session
from app.models import Habit, HabitCheck


router = APIRouter()


@router.get("/")
def index():
    return RedirectResponse(url="/day")


@router.get("/day")
def day(request: Request, date: str | None = None, session: Session = Depends(get_session)):
    d = parse_date_yyyy_mm_dd(date) if date else today_local()

    habits = session.exec(
        select(Habit).where(Habit.active == True).order_by(Habit.id)  # noqa: E712
    ).all()
    habit_ids = [h.id for h in habits if h.id is not None]

    completed_by_habit_id: Dict[int, bool] = {}
    if habit_ids:
        checks = session.exec(
            select(HabitCheck).where(
                HabitCheck.habit_id.in_(habit_ids), HabitCheck.check_date == d
            )
        ).all()
        for c in checks:
            completed_by_habit_id[c.habit_id] = c.completed

    templates = request.app.state.templates
    return templates.TemplateResponse(
        "day.html",
        {
            "request": request,
            "date_str": d.isoformat(),
            "habits": habits,
            "period_title": "Día",
            "completed_by_habit_id": completed_by_habit_id,
        },
    )


@router.get("/week")
def week(
    request: Request,
    date: str | None = None,
    session: Session = Depends(get_session),
):
    d = parse_date_yyyy_mm_dd(date) if date else today_local()
    start = iso_week_start(d)
    days = [add_days(start, i) for i in range(7)]
    end = days[-1]
    prev_start = add_days(start, -7)
    next_start = add_days(start, 7)

    habits = session.exec(
        select(Habit).where(Habit.active == True).order_by(Habit.id)  # noqa: E712
    ).all()
    habit_ids = [h.id for h in habits if h.id is not None]

    # completed_map[habit_id][YYYY-MM-DD] = completed?
    completed_map: Dict[int, Dict[str, bool]] = {}
    if habit_ids:
        checks = session.exec(
            select(HabitCheck).where(
                HabitCheck.habit_id.in_(habit_ids),
                HabitCheck.check_date >= start,
                HabitCheck.check_date <= end,
            )
        ).all()
        for c in checks:
            completed_map.setdefault(c.habit_id, {})[c.check_date.isoformat()] = c.completed

    templates = request.app.state.templates
    iso_year, iso_week, _ = d.isocalendar()
    return templates.TemplateResponse(
        "week.html",
        {
            "request": request,
            "period_title": f"Semana {iso_year}-W{iso_week:02d}",
            "week_start": start.isoformat(),
            "prev_week_date": prev_start.isoformat(),
            "next_week_date": next_start.isoformat(),
            "days": days,
            "habits": habits,
            "completed_map": completed_map,
        },
    )


def _month_range(year: int, month: int) -> tuple[date, date]:
    start = date(year, month, 1)
    if month == 12:
        end = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end = date(year, month + 1, 1) - timedelta(days=1)
    return start, end


@router.get("/month")
def month(
    request: Request,
    year: int | None = None,
    month: int | None = None,
    session: Session = Depends(get_session),
):
    today = today_local()
    y = year if year is not None else today.year
    m = month if month is not None else today.month
    start, end = _month_range(y, m)

    habits = session.exec(
        select(Habit).where(Habit.active == True).order_by(Habit.id)  # noqa: E712
    ).all()
    habit_ids = [h.id for h in habits if h.id is not None]

    completed_counts: Dict[int, int] = {h.id: 0 for h in habits if h.id is not None}
    if habit_ids:
        checks = session.exec(
            select(HabitCheck).where(
                HabitCheck.habit_id.in_(habit_ids),
                HabitCheck.check_date >= start,
                HabitCheck.check_date <= end,
                HabitCheck.completed == True,  # noqa: E712
            )
        ).all()
        for c in checks:
            completed_counts[c.habit_id] = completed_counts.get(c.habit_id, 0) + 1

    templates = request.app.state.templates
    total_days = (end - start).days + 1

    prev_month_year = y if m > 1 else y - 1
    prev_month = m - 1 if m > 1 else 12
    next_month_year = y if m < 12 else y + 1
    next_month = m + 1 if m < 12 else 1

    return templates.TemplateResponse(
        "month.html",
        {
            "request": request,
            "period_title": f"{y}-{m:02d}",
            "year": y,
            "month": m,
            "start": start,
            "end": end,
            "total_days": total_days,
            "prev_month_year": prev_month_year,
            "prev_month": prev_month,
            "next_month_year": next_month_year,
            "next_month": next_month,
            "habits": habits,
            "completed_counts": completed_counts,
        },
    )


@router.get("/year")
def year(
    request: Request,
    year: int | None = None,
    session: Session = Depends(get_session),
):
    today = today_local()
    y = year if year is not None else today.year
    start = date(y, 1, 1)
    end = date(y, 12, 31)

    habits = session.exec(
        select(Habit).where(Habit.active == True).order_by(Habit.id)  # noqa: E712
    ).all()
    habit_ids = [h.id for h in habits if h.id is not None]

    # completed_counts[habit_id][month_number] = count de días completados
    completed_counts: Dict[int, Dict[int, int]] = {
        h.id: {mm: 0 for mm in range(1, 13)} for h in habits if h.id is not None
    }

    if habit_ids:
        checks = session.exec(
            select(HabitCheck).where(
                HabitCheck.habit_id.in_(habit_ids),
                HabitCheck.check_date >= start,
                HabitCheck.check_date <= end,
                HabitCheck.completed == True,  # noqa: E712
            )
        ).all()
        for c in checks:
            mm = c.check_date.month
            completed_counts[c.habit_id][mm] = completed_counts[c.habit_id].get(mm, 0) + 1

    templates = request.app.state.templates
    prev_year = y - 1
    next_year = y + 1
    return templates.TemplateResponse(
        "year.html",
        {
            "request": request,
            "period_title": f"{y}",
            "year": y,
            "prev_year": prev_year,
            "next_year": next_year,
            "habits": habits,
            "completed_counts": completed_counts,
        },
    )

