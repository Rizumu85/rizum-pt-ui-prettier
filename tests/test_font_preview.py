from __future__ import annotations

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6 import QtCore, QtTest, QtWidgets

from preview import build_font_preview
from rizum_ui import AnimatedSaveButton, SecondaryActionButton


class FontPreviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    def make_panel(self):
        panel = build_font_preview(QtWidgets)
        self.addCleanup(panel.deleteLater)
        return panel

    def test_redesign_preserves_layout_and_spin_input(self):
        panel = self.make_panel()

        self.assertEqual(panel._rizum_size_control.objectName(), "RizumMockInput")
        self.assertIsInstance(panel._rizum_reset_button, SecondaryActionButton)
        self.assertIsInstance(panel._rizum_save_button, AnimatedSaveButton)
        self.assertEqual(panel._rizum_card_layout.getContentsMargins(), (0, 0, 0, 8))
        self.assertEqual(
            panel._rizum_hint_widget.layout().getContentsMargins(),
            (8, 4, 8, 4),
        )
        self.assertEqual(panel._rizum_hint_widget.layout().spacing(), 10)
        self.assertEqual(panel._rizum_footer.height(), 48)
        self.assertEqual(
            [(button.width(), button.height()) for button in panel._rizum_icon_buttons],
            [(22, 22), (22, 22), (32, 32)],
        )
        self.assertEqual(panel._rizum_reset_button.size(), QtCore.QSize(68, 26))
        self.assertEqual(panel._rizum_save_button.size(), QtCore.QSize(72, 26))

    def test_save_state_is_owned_by_the_footer_action(self):
        panel = self.make_panel()
        panel.show()
        self.app.processEvents()

        self.assertFalse(panel._rizum_save_button.isEnabled())
        panel._rizum_size_control.setValue(1.1)
        self.app.processEvents()
        self.assertTrue(panel._rizum_save_button.isEnabled())
        self.assertTrue(panel._rizum_undo_button.isEnabled())

        QtTest.QTest.mouseClick(
            panel._rizum_save_button,
            QtCore.Qt.MouseButton.LeftButton,
        )
        self.assertTrue(panel._rizum_save_button.feedbackActive())
        self.assertFalse(panel._rizum_undo_button.isEnabled())

    def test_redesign_scales_from_the_original_baseline(self):
        panel = self.make_panel()
        base_label_width = panel._rizum_rows[0]._rizum_label.width()
        panel._rizum_size_control.setValue(1.5)
        self.app.processEvents()
        self.assertEqual(panel._rizum_size_control.height(), 48)
        self.assertEqual(panel._rizum_card_layout.getContentsMargins(), (0, 0, 0, 12))
        self.assertGreater(panel._rizum_rows[0]._rizum_label.width(), base_label_width)
        self.assertEqual(
            panel._rizum_hint_widget.layout().getContentsMargins(),
            (12, 6, 12, 6),
        )
        self.assertEqual(panel._rizum_hint_widget.layout().spacing(), 15)
        self.assertEqual(panel._rizum_footer.height(), 72)
        self.assertEqual(panel._rizum_undo_button.size(), QtCore.QSize(48, 48))

        panel._rizum_size_control.setValue(0.75)
        self.app.processEvents()
        self.assertEqual(panel._rizum_size_control.height(), 24)
        self.assertEqual(panel._rizum_card_layout.getContentsMargins(), (0, 0, 0, 6))
        self.assertLess(panel._rizum_rows[0]._rizum_label.width(), base_label_width)
        self.assertEqual(
            panel._rizum_hint_widget.layout().getContentsMargins(),
            (6, 3, 6, 3),
        )
        self.assertEqual(panel._rizum_hint_widget.layout().spacing(), 8)
        self.assertEqual(panel._rizum_footer.height(), 36)
        self.assertEqual(panel._rizum_undo_button.size(), QtCore.QSize(24, 24))


if __name__ == "__main__":
    unittest.main()
