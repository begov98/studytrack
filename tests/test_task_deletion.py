import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from studytrack.database import get_all_tasks, initialize_database
from studytrack.services import create_task, remove_task
from studytrack.ui import StudyTrackApp


class TaskDeletionTests(unittest.TestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_directory.cleanup)
        self.db_path = Path(self.temp_directory.name) / "test.db"
        initialize_database(self.db_path)

        self.first_id = create_task(
            "Първа задача", "Python", "15.10.2026", self.db_path
        )
        self.second_id = create_task(
            "Втора задача", "Python", "16.10.2026", self.db_path
        )

    def test_deletion_removes_only_selected_task(self):
        remove_task(self.first_id, self.db_path)

        tasks = get_all_tasks(self.db_path)

        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["id"], self.second_id)
        self.assertEqual(tasks[0]["title"], "Втора задача")

    def test_deleted_task_stays_deleted_after_reinitialization(self):
        remove_task(self.first_id, self.db_path)
        initialize_database(self.db_path)

        ids = [task["id"] for task in get_all_tasks(self.db_path)]

        self.assertNotIn(self.first_id, ids)
        self.assertIn(self.second_id, ids)

    def test_missing_task_does_not_delete_other_tasks(self):
        original = get_all_tasks(self.db_path)

        with self.assertRaisesRegex(ValueError, "не съществува"):
            remove_task(self.second_id + 1000, self.db_path)

        self.assertEqual(get_all_tasks(self.db_path), original)


class TaskDeletionUiTests(unittest.TestCase):
    def setUp(self):
        self.app = Mock()
        self.app.task_table.selection.return_value = ("7",)
        self.app.task_table.item.return_value = (
            "Примерна задача",
            "Python",
            "15.10.2026",
            "Незавършена",
        )

    @patch("studytrack.ui.remove_task")
    @patch("studytrack.ui.messagebox.askyesno", return_value=False)
    def test_cancel_does_not_delete_task(self, mock_confirm, mock_remove):
        StudyTrackApp.delete_selected_task(self.app)

        mock_confirm.assert_called_once()
        self.assertIn(
            "Примерна задача",
            mock_confirm.call_args.args[1],
        )
        mock_remove.assert_not_called()
        self.app.refresh_tasks.assert_not_called()

    @patch("studytrack.ui.remove_task")
    @patch("studytrack.ui.messagebox.askyesno", return_value=True)
    def test_confirmation_deletes_selected_task(
        self, mock_confirm, mock_remove
    ):
        StudyTrackApp.delete_selected_task(self.app)

        mock_remove.assert_called_once_with(7)
        self.app.refresh_tasks.assert_called_once()

    @patch("studytrack.ui.remove_task")
    @patch("studytrack.ui.messagebox.askyesno")
    @patch("studytrack.ui.messagebox.showinfo")
    def test_no_selection_does_not_attempt_deletion(
        self, mock_info, mock_confirm, mock_remove
    ):
        self.app.task_table.selection.return_value = ()

        StudyTrackApp.delete_selected_task(self.app)

        mock_info.assert_called_once()
        mock_confirm.assert_not_called()
        mock_remove.assert_not_called()


if __name__ == "__main__":
    unittest.main()