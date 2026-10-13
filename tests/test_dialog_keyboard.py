import unittest
from unittest.mock import Mock

from studytrack.ui import AddTaskDialog


class DialogKeyboardTests(unittest.TestCase):
    def test_enter_on_cancel_closes_without_saving(self):
        dialog = Mock()
        dialog.focus_get.return_value = dialog.cancel_button

        result = AddTaskDialog.handle_enter(dialog)

        dialog.destroy.assert_called_once()
        dialog.submit.assert_not_called()
        self.assertEqual(result, "break")

    def test_enter_in_input_field_submits(self):
        dialog = Mock()
        dialog.focus_get.return_value = Mock()

        result = AddTaskDialog.handle_enter(dialog)

        dialog.submit.assert_called_once()
        dialog.destroy.assert_not_called()
        self.assertEqual(result, "break")


if __name__ == "__main__":
    unittest.main()