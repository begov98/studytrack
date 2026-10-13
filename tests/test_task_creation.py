import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from studytrack.database import get_all_tasks, initialize_database
from studytrack.services import create_task
from studytrack.ui import StudyTrackApp


class TaskCreationTests(unittest.TestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_directory.cleanup)
        self.db_path = Path(self.temp_directory.name) / "test.db"
        initialize_database(self.db_path)

    def test_valid_task_is_saved_as_incomplete(self):
        task_id = create_task(
            "  Курсова работа  ",
            "  Софтуерни процеси  ",
            "15.10.2026",
            self.db_path,
        )

        tasks = get_all_tasks(self.db_path)

        self.assertEqual(
            tasks,
            [
                {
                    "id": task_id,
                    "title": "Курсова работа",
                    "subject": "Софтуерни процеси",
                    "due_date": "2026-10-15",
                    "is_completed": 0,
                }
            ],
        )

    def test_invalid_data_does_not_create_records(self):
        invalid_inputs = [
            ("", "Python", "15.10.2026"),
            ("Упражнение", "   ", "15.10.2026"),
            ("Упражнение", "Python", "31.02.2026"),
        ]

        for title, subject, due_date in invalid_inputs:
            with self.subTest(
                title=title,
                subject=subject,
                due_date=due_date,
            ):
                with self.assertRaises(ValueError):
                    create_task(title, subject, due_date, self.db_path)

                self.assertEqual(get_all_tasks(self.db_path), [])

    def test_two_tasks_receive_different_ids(self):
        first_id = create_task(
            "Първа задача", "Python", "15.10.2026", self.db_path
        )
        second_id = create_task(
            "Втора задача", "Python", "16.10.2026", self.db_path
        )

        self.assertNotEqual(first_id, second_id)
        self.assertEqual(len(get_all_tasks(self.db_path)), 2)


class TaskCreationUiTests(unittest.TestCase):
    @patch("studytrack.ui.create_task")
    def test_list_is_refreshed_after_successful_save(self, mock_create):
        app = Mock()
        events = []

        def successful_save(*args):
            events.append("saved")
            return 42

        mock_create.side_effect = successful_save
        app.refresh_tasks.side_effect = lambda: events.append("refreshed")

        task_id = StudyTrackApp.save_new_task(
            app, "Упражнение", "Python", "15.10.2026"
        )

        self.assertEqual(task_id, 42)
        mock_create.assert_called_once_with(
            "Упражнение", "Python", "15.10.2026"
        )
        self.assertEqual(events, ["saved", "refreshed"])

    @patch("studytrack.ui.create_task")
    def test_list_is_not_refreshed_when_validation_fails(self, mock_create):
        app = Mock()
        mock_create.side_effect = ValueError("Въведи заглавие на задачата.")

        with self.assertRaises(ValueError):
            StudyTrackApp.save_new_task(
                app, "", "Python", "15.10.2026"
            )

        app.refresh_tasks.assert_not_called()


if __name__ == "__main__":
    unittest.main()