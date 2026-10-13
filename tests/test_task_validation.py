import unittest

from studytrack.services import validate_task


class TaskValidationTests(unittest.TestCase):
    def test_valid_data_is_trimmed_and_date_is_converted(self):
        result = validate_task(
            "  Курсова работа  ",
            "  Софтуерни процеси  ",
            "  15.10.2026  ",
        )

        self.assertEqual(
            result,
            {
                "title": "Курсова работа",
                "subject": "Софтуерни процеси",
                "due_date": "2026-10-15",
            },
        )

    def test_blank_title_is_rejected(self):
        for title in ("", "   ", "\t"):
            with self.subTest(title=title):
                with self.assertRaisesRegex(ValueError, "заглавие"):
                    validate_task(title, "Python", "15.10.2026")

    def test_blank_subject_is_rejected(self):
        for subject in ("", "   ", "\t"):
            with self.subTest(subject=subject):
                with self.assertRaisesRegex(ValueError, "предмет"):
                    validate_task("Упражнение", subject, "15.10.2026")

    def test_blank_date_is_rejected(self):
        for due_date in ("", "   "):
            with self.subTest(due_date=due_date):
                with self.assertRaisesRegex(ValueError, "краен срок"):
                    validate_task("Упражнение", "Python", due_date)

    def test_wrong_date_format_is_rejected(self):
        for due_date in (
            "2026-10-15",
            "15/10/2026",
            "1.10.2026",
            "текст",
        ):
            with self.subTest(due_date=due_date):
                with self.assertRaisesRegex(ValueError, "формат"):
                    validate_task("Упражнение", "Python", due_date)

    def test_impossible_calendar_date_is_rejected(self):
        for due_date in ("31.02.2026", "29.02.2025", "15.13.2026"):
            with self.subTest(due_date=due_date):
                with self.assertRaisesRegex(ValueError, "календарна"):
                    validate_task("Упражнение", "Python", due_date)

    def test_leap_year_date_is_allowed(self):
        result = validate_task("Упражнение", "Python", "29.02.2024")

        self.assertEqual(result["due_date"], "2024-02-29")

    def test_past_date_is_allowed(self):
        result = validate_task("Упражнение", "Python", "01.01.2000")

        self.assertEqual(result["due_date"], "2000-01-01")


if __name__ == "__main__":
    unittest.main()