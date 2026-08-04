from __future__ import annotations

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6 import QtWidgets

from rizum_ui import AnimatedSaveButton, ModeParameterSlot, TextActionButton


class SettingsControlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    def test_text_action_scales_from_its_compact_height(self):
        button = TextActionButton("Restore")
        self.addCleanup(button.deleteLater)

        button.setCompactHeight(35)

        self.assertEqual(button.height(), 35)
        self.assertGreater(button.width(), 40)

    def test_save_button_exposes_clean_dirty_and_feedback_states(self):
        button = AnimatedSaveButton("Save")
        self.addCleanup(button.deleteLater)
        self.assertFalse(button.isEnabled())

        button.setDirty(True, animate=False)
        self.assertTrue(button.isEnabled())
        self.assertTrue(button.isDirty())

        button.showSavedFeedback()
        self.assertFalse(button.isEnabled())
        self.assertTrue(button.feedbackActive())

    def test_parameter_slot_switches_rows_atomically(self):
        speed = QtWidgets.QWidget()
        angle = QtWidgets.QWidget()
        slot = ModeParameterSlot({"continuous": speed, "custom": angle}, 46)
        self.addCleanup(slot.deleteLater)

        slot.setMode("continuous")
        self.assertEqual(slot.height(), 46)
        self.assertIs(slot._layout.currentWidget(), speed)

        slot.setMode("custom", animate=True)
        self.assertEqual(slot.height(), 46)
        self.assertIs(slot._layout.currentWidget(), angle)
        self.assertIsNone(speed.graphicsEffect())
        self.assertIsNone(angle.graphicsEffect())

        slot.setMode("step_15")
        self.assertEqual(slot.height(), 0)


if __name__ == "__main__":
    unittest.main()
