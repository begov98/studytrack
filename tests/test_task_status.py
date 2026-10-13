import tempfile
import unittest
from pathlib import Path

from studytrack.database import get_all_tasks, initialize_database
from studytrack.services import change_task_status, create_task


class TaskStatusTests(unittest.TestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_directory.cleanup)
        self.db_path = Path(self.temp_directory.name) / "test.db"
        initialize_database(self.db_path)

        self.task_id = create_task(
            "Курсова работа",
            "Софтуерни процеси",
            "15.10.2026",
            self.db_path,
        )

    def test_incomplete_task_becomes_completed(self):
        change_task_status(self.task_id, self.db_path)

        task = get_all_tasks(self.db_path)[0]

        self.assertEqual(task["is_completed"], 1)

    def test_completed_task_becomes_incomplete(self):
        change_task_status(self.task_id, self.db_path)
        change_task_status(self.task_id, self.db_path)

        task = get_all_tasks(self.db_path)[0]

        self.assertEqual(task["is_completed"], 0)

    def test_status_is_preserved_after_reinitialization(self):
        change_task_status(self.task_id, self.db_path)
        initialize_database(self.db_path)

        task = get_all_tasks(self.db_path)[0]

        self.assertEqual(task["is_completed"], 1)

    def test_other_fields_and_other_tasks_remain_unchanged(self):
        create_task(
            "Втора задача",
            "Python",
            "16.10.2026",
            self.db_path,
        )
        original = get_all_tasks(self.db_path)

        change_task_status(self.task_id, self.db_path)

        expected = [dict(task) for task in original]
        for task in expected:
            if task["id"] == self.task_id:
                task["is_completed"] = 1

        self.assertEqual(get_all_tasks(self.db_path), expected)

    def test_missing_task_raises_error_without_changing_data(self):
        original = get_all_tasks(self.db_path)

        with self.assertRaisesRegex(ValueError, "не съществува"):
            change_task_status(self.task_id + 1000, self.db_path)

        self.assertEqual(get_all_tasks(self.db_path), original)


if __name__ == "__main__":
    unittest.main()