import unittest
from copy import deepcopy

from studytrack.services import filter_tasks


class TaskFilteringTests(unittest.TestCase):
    def setUp(self):
        self.tasks = [
            {
                "id": 1,
                "title": "Първа задача",
                "subject": "Python",
                "due_date": "2026-10-15",
                "is_completed": 0,
            },
            {
                "id": 2,
                "title": "Втора задача",
                "subject": "Python",
                "due_date": "2026-10-16",
                "is_completed": 1,
            },
            {
                "id": 3,
                "title": "Трета задача",
                "subject": "Математика",
                "due_date": "2026-10-17",
                "is_completed": 0,
            },
        ]

    def test_no_filters_returns_all_tasks(self):
        self.assertEqual(filter_tasks(self.tasks), self.tasks)

    def test_subject_filter(self):
        result = filter_tasks(self.tasks, subject="Python")

        self.assertEqual([task["id"] for task in result], [1, 2])

    def test_status_filter_in_both_directions(self):
        for status, expected_ids in (
            (True, [2]),
            (False, [1, 3]),
        ):
            with self.subTest(status=status):
                result = filter_tasks(
                    self.tasks,
                    is_completed=status,
                )

                self.assertEqual(
                    [task["id"] for task in result],
                    expected_ids,
                )

    def test_filters_are_combined(self):
        result = filter_tasks(
            self.tasks,
            subject="Python",
            is_completed=False,
        )

        self.assertEqual([task["id"] for task in result], [1])

    def test_no_matching_tasks_returns_empty_list(self):
        result = filter_tasks(
            self.tasks,
            subject="Математика",
            is_completed=True,
        )

        self.assertEqual(result, [])

    def test_filtering_does_not_change_original_data(self):
        original = deepcopy(self.tasks)

        filter_tasks(
            self.tasks,
            subject="Python",
            is_completed=True,
        )

        self.assertEqual(self.tasks, original)
        self.assertEqual(filter_tasks(self.tasks), original)


if __name__ == "__main__":
    unittest.main()