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
from rizum_ui import AnimatedSaveButton, TextActionButton


class FontPreviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    def make_panel(self, variant):
        panel = build_font_preview(QtWidgets, size_control_variant=variant)
        self.addCleanup(panel.deleteLater)
        return panel

    def test_comparison_changes_only_the_size_control_variant(self):
        compact = self.make_panel("compact")
        spin = self.make_panel("spin")

        self.assertEqual(compact._rizum_size_control.objectName(), "RizumCompactStepper")
        self.assertEqual(spin._rizum_size_control.objectName(), "RizumMockInput")
        for panel in (compact, spin):
            self.assertIsInstance(panel._rizum_reset_button, TextActionButton)
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
            ["original", "compact", "spin"],
        )
        original = comparison._rizum_candidates[0]
        self.assertEqual(original._rizum_reset_button.text(), "Reset")
        self.assertEqual(original._rizum_save_button.text(), "Apply")

        standalone = build_font_preview_original(QtWidgets)
        self.addCleanup(standalone.deleteLater)
        self.assertEqual(standalone.size(), original.size())

    def test_save_state_is_owned_by_the_footer_action(self):
        panel = self.make_panel("spin")
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

    def test_both_variants_scale_from_the_same_baseline(self):
        for variant in ("compact", "spin"):
            panel = self.make_panel(variant)
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
