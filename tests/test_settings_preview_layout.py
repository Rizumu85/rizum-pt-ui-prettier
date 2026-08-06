from __future__ import annotations

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6 import QtWidgets

from preview import build_settings_preview
from rizum_ui import PAINTER_SETTINGS_LAYOUT


class SettingsPreviewLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    def setUp(self):
        self.app.setProperty("rizumUiFontScale", 1.0)
        self.app.setProperty("rizumPreviewLanguage", "en")

    def make_panel(self):
        panel = build_settings_preview(QtWidgets)
        self.addCleanup(panel.deleteLater)
        return panel

    def test_dark_surface_and_rows_match_the_codex_visual_standard(self):
        panel = self.make_panel()
        stylesheet = panel.settingsSurface().styleSheet()

        self.assertIn("background: #202020", stylesheet)
        self.assertNotIn("QFrame#RizumSettingsRow:hover", stylesheet)
        sections = panel.findChildren(QtWidgets.QLabel, "RizumSettingsSection")
        self.assertEqual(
            [label.text() for label in sections],
            ["EXPORT", "PHOTOSHOP", "ABOUT"],
        )
        self.assertEqual(
            panel._rizum_bit_depth.height(),
            PAINTER_SETTINGS_LAYOUT.control_height.design,
        )
        self.assertEqual(
            [row.height() for row in panel._rizum_rows],
            [46, 46, 40, 46, 40, 40],
        )

    def test_preview_replicates_the_live_bit_depth_choices(self):
        panel = self.make_panel()
        control = panel._rizum_bit_depth

        self.assertEqual(control.findData(None), 0)
        self.assertEqual(control.findData(8), 1)
        self.assertEqual(control.findData(16), 2)
        control.setCurrentIndex(0)
        self.assertEqual(control.currentText(), "Texture Set")

    def test_localized_bit_depth_value_is_not_clipped_at_large_scale(self):
        self.app.setProperty("rizumPreviewLanguage", "es")
        self.app.setProperty("rizumUiFontScale", 1.5)
        panel = self.make_panel()
        panel.show()
        self.app.processEvents()

        label = panel._rizum_bit_depth._label
        self.assertLessEqual(label.sizeHint().width(), label.width())

    def test_ui_scale_updates_layout_and_painted_controls_together(self):
        panel = self.make_panel()
        panel.setSettingsUiScale(1.1)

        body_margins = panel._rizum_body_layout.contentsMargins()
        self.assertEqual(body_margins.left(), 22)
        self.assertEqual(body_margins.top(), 13)
        self.assertEqual(
            [row.height() for row in panel._rizum_rows],
            [51, 51, 44, 51, 44, 44],
        )
        self.assertEqual(panel._rizum_bit_depth.height(), 33)
        self.assertEqual(panel._rizum_done_button.height(), 31)
        self.assertEqual(panel._rizum_padding_toggle.height(), 22)

    def test_dilation_reveal_changes_only_its_canonical_row_and_gap(self):
        panel = self.make_panel()
        reveal = panel._rizum_dilation_reveal
        collapsed_height = panel.height()

        reveal.setExpanded(True, animate=False)
        self.assertEqual(
            panel.height() - collapsed_height,
            PAINTER_SETTINGS_LAYOUT.detail_row_height.design
            + PAINTER_SETTINGS_LAYOUT.body_spacing.design,
        )
        reveal.setExpanded(False, animate=False)
        self.assertEqual(panel.height(), collapsed_height)


if __name__ == "__main__":
    unittest.main()
