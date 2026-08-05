from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6 import QtCore, QtWidgets


ROOT = Path(__file__).resolve().parents[1]


def install_painter_stub(main_window):
    painter = types.ModuleType("substance_painter")
    painter_ui = types.ModuleType("substance_painter.ui")
    painter_logging = types.ModuleType("substance_painter.logging")
    painter_ui.get_main_window = lambda: main_window
    painter_ui.add_menu = lambda menu: None
    painter_ui.delete_ui_element = lambda element: None
    painter_logging.info = lambda message: None
    painter_logging.warning = lambda message: None
    painter.ui = painter_ui
    painter.logging = painter_logging
    sys.modules["substance_painter"] = painter
    sys.modules["substance_painter.ui"] = painter_ui
    sys.modules["substance_painter.logging"] = painter_logging


def load_plugin():
    name = "rizum_pt_drag_distance_test"
    spec = importlib.util.spec_from_file_location(
        name,
        ROOT / "__init__.py",
        submodule_search_locations=[str(ROOT)],
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class DragDistanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
        cls.app.setProperty("rizumUiFontScale", 1.0)
        cls.main_window = QtWidgets.QWidget()
        install_painter_stub(cls.main_window)
        cls.settings_dir = tempfile.TemporaryDirectory()
        QtCore.QSettings.setDefaultFormat(QtCore.QSettings.Format.IniFormat)
        QtCore.QSettings.setPath(
            QtCore.QSettings.Format.IniFormat,
            QtCore.QSettings.Scope.UserScope,
            cls.settings_dir.name,
        )

        plugin_module = load_plugin()
        ui_module = sys.modules[f"{plugin_module.__name__}.ui"]

        cls.DEFAULT_DRAG_DISTANCE = ui_module.DEFAULT_DRAG_DISTANCE
        cls.RizumDragDistanceSettings = (
            plugin_module.RizumDragDistanceSettings
        )
        cls.SETTINGS_APPLICATION = ui_module.SETTINGS_APPLICATION
        cls.SETTINGS_ORGANIZATION = ui_module.SETTINGS_ORGANIZATION
        cls.SettingsDialog = ui_module.SettingsDialog

    @classmethod
    def tearDownClass(cls):
        cls.main_window.deleteLater()
        cls.settings_dir.cleanup()

    def setUp(self):
        settings = QtCore.QSettings(
            self.SETTINGS_ORGANIZATION,
            self.SETTINGS_APPLICATION,
        )
        settings.clear()
        settings.sync()

    def test_menu_title_and_unsaved_default_are_updated(self):
        plugin = self.RizumDragDistanceSettings()
        self.addCleanup(plugin.menu.deleteLater)

        self.assertEqual(ROOT.name, "rizum-pt-drag-distance")
        self.assertEqual(plugin.menu.title(), "Drag Distance")
        self.assertEqual(
            plugin.menu.objectName(),
            "rizum_pt_drag_distance_menu",
        )
        self.assertEqual(self.DEFAULT_DRAG_DISTANCE, 50)
        self.assertEqual(QtWidgets.QApplication.startDragDistance(), 50)
        self.assertEqual(plugin.current_action.text(), "Current: 50 pixels")

    def test_dialog_uses_shared_compact_controls_and_standard_button_order(self):
        dialog = self.SettingsDialog(self.main_window)
        self.addCleanup(dialog.deleteLater)
        dialog.show()
        self.app.processEvents()

        self.assertEqual((dialog.width(), dialog.height()), (250, 96))
        self.assertEqual(dialog.spin_box.objectName(), "RizumCompactStepper")
        self.assertEqual(dialog.spin_box.value(), 50)
        self.assertIn(
            "background: #202020",
            dialog.settingsSurface().styleSheet(),
        )
        self.assertLess(dialog.cancel_button.x(), dialog.ok_button.x())
        self.assertEqual(dialog.cancel_button.width(), dialog.ok_button.width())
        self.assertEqual(dialog.cancel_button._background.name(), "#333333")
        self.assertEqual(dialog.spin_box._theme["muted"], "#9a9a9a")
        button_bottom = dialog._button_row.mapTo(
            dialog,
            QtCore.QPoint(0, dialog._button_row.height()),
        ).y()
        self.assertEqual(dialog.height() - button_bottom, 12)

    def test_dialog_scales_the_shared_controls_with_ui_font_scale(self):
        self.app.setProperty("rizumUiFontScale", 1.1)
        self.addCleanup(self.app.setProperty, "rizumUiFontScale", 1.0)
        dialog = self.SettingsDialog(self.main_window)
        self.addCleanup(dialog.deleteLater)

        self.assertEqual((dialog.width(), dialog.height()), (275, 106))
        self.assertEqual(dialog.spin_box.height(), 35)
        self.assertEqual(dialog.cancel_button.height(), 31)


if __name__ == "__main__":
    unittest.main()
