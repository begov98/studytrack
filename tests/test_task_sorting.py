import unittest
from copy import deepcopy

from studytrack.services import filter_tasks, sort_tasks_by_deadline


class TaskSortingTests(unittest.TestCase):
    def setUp(self):
        self.tasks = [
            {
                "id": 1,
                "title": "Януарска задача",
                "subject": "Python",
                "due_date": "2027-01-05",
                "is_completed": 0,
            },
            {
                "id": 2,
                "title": "Декемврийска задача",
                "subject": "Математика",
                "due_date": "2026-12-20",
                "is_completed": 1,
            },
            {
                "id": 3,
                "title": "Ноемврийска задача",
                "subject": "Python",
                "due_date": "2026-11-30",
                "is_completed": 0,
            },
        ]

    def test_ascending_order_across_months_and_years(self):
        result = sort_tasks_by_deadline(self.tasks)

        self.assertEqual(
            [task["id"] for task in result],
            [3, 2, 1],
        )

    def test_descending_order(self):
        result = sort_tasks_by_deadline(
            self.tasks,
            descending=True,
        )

        self.assertEqual(
            [task["id"] for task in result],
            [1, 2, 3],
        )

    def test_sorting_after_filtering(self):
        filtered = filter_tasks(
            self.tasks,
            subject="Python",
            is_completed=False,
        )
        result = sort_tasks_by_deadline(filtered)

        self.assertEqual(
            [task["id"] for task in result],
            [3, 1],
        )

    def test_sorting_does_not_change_original_data(self):
        original = deepcopy(self.tasks)

        sort_tasks_by_deadline(self.tasks)

        self.assertEqual(self.tasks, original)

    def test_empty_list(self):
        self.assertEqual(sort_tasks_by_deadline([]), [])

    def test_equal_dates_keep_both_tasks_in_original_order(self):
        tasks = [
            {**self.tasks[0], "due_date": "2026-10-15"},
            {**self.tasks[1], "due_date": "2026-10-15"},
        ]

        result = sort_tasks_by_deadline(tasks)

        self.assertEqual(
            [task["id"] for task in result],
            [1, 2],
        )


if __name__ == "__main__":
    unittest.main()