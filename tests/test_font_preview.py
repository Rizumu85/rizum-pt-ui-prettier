from __future__ import annotations

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6 import QtCore, QtTest, QtWidgets

from preview import (
    build_font_comparison,
    build_font_preview,
    build_font_preview_original,
)
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
        self.assertEqual(panel._rizum_footer.height(), 48)
        self.assertEqual(
            [(button.width(), button.height()) for button in panel._rizum_icon_buttons],
            [(22, 22), (22, 22), (22, 22)],
        )

    def test_comparison_keeps_the_original_as_a_visual_baseline(self):
        comparison = build_font_comparison(QtWidgets)
        self.addCleanup(comparison.deleteLater)

        self.assertEqual(
            [panel._rizum_size_control_variant for panel in comparison._rizum_candidates],
            ["original", "spin"],
        )
        original = comparison._rizum_candidates[0]
        self.assertEqual(original._rizum_size_control.objectName(), "RizumMockInput")
        self.assertIsNotNone(original._rizum_undo_button)
        self.assertEqual(original._rizum_reset_button.text(), "Reset")
        self.assertEqual(original._rizum_save_button.text(), "Save")

        standalone = build_font_preview_original(QtWidgets)
        self.addCleanup(standalone.deleteLater)
        self.assertEqual(standalone.size(), original.size())

    def test_original_matches_the_live_ui_font_layout_metrics(self):
        panel = build_font_preview_original(QtWidgets)
        self.addCleanup(panel.deleteLater)
        panel.show()
        self.app.processEvents()

        self.assertEqual(panel._rizum_card_layout.getContentsMargins(), (0, 0, 0, 8))
        self.assertEqual(panel._rizum_main_layout.getContentsMargins(), (12, 12, 12, 6))
        self.assertEqual(panel._rizum_main_layout.spacing(), 10)
        self.assertEqual([row.height() for row in panel._rizum_rows], [32, 32])
        self.assertEqual(panel._rizum_size_control.size(), QtCore.QSize(120, 32))
        self.assertEqual(panel._rizum_icon_group.spacing(), 2)
        self.assertEqual(
            [(button.size(), button._icon_size) for button in panel._rizum_icon_buttons],
            [(QtCore.QSize(32, 32), 17)] * 3,
        )
        self.assertEqual(
            panel._rizum_hint_widget.layout().getContentsMargins(),
            (8, 4, 9, 4),
        )
        self.assertEqual(panel._rizum_hint_widget.minimumWidth(), 108)
        self.assertEqual(panel._rizum_footer.height(), 48)
        self.assertFalse(panel._rizum_undo_button.isEnabled())
        self.assertEqual(panel._rizum_reset_button.size(), QtCore.QSize(68, 26))
        self.assertEqual(panel._rizum_save_button.size(), QtCore.QSize(72, 26))

        panel._rizum_size_control.setValue(1.5)
        self.app.processEvents()
        self.assertEqual(panel._rizum_card_layout.getContentsMargins(), (0, 0, 0, 12))
        self.assertEqual(panel._rizum_main_layout.getContentsMargins(), (18, 18, 18, 9))
        self.assertEqual(panel._rizum_main_layout.spacing(), 15)
        self.assertEqual([row.height() for row in panel._rizum_rows], [48, 48])
        self.assertEqual(panel._rizum_icon_buttons[0].size(), QtCore.QSize(48, 48))
        self.assertEqual(panel._rizum_icon_buttons[0]._icon_size, 26)
        self.assertEqual(
            panel._rizum_hint_widget.layout().getContentsMargins(),
            (12, 6, 14, 6),
        )
        self.assertEqual(panel._rizum_hint_widget.minimumWidth(), 162)
        self.assertEqual(panel._rizum_footer.height(), 72)
        self.assertEqual(panel._rizum_reset_button.height(), 39)
        self.assertEqual(panel._rizum_save_button.height(), 39)

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
        panel._rizum_size_control.setValue(1.5)
        self.app.processEvents()
        self.assertEqual(panel._rizum_size_control.height(), 48)
        self.assertEqual(panel._rizum_footer.height(), 72)

        panel._rizum_size_control.setValue(0.75)
        self.app.processEvents()
        self.assertEqual(panel._rizum_size_control.height(), 24)
        self.assertEqual(panel._rizum_footer.height(), 36)


if __name__ == "__main__":
    unittest.main()
