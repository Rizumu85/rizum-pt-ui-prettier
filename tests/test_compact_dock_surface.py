from __future__ import annotations

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6 import QtCore, QtGui, QtWidgets

from rizum_ui import (
    COMPACT_DOCK_PANEL_BG,
    COMPACT_DOCK_TABBED_PANEL_BG,
    apply_compact_dock_surface,
    compact_dock_surface_color,
)


def _settle(app):
    for _ in range(3):
        app.processEvents()


class CompactDockSurfaceStateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    def setUp(self):
        self.window = QtWidgets.QMainWindow()
        self.window.setCentralWidget(QtWidgets.QWidget())
        self.surface = QtWidgets.QWidget()
        apply_compact_dock_surface(self.surface)
        self.dock = QtWidgets.QDockWidget("Plugin", self.window)
        self.dock.setWidget(self.surface)
        self.window.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self.dock)
        self.window.show()
        _settle(self.app)

    def tearDown(self):
        self.window.close()
        self.window.deleteLater()

    def _window_color(self):
        return self.surface.palette().color(QtGui.QPalette.ColorRole.Window).name()

    def test_standalone_dock_uses_title_bar_color(self):
        self.assertEqual(compact_dock_surface_color(self.surface), COMPACT_DOCK_PANEL_BG)
        self.assertEqual(self._window_color(), COMPACT_DOCK_PANEL_BG)
        self.assertFalse(bool(self.surface.property("rizumDockTabbed")))

    def test_tabbed_dock_switches_to_tab_color_and_back(self):
        other = QtWidgets.QDockWidget("Layers", self.window)
        other.setWidget(QtWidgets.QLabel("layers"))
        self.window.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, other)
        self.window.tabifyDockWidget(other, self.dock)
        self.dock.raise_()
        _settle(self.app)
        self.assertEqual(compact_dock_surface_color(self.surface), COMPACT_DOCK_TABBED_PANEL_BG)
        self.assertEqual(self._window_color(), COMPACT_DOCK_TABBED_PANEL_BG)
        self.assertTrue(self.surface.property("rizumDockTabbed"))

        self.dock.setFloating(True)
        _settle(self.app)
        self.assertEqual(self._window_color(), COMPACT_DOCK_PANEL_BG)
        self.assertFalse(self.surface.property("rizumDockTabbed"))


if __name__ == "__main__":
    unittest.main()
