import os
from typing import Generator

from sqlmodel import Session, SQLModel, create_engine


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


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

