"""Regression tests for the canonical Painter settings layout."""

from __future__ import annotations

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6 import QtWidgets

from rizum_ui import PAINTER_SETTINGS_LAYOUT, PainterSettingsDialog


class PainterSettingsLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
        cls.app.setProperty("rizumUiFontScale", 1.0)

    def test_live_view_roll_metrics_are_the_shared_baseline(self):
        layout = PAINTER_SETTINGS_LAYOUT

        self.assertEqual(layout.dialog_width.design, 300)
        self.assertEqual(layout.body_margin_x.design, 20)
        self.assertEqual(layout.body_margin_top.design, 12)
        self.assertEqual(layout.body_margin_bottom.design, 20)
        self.assertEqual(layout.first_section_height.design, 26)
        self.assertEqual(layout.section_height.design, 36)
        self.assertEqual(layout.row_height.design, 40)
        self.assertEqual(layout.detail_row_height.design, 46)
        self.assertEqual(layout.control_height.design, 30)
        self.assertEqual(layout.stepper_height.design, 32)
        self.assertEqual(layout.footer_margin_x.design, 20)
        self.assertEqual(layout.footer_row_height.design, 32)
        self.assertEqual(layout.footer_button_height.design, 28)
        self.assertEqual(layout.row_spacing, 8)
        self.assertEqual(layout.footer_button_spacing, 8)

    def test_metrics_resolve_through_the_dialog_ui_scale(self):
        dialog = PainterSettingsDialog()
        self.addCleanup(dialog.deleteLater)
        dialog.setSettingsUiScale(1.1)

        self.assertEqual(
            PAINTER_SETTINGS_LAYOUT.body_margin_x.resolve(dialog),
            22,
        )
        self.assertEqual(
            PAINTER_SETTINGS_LAYOUT.row_height.resolve(dialog),
            44,
        )
        self.assertEqual(
            PAINTER_SETTINGS_LAYOUT.detail_row_height.resolve(dialog),
            51,
        )
        self.assertEqual(
            PAINTER_SETTINGS_LAYOUT.control_height.resolve(dialog),
            33,
        )


if __name__ == "__main__":
    unittest.main()
