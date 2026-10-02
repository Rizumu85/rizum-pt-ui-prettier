from __future__ import annotations

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6 import QtWidgets

from rizum_ui import make_combo_input, make_popup_menu, popup_menu_stylesheet


class PopupMenuScaleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    def tearDown(self):
        self.app.setProperty("rizumUiFontScale", 1.0)

    def test_font_follows_ui_font_scale(self):
        self.app.setProperty("rizumUiFontScale", 1.5)
        menu = make_popup_menu()
        self.addCleanup(menu.deleteLater)
        self.assertEqual(menu.objectName(), "RizumPopupMenu")
        self.assertIn("font-size: 18px;", menu.styleSheet())

    def test_scale_floor_is_three_quarters(self):
        self.assertIn("font-size: 9px;", popup_menu_stylesheet(0.5))

    def test_refresh_metrics_rescales_a_kept_menu_and_keeps_extra_rules(self):
        menu = make_popup_menu(extra_stylesheet="QMenu#RizumPopupMenu::icon { left: 6px; }")
        self.addCleanup(menu.deleteLater)
        self.assertIn("font-size: 12px;", menu.styleSheet())
        self.app.setProperty("rizumUiFontScale", 2.0)
        menu.refreshMetrics()
        self.assertIn("font-size: 24px;", menu.styleSheet())
        self.assertTrue(menu.styleSheet().rstrip().endswith("left: 6px; }"))

    def test_disabled_items_are_muted_text_not_boxes(self):
        sheet = popup_menu_stylesheet(1.0)
        self.assertIn("::item:disabled", sheet)
        self.assertIn("background: transparent;", sheet)

    def test_combo_input_uses_the_shared_menu(self):
        self.app.setProperty("rizumUiFontScale", 1.5)
        combo = make_combo_input([("One", 1), ("Two", 2)])
        self.addCleanup(combo.deleteLater)
        combo.resize(120, 30)
        combo.show()
        from PySide6 import QtCore, QtTest

        QtTest.QTest.mouseClick(combo, QtCore.Qt.MouseButton.LeftButton)
        self.assertIsNotNone(combo._menu)
        self.assertIn("font-size: 18px;", combo._menu.styleSheet())
        combo._menu.close()


if __name__ == "__main__":
    unittest.main()
