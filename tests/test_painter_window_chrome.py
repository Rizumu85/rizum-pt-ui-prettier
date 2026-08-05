from __future__ import annotations

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6 import QtCore, QtWidgets

from preview import build_bridge_preview, build_settings_preview
from rizum_ui import (
    PAINTER_FOOTER_MARGIN_BOTTOM,
    PAINTER_FOOTER_MARGIN_X,
    make_painter_title_bar,
)
from view_roll_preview import ViewRollConceptPanel


class PainterWindowChromeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
        cls.app.setProperty("rizumUiFontScale", 1.0)

    def test_title_bar_stays_at_native_metrics_when_content_scale_changes(self):
        title_bar = make_painter_title_bar("Export")
        self.addCleanup(title_bar.deleteLater)

        self.assertEqual(title_bar.height(), 32)
        title_bar.setCompactHeight(40)
        self.assertEqual(title_bar.height(), 32)
        icon = title_bar.findChild(QtWidgets.QLabel, "RizumPainterTitleBarIcon")
        title = title_bar.findChild(QtWidgets.QLabel, "RizumPainterTitleBarText")
        self.assertEqual((icon.width(), icon.height()), (14, 14))
        self.assertEqual(title.font().pixelSize(), 12)
        self.assertTrue(
            title_bar.testAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground)
        )

    def test_reference_panels_omit_platform_owned_title_bars(self):
        panels = [
            build_bridge_preview(QtWidgets),
            build_settings_preview(QtWidgets),
            ViewRollConceptPanel(),
        ]
        for panel in panels:
            self.addCleanup(panel.deleteLater)
            self.assertEqual(
                len(
                    panel.findChildren(
                        QtWidgets.QWidget,
                        "RizumPainterTitleBar",
                    )
                ),
                0,
            )
            self.assertEqual(
                len(
                    panel.findChildren(
                        QtWidgets.QFrame,
                        "RizumPainterWindowContent",
                    )
                ),
                1,
            )

    def test_preview_panels_do_not_duplicate_native_window_titles(self):
        panels = [
            (build_bridge_preview(QtWidgets), "RizumExportTitle"),
            (build_settings_preview(QtWidgets), "RizumSettingsTitle"),
            (ViewRollConceptPanel(), "RizumViewRollTitle"),
        ]
        for panel, old_title_name in panels:
            self.addCleanup(panel.deleteLater)
            self.assertIsNone(panel.findChild(QtWidgets.QLabel, old_title_name))

    def test_view_roll_preview_has_no_platform_frame_decoration(self):
        panel = ViewRollConceptPanel()
        self.addCleanup(panel.deleteLater)

        content = panel.findChild(QtWidgets.QFrame, "RizumPainterWindowContent")
        self.assertIsNotNone(content)
        self.assertIn(
            "border-top-left-radius: 0px",
            content.styleSheet(),
        )
        self.assertIn(
            "border-bottom-left-radius: 0px",
            content.styleSheet(),
        )
        self.assertIn(
            "background: #1b1b1b",
            panel.dialog.settingsSurface().styleSheet(),
        )

    def test_preview_footers_share_painter_edge_margins(self):
        bridge = build_bridge_preview(QtWidgets)
        settings = build_settings_preview(QtWidgets)
        self.addCleanup(bridge.deleteLater)
        self.addCleanup(settings.deleteLater)

        for footer_name in ("RizumExportFooter", "RizumSettingsFooter"):
            owner = bridge if footer_name == "RizumExportFooter" else settings
            footer = owner.findChild(QtWidgets.QWidget, footer_name)
            row = footer.layout()
            if footer_name == "RizumSettingsFooter":
                row = footer.findChild(
                    QtWidgets.QWidget, "RizumSettingsFooterRow"
                ).layout()
            margins = row.contentsMargins()
            self.assertEqual(margins.left(), PAINTER_FOOTER_MARGIN_X)
            self.assertEqual(margins.right(), PAINTER_FOOTER_MARGIN_X)
            self.assertEqual(margins.bottom(), PAINTER_FOOTER_MARGIN_BOTTOM)


if __name__ == "__main__":
    unittest.main()
