import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from studytrack.database import get_all_tasks, initialize_database
from studytrack.services import (
    change_task_status,
    create_task,
    remove_task,
)


class DatabaseMigrationTests(unittest.TestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_directory.cleanup)
        self.db_path = Path(self.temp_directory.name) / "test.db"

    def test_deleted_id_is_not_reused_in_new_database(self):
        initialize_database(self.db_path)

        old_id = create_task(
            "Стара задача", "Python", "20.10.2026", self.db_path
        )
        remove_task(old_id, self.db_path)

        new_id = create_task(
            "Нова задача", "Python", "21.10.2026", self.db_path
        )

        self.assertGreater(new_id, old_id)

    def test_migration_preserves_existing_data_and_prevents_id_reuse(self):
        with closing(sqlite3.connect(self.db_path)) as connection:
            with connection:
                connection.execute(
                    """
                    CREATE TABLE tasks (
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
                connection.executemany(
                    """
                    INSERT INTO tasks (
                        id, title, subject, due_date, is_completed
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    [
                        (3, "Първа задача", "Python", "2026-10-20", 0),
                        (7, "Втора задача", "Математика", "2026-10-21", 1),
                    ],
                )

        original = get_all_tasks(self.db_path)

        initialize_database(self.db_path)

        self.assertEqual(get_all_tasks(self.db_path), original)

        remove_task(7, self.db_path)
        new_id = create_task(
            "Нова задача", "Python", "22.10.2026", self.db_path
        )

        self.assertGreater(new_id, 7)

    def test_reinitialization_preserves_deleted_id_history(self):
        initialize_database(self.db_path)

        old_id = create_task(
            "Стара задача", "Python", "20.10.2026", self.db_path
        )
        remove_task(old_id, self.db_path)

        initialize_database(self.db_path)

        new_id = create_task(
            "Нова задача", "Python", "21.10.2026", self.db_path
        )

        self.assertGreater(new_id, old_id)

    def test_stale_id_cannot_change_replacement_task(self):
        initialize_database(self.db_path)

        old_id = create_task(
            "Стара задача", "Python", "20.10.2026", self.db_path
        )
        remove_task(old_id, self.db_path)

        create_task(
            "Нова задача", "Python", "21.10.2026", self.db_path
        )
        original = get_all_tasks(self.db_path)

        with self.assertRaisesRegex(ValueError, "не съществува"):
            change_task_status(old_id, self.db_path)

        self.assertEqual(get_all_tasks(self.db_path), original)


if __name__ == "__main__":
    unittest.main()