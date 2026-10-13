"""Инициализация и достъп до SQLite базата данни."""

import sqlite3
from contextlib import closing
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "studytrack.db"


def initialize_database(db_path: Path = DEFAULT_DB_PATH) -> None:
    """Създава базата и таблицата, без да изтрива съществуващи данни."""
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with closing(sqlite3.connect(db_path)) as connection:
        with connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL
                        CHECK (length(trim(title)) > 0),
                    subject TEXT NOT NULL
                        CHECK (length(trim(subject)) > 0),
                    due_date TEXT NOT NULL,
                    is_completed INTEGER NOT NULL DEFAULT 0
                        CHECK (is_completed IN (0, 1))
                )
                """
            )