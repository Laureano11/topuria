from __future__ import annotations

import os
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def _tz_name() -> str:
    return os.getenv("TZ", "UTC")


def local_tz() -> ZoneInfo:
    try:
        return ZoneInfo(_tz_name())
    except ZoneInfoNotFoundError:
        return ZoneInfo("UTC")


def today_local() -> date:
    return datetime.now(tz=local_tz()).date()


def now_local_naive() -> datetime:
    # Guardamos timestamps sin tzinfo para que SQLite no tenga que interpretar zonas.
    return datetime.now(tz=local_tz()).replace(tzinfo=None)


def parse_date_yyyy_mm_dd(s: str) -> date:
    # Espera "YYYY-MM-DD"
    return date.fromisoformat(s)


def parse_iso_datetime(s: str) -> datetime:
    # Acepta "YYYY-MM-DDTHH:MM:SS" (sin tzinfo) o similar.
    return datetime.fromisoformat(s)


def iso_week_start(d: date) -> date:
    # Lunes ISO de la semana del día d
    iso_year, iso_week, _ = d.isocalendar()
    return date.fromisocalendar(iso_year, iso_week, 1)


def add_days(d: date, n: int) -> date:
    return d + timedelta(days=n)

