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


def get_all_tasks(db_path: Path = DEFAULT_DB_PATH) -> list[dict]:
    """Връща всички задачи, подредени по идентификатор."""
    with closing(sqlite3.connect(db_path)) as connection:
        connection.row_factory = sqlite3.Row

        rows = connection.execute(
            """
            SELECT id, title, subject, due_date, is_completed
            FROM tasks
            ORDER BY id
            """
        ).fetchall()

        return [dict(row) for row in rows]

def insert_task(
    title: str,
    subject: str,
    due_date: str,
    db_path: Path = DEFAULT_DB_PATH,
) -> int:
    """Записва задача и връща нейния идентификатор."""
    with closing(sqlite3.connect(db_path)) as connection:
        with connection:
            cursor = connection.execute(
                """
                INSERT INTO tasks (title, subject, due_date)
                VALUES (?, ?, ?)
                """,
                (title, subject, due_date),
            )
            return cursor.lastrowid


def update_task(
    task_id: int,
    title: str,
    subject: str,
    due_date: str,
    db_path: Path = DEFAULT_DB_PATH,
) -> None:
    """Актуализира данните на задача, без да променя статуса ѝ."""
    with closing(sqlite3.connect(db_path)) as connection:
        with connection:
            cursor = connection.execute(
                """
                UPDATE tasks
                SET title = ?, subject = ?, due_date = ?
                WHERE id = ?
                """,
                (title, subject, due_date, task_id),
            )

            if cursor.rowcount == 0:
                raise ValueError("Задачата вече не съществува.")

def delete_task(
    task_id: int,
    db_path: Path = DEFAULT_DB_PATH,
) -> None:
    """Изтрива само задачата с посочения идентификатор."""
    with closing(sqlite3.connect(db_path)) as connection:
        with connection:
            cursor = connection.execute(
                "DELETE FROM tasks WHERE id = ?",
                (task_id,),
            )

            if cursor.rowcount == 0:
                raise ValueError("Задачата вече не съществува.")