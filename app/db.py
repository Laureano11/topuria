import os
from typing import Generator

from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy import text


def _sqlite_path() -> str:
    # Para Fly: /data lo provee el volumen persistente.
    return os.getenv("SQLITE_PATH", "/data/sqlite.db")


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

        check_cols = _sqlite_table_columns(conn, "habitcheck")
        if "check_at" not in check_cols:
            conn.execute(text("ALTER TABLE habitcheck ADD COLUMN check_at TEXT"))


def _sqlite_table_columns(conn, table_name: str) -> set[str]:
    rows = conn.execute(text(f"PRAGMA table_info({table_name})")).fetchall()
    # rows: (cid, name, type, notnull, dflt_value, pk)
    return {row[1] for row in rows}


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

