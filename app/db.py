import os
from typing import Generator

from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy import text

from app.dates import add_days, now_local_naive, today_local
from app.models import Habit, HabitCheck, HabitEvent


def _sqlite_path() -> str:
    # Para Fly: /data lo provee el volumen persistente.
    configured = os.getenv("SQLITE_PATH")
    if configured:
        return configured
    if os.path.isdir("/data"):
        return "/data/sqlite.db"
    return os.path.abspath("sqlite.db")


def _sqlite_url(db_path: str) -> str:
    # SQLite en SQLAlchemy usa: sqlite:////ruta/absoluta
    # sqlite:////data/sqlite.db
    return f"sqlite:///{db_path}" if db_path.startswith("/") else f"sqlite:///{db_path}"


engine = create_engine(
    _sqlite_url(_sqlite_path()),
    connect_args={"check_same_thread": False},
)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)
    _ensure_sqlite_columns()
    _migrate_legacy_checks_to_events()
    _seed_demo_data()


def _ensure_sqlite_columns() -> None:
    # SQLite no hace migraciones automáticas con SQLModel, así que agregamos columnas faltantes.
    with engine.begin() as conn:
        habit_cols = _sqlite_table_columns(conn, "habit")
        if "category" not in habit_cols:
            conn.execute(text("ALTER TABLE habit ADD COLUMN category TEXT DEFAULT 'General'"))
        if "cadence" not in habit_cols:
            conn.execute(text("ALTER TABLE habit ADD COLUMN cadence TEXT DEFAULT 'daily'"))
        if "habit_kind" not in habit_cols:
            conn.execute(text("ALTER TABLE habit ADD COLUMN habit_kind TEXT DEFAULT 'positive'"))
        if "started_at" not in habit_cols:
            conn.execute(text("ALTER TABLE habit ADD COLUMN started_at DATE"))
        if "started_at_text" not in habit_cols:
            conn.execute(text("ALTER TABLE habit ADD COLUMN started_at_text TEXT"))
        if "target_count" not in habit_cols:
            conn.execute(text("ALTER TABLE habit ADD COLUMN target_count INTEGER"))

        check_cols = _sqlite_table_columns(conn, "habitcheck")
        if "check_at" not in check_cols:
            conn.execute(text("ALTER TABLE habitcheck ADD COLUMN check_at TEXT"))


def _sqlite_table_columns(conn, table_name: str) -> set[str]:
    rows = conn.execute(text(f"PRAGMA table_info({table_name})")).fetchall()
    # rows: (cid, name, type, notnull, dflt_value, pk)
    return {row[1] for row in rows}


def _migrate_legacy_checks_to_events() -> None:
    with Session(engine) as session:
        if session.query(HabitEvent).first() is not None:
            return

        habits = session.query(Habit).all()
        habits_by_id = {habit.id: habit for habit in habits if habit.id is not None}
        checks = session.query(HabitCheck).filter(HabitCheck.completed == True).all()  # noqa: E712

        migrated = False
        for check in checks:
            habit = habits_by_id.get(check.habit_id)
            if habit is None:
                continue

            event_type = "failure" if habit.habit_kind == "avoid" else "completion"
            occurred_at = check.check_at or f"{check.check_date.isoformat()}T00:00:00"
            session.add(
                HabitEvent(
                    habit_id=check.habit_id,
                    occurred_on=check.check_date,
                    occurred_at=occurred_at,
                    event_type=event_type,
                )
            )
            migrated = True

        if migrated:
            session.commit()


def _seed_demo_data() -> None:
    with Session(engine) as session:
        if session.query(Habit).first() is not None:
            return

        today = today_local()
        now = now_local_naive()

        demo_habits = [
            Habit(name="Fui al gimnasio", category="Salud", cadence="daily", target_count=1),
            Habit(name="Estiré 10 minutos", category="Salud", cadence="daily", target_count=1),
            Habit(name="Leí 50 páginas", category="Estudio", cadence="daily", target_count=1),
            Habit(name="Medité 10 min", category="Salud", cadence="daily", target_count=1),
            Habit(name="Revisé finanzas personales", category="Dinero", cadence="daily", target_count=1),
            Habit(name="Trabajé en proyecto personal", category="Trabajo", cadence="daily", target_count=1),
            Habit(name="Aprendí algo nuevo", category="Estudio", cadence="daily", target_count=1),
            Habit(name="Llamar a familia", category="Salud", cadence="weekly", target_count=1),
            Habit(name="Sesión de estudio profundo", category="Estudio", cadence="weekly", target_count=3),
            Habit(name="Salida al aire libre", category="Salud", cadence="weekly", target_count=2),
            Habit(name="Revisar inversiones", category="Dinero", cadence="weekly", target_count=1),
            Habit(name="Revisar presupuesto profundo", category="Dinero", cadence="monthly", target_count=2),
            Habit(name="Networking profesional", category="Trabajo", cadence="monthly", target_count=3),
            Habit(name="Módulos de curso completados", category="Estudio", cadence="monthly", target_count=4),
            Habit(name="Libros leídos", category="Estudio", cadence="yearly", target_count=24),
            Habit(name="Cursos completados", category="Estudio", cadence="yearly", target_count=6),
            Habit(name="Inversión mensual", category="Dinero", cadence="yearly", target_count=12),
            Habit(
                name="Sin alcohol",
                category="Salud",
                cadence="streak",
                habit_kind="avoid",
                target_count=7,
                started_at=today,
                started_at_text=add_days(today, -2).isoformat() + "T10:45:00",
            ),
            Habit(
                name="Sin redes sociales en la mañana",
                category="Estudio",
                cadence="streak",
                habit_kind="avoid",
                target_count=10,
                started_at=today,
                started_at_text=add_days(today, -8).isoformat() + "T06:30:00",
            ),
            Habit(
                name="Sin comer azúcar",
                category="Salud",
                cadence="streak",
                habit_kind="avoid",
                target_count=7,
                started_at=today,
                started_at_text=add_days(today, -1).isoformat() + "T15:20:00",
            ),
        ]

        for habit in demo_habits:
            session.add(habit)
        session.commit()

        habits_by_name = {
            habit.name: habit
            for habit in session.query(Habit).all()
            if habit.id is not None
        }

        def add_completion(name: str, days_ago: int, hour: int = 9, minute: int = 0) -> None:
            habit = habits_by_name[name]
            event_day = add_days(today, -days_ago)
            session.add(
                HabitEvent(
                    habit_id=habit.id,
                    occurred_on=event_day,
                    occurred_at=event_day.isoformat() + f"T{hour:02d}:{minute:02d}:00",
                    event_type="completion",
                )
            )

        for name in ["Fui al gimnasio", "Estiré 10 minutos", "Leí 50 páginas"]:
            add_completion(name, 0)
        for name in [
            "Fui al gimnasio",
            "Estiré 10 minutos",
            "Leí 50 páginas",
            "Revisé finanzas personales",
            "Trabajé en proyecto personal",
        ]:
            add_completion(name, 1)
        for name in ["Fui al gimnasio", "Leí 50 páginas", "Aprendí algo nuevo"]:
            add_completion(name, 2)

        add_completion("Llamar a familia", 3, 20, 15)
        add_completion("Sesión de estudio profundo", 1, 19, 30)
        add_completion("Sesión de estudio profundo", 3, 18, 45)
        add_completion("Salida al aire libre", 5, 17, 10)

        add_completion("Revisar presupuesto profundo", 12, 11, 0)
        add_completion("Networking profesional", 10, 18, 0)
        add_completion("Networking profesional", 5, 18, 30)
        add_completion("Módulos de curso completados", 9, 21, 0)
        add_completion("Módulos de curso completados", 4, 21, 0)

        yearly_books = [75, 63, 52, 44, 33, 19, 6]
        for index, days_ago in enumerate(yearly_books):
            add_completion("Libros leídos", days_ago, 22, index)

        for days_ago in [60, 14]:
            add_completion("Cursos completados", days_ago, 20, 0)
        for days_ago in [80, 50, 20]:
            add_completion("Inversión mensual", days_ago, 8, 30)

        session.add(
            HabitEvent(
                habit_id=habits_by_name["Sin alcohol"].id,
                occurred_on=add_days(today, -15),
                occurred_at=add_days(today, -15).isoformat() + "T22:00:00",
                event_type="failure",
            )
        )
        session.add(
            HabitEvent(
                habit_id=habits_by_name["Sin redes sociales en la mañana"].id,
                occurred_on=add_days(today, -18),
                occurred_at=add_days(today, -18).isoformat() + "T09:00:00",
                event_type="failure",
            )
        )
        session.add(
            HabitEvent(
                habit_id=habits_by_name["Sin comer azúcar"].id,
                occurred_on=add_days(today, -6),
                occurred_at=add_days(today, -6).isoformat() + "T16:30:00",
                event_type="failure",
            )
        )
        session.commit()


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

