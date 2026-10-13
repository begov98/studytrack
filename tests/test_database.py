import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from studytrack.database import initialize_database


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_directory.cleanup)
        self.db_path = Path(self.temp_directory.name) / "data" / "test.db"

    def test_initialization_creates_database_and_tasks_table(self):
        initialize_database(self.db_path)

        self.assertTrue(self.db_path.is_file())

        with closing(sqlite3.connect(self.db_path)) as connection:
            rows = connection.execute(
                "SELECT id, title, subject, due_date, is_completed FROM tasks"
            ).fetchall()

        self.assertEqual(rows, [])

    def test_reinitialization_preserves_tasks(self):
        initialize_database(self.db_path)

        with closing(sqlite3.connect(self.db_path)) as connection:
            with connection:
                connection.execute(
                    """
                    INSERT INTO tasks (title, subject, due_date)
                    VALUES (?, ?, ?)
                    """,
                    ("Курсова работа", "Софтуерни процеси", "2026-10-15"),
                )

        initialize_database(self.db_path)

        with closing(sqlite3.connect(self.db_path)) as connection:
            rows = connection.execute(
                "SELECT title, subject, due_date, is_completed FROM tasks"
            ).fetchall()

        self.assertEqual(
            rows,
            [("Курсова работа", "Софтуерни процеси", "2026-10-15", 0)],
        )


if __name__ == "__main__":
    unittest.main()