import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from studytrack.database import get_all_tasks, initialize_database


class TaskListingTests(unittest.TestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_directory.cleanup)
        self.db_path = Path(self.temp_directory.name) / "test.db"
        initialize_database(self.db_path)

    def test_empty_database_returns_empty_list(self):
        self.assertEqual(get_all_tasks(self.db_path), [])

    def test_returns_all_tasks_with_their_saved_values(self):
        with closing(sqlite3.connect(self.db_path)) as connection:
            with connection:
                connection.executemany(
                    """
                    INSERT INTO tasks (
                        title, subject, due_date, is_completed
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                    [
                        (
                            "Курсова работа",
                            "Софтуерни процеси",
                            "2026-10-15",
                            0,
                        ),
                        (
                            "Упражнение",
                            "Python",
                            "2026-10-14",
                            1,
                        ),
                    ],
                )

        tasks = get_all_tasks(self.db_path)

        self.assertEqual(len(tasks), 2)
        self.assertNotEqual(tasks[0]["id"], tasks[1]["id"])

        self.assertEqual(tasks[0]["title"], "Курсова работа")
        self.assertEqual(tasks[0]["subject"], "Софтуерни процеси")
        self.assertEqual(tasks[0]["due_date"], "2026-10-15")
        self.assertEqual(tasks[0]["is_completed"], 0)

        self.assertEqual(tasks[1]["title"], "Упражнение")
        self.assertEqual(tasks[1]["subject"], "Python")
        self.assertEqual(tasks[1]["due_date"], "2026-10-14")
        self.assertEqual(tasks[1]["is_completed"], 1)


if __name__ == "__main__":
    unittest.main()