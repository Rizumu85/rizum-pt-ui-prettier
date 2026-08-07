from __future__ import annotations

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6 import QtWidgets

from preview import build_dock_toolbar_preview
from rizum_ui import IconActionButton


def make_host(width):
    host = QtWidgets.QFrame()
    host.setFixedWidth(width)
    layout = QtWidgets.QVBoxLayout(host)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)
    toolbar = build_dock_toolbar_preview(QtWidgets)
    layout.addWidget(toolbar)
    host.show()
    return host, toolbar


class DockToolbarPreviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
        cls.app.setProperty("rizumUiFontScale", 1.0)

    def test_row_metrics(self):
        toolbar = build_dock_toolbar_preview(QtWidgets)
        self.addCleanup(toolbar.deleteLater)

        self.assertEqual(toolbar.height(), 44)
        margins = toolbar.layout().contentsMargins()
        self.assertEqual((margins.left(), margins.right()), (12, 12))
        self.assertEqual(toolbar.layout().spacing(), 6)

    def test_export_is_the_expanding_primary_action(self):
        toolbar = build_dock_toolbar_preview(QtWidgets)
        self.addCleanup(toolbar.deleteLater)

        export = toolbar._rizum_export_button
        self.assertIsInstance(export, IconActionButton)
        self.assertEqual(export.text(), "Export")
        self.assertEqual(export.height(), 28)
        self.assertEqual(export.minimumWidth(), 96)
        self.assertEqual(
            export.sizePolicy().horizontalPolicy(),
            QtWidgets.QSizePolicy.Policy.Expanding,
        )

    def test_bridge_and_settings_are_compact_icon_buttons(self):
        toolbar = build_dock_toolbar_preview(QtWidgets)
        self.addCleanup(toolbar.deleteLater)

        bridge = toolbar._rizum_bridge_button
        settings = toolbar._rizum_settings_button
        self.assertEqual((bridge.width(), bridge.height()), (22, 22))
        self.assertEqual((settings.width(), settings.height()), (22, 22))
        self.assertFalse(bridge.isEnabled())
        self.assertTrue(settings.isEnabled())

    def test_toolbar_stays_uncropped_at_210px(self):
        host, toolbar = make_host(210)
        self.addCleanup(host.deleteLater)

        self.assertGreaterEqual(toolbar.width(), 210)
        export = toolbar._rizum_export_button
        self.assertGreaterEqual(export.width(), 96)
        for button in (
            toolbar._rizum_bridge_button,
            toolbar._rizum_settings_button,
        ):
            right_edge = button.mapTo(toolbar, button.rect().topRight()).x()
            self.assertLessEqual(right_edge, toolbar.width())

    def test_export_grows_with_wider_containers(self):
        widths = {}
        for width in (210, 300, 420):
            host, toolbar = make_host(width)
            self.addCleanup(host.deleteLater)
            widths[width] = toolbar._rizum_export_button.width()

        self.assertLess(widths[210], widths[300])
        self.assertLess(widths[300], widths[420])


if __name__ == "__main__":
    unittest.main()
