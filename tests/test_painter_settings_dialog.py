from __future__ import annotations

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6 import QtWidgets

from rizum_ui import PainterSettingsDialog


class PainterSettingsDialogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(
            []
        )

    def test_default_frame_and_surface_follow_painter_geometry(self):
        dialog = PainterSettingsDialog()
        margins = dialog.layout().contentsMargins()

        self.assertEqual(
            (margins.left(), margins.top(), margins.right(), margins.bottom()),
            (2, 0, 2, 2),
        )
        self.assertEqual(dialog.settingsFrameWidth(), 2)
        self.assertEqual(dialog.settingsSurfaceRadius(), 8.0)
        self.assertIn("background: #1b1b1b", dialog.settingsSurface().styleSheet())
        self.assertIn("border-radius: 8px", dialog.settingsSurface().styleSheet())

    def test_frame_width_recomputes_parallel_inner_curve(self):
        dialog = PainterSettingsDialog()

        dialog.setSettingsFrameWidth(3)

        margins = dialog.layout().contentsMargins()
        self.assertEqual(
            (margins.left(), margins.top(), margins.right(), margins.bottom()),
            (3, 0, 3, 3),
        )
        self.assertEqual(dialog.settingsSurfaceRadius(), 7.0)
        self.assertIn("border-radius: 7px", dialog.settingsSurface().styleSheet())

    def test_settings_typography_tracks_ui_font_scale(self):
        dialog = PainterSettingsDialog()

        dialog.setSettingsUiScale(1.1)

        stylesheet = dialog.settingsSurface().styleSheet()
        self.assertEqual(dialog.settingsUiScale(), 1.1)
        self.assertEqual(dialog.settingsMetric(13), 14)
        self.assertIn("font-size: 11px", stylesheet)
        self.assertIn("font-size: 14px", stylesheet)
        self.assertIn("font-size: 12px", stylesheet)
        self.assertIn("font-weight: 700", stylesheet)

    def test_section_heading_color_matches_pt_bridge_reference(self):
        dialog = PainterSettingsDialog()
        stylesheet = dialog.settingsSurface().styleSheet()

        self.assertIn(
            "QLabel#RizumSettingsSection {\n"
            "                color: #666666;",
            stylesheet,
        )

    def test_show_preserves_consumer_surface_rules_when_scale_is_unchanged(self):
        self.app.setProperty("rizumUiFontScale", 1.0)
        dialog = PainterSettingsDialog()
        self.addCleanup(dialog.deleteLater)
        surface = dialog.settingsSurface()
        consumer_rule = "QWidget#ConsumerPanel { background: transparent; }"
        surface.setStyleSheet(surface.styleSheet() + consumer_rule)

        dialog.show()
        self.app.processEvents()

        self.assertIn(consumer_rule, surface.styleSheet())

    def test_metadata_labels_do_not_paint_over_parent_hover_fill(self):
        dialog = PainterSettingsDialog()
        stylesheet = dialog.settingsSurface().styleSheet()

        self.assertIn(
            "QLabel#RizumSettingsItemMeta,\n"
            "            QLabel#RizumSettingsFooterHint {\n"
            "                background: transparent;",
            stylesheet,
        )


if __name__ == "__main__":
    unittest.main()
