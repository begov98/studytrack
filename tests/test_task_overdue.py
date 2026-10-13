import unittest
from datetime import date

from studytrack.services import is_task_overdue


class TaskOverdueTests(unittest.TestCase):
    def setUp(self):
        self.today = date(2026, 10, 13)

    def test_incomplete_task_before_today_is_overdue(self):
        task = {
            "due_date": "2026-10-12",
            "is_completed": 0,
        }

        self.assertTrue(is_task_overdue(task, today=self.today))

    def test_task_due_today_is_not_overdue(self):
        task = {
            "due_date": "2026-10-13",
            "is_completed": 0,
        }

        self.assertFalse(is_task_overdue(task, today=self.today))

    def test_future_task_is_not_overdue(self):
        task = {
            "due_date": "2026-10-14",
            "is_completed": 0,
        }

        self.assertFalse(is_task_overdue(task, today=self.today))

    def test_completed_task_is_not_overdue(self):
        task = {
            "due_date": "2026-10-12",
            "is_completed": 1,
        }

        self.assertFalse(is_task_overdue(task, today=self.today))

    def test_previous_year_task_is_overdue(self):
        task = {
            "due_date": "2025-12-31",
            "is_completed": 0,
        }

        self.assertTrue(
            is_task_overdue(task, today=date(2026, 1, 1))
        )

    def test_result_changes_when_status_or_deadline_changes(self):
        task = {
            "due_date": "2026-10-12",
            "is_completed": 0,
        }

        self.assertTrue(is_task_overdue(task, today=self.today))

        task["is_completed"] = 1
        self.assertFalse(is_task_overdue(task, today=self.today))

        task["is_completed"] = 0
        task["due_date"] = "2026-10-14"
        self.assertFalse(is_task_overdue(task, today=self.today))


if __name__ == "__main__":
    unittest.main()