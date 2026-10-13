import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from studytrack.database import get_all_tasks, initialize_database
from studytrack.services import create_task, edit_task


class TaskEditingTests(unittest.TestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_directory.cleanup)
        self.db_path = Path(self.temp_directory.name) / "test.db"
        initialize_database(self.db_path)

        self.task_id = create_task(
            "Първоначална задача",
            "Python",
            "15.10.2026",
            self.db_path,
        )

    def test_edit_updates_fields_and_preserves_id_and_status(self):
        with closing(sqlite3.connect(self.db_path)) as connection:
            with connection:
                connection.execute(
                    "UPDATE tasks SET is_completed = 1 WHERE id = ?",
                    (self.task_id,),
                )

        edit_task(
            self.task_id,
            "  Обновена задача  ",
            "  Бази данни  ",
            "20.11.2026",
            self.db_path,
        )

        self.assertEqual(
            get_all_tasks(self.db_path),
            [
                {
                    "id": self.task_id,
                    "title": "Обновена задача",
                    "subject": "Бази данни",
                    "due_date": "2026-11-20",
                    "is_completed": 1,
                }
            ],
        )

    def test_invalid_edit_leaves_original_data_unchanged(self):
        original = get_all_tasks(self.db_path)

        invalid_inputs = [
            ("   ", "Python", "15.10.2026"),
            ("Задача", "", "15.10.2026"),
            ("Задача", "Python", "31.02.2026"),
        ]

        for title, subject, due_date in invalid_inputs:
            with self.subTest(
                title=title,
                subject=subject,
                due_date=due_date,
            ):
                with self.assertRaises(ValueError):
                    edit_task(
                        self.task_id,
                        title,
                        subject,
                        due_date,
                        self.db_path,
                    )

                self.assertEqual(get_all_tasks(self.db_path), original)

    def test_edit_does_not_change_other_tasks(self):
        second_id = create_task(
            "Втора задача", "Математика", "16.10.2026", self.db_path
        )
        original_second = next(
            task
            for task in get_all_tasks(self.db_path)
            if task["id"] == second_id
        )

        edit_task(
            self.task_id,
            "Променена първа задача",
            "Python",
            "20.10.2026",
            self.db_path,
        )

        current_second = next(
            task
            for task in get_all_tasks(self.db_path)
            if task["id"] == second_id
        )

        self.assertEqual(current_second, original_second)

    def test_missing_task_raises_error_without_changing_data(self):
        original = get_all_tasks(self.db_path)

        with self.assertRaisesRegex(ValueError, "не съществува"):
            edit_task(
                self.task_id + 1000,
                "Задача",
                "Python",
                "15.10.2026",
                self.db_path,
            )

        self.assertEqual(get_all_tasks(self.db_path), original)


if __name__ == "__main__":
    unittest.main()