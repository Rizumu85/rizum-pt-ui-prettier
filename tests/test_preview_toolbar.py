from __future__ import annotations

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6 import QtWidgets

from preview import build_preview


class PreviewToolbarTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    def setUp(self):
        self.app.setProperty("rizumPreviewLanguage", "en")
        self.app.setProperty("rizumUiFontScale", 1.0)

    def test_global_scale_and_language_controls_are_above_the_tabs(self):
        window = QtWidgets.QWidget()
        self.addCleanup(window.deleteLater)
        window.setProperty("rizumPreviewUiScale", 1.0)

        build_preview(window, QtWidgets, False, lambda: None)
        window.show()
        self.app.processEvents()

        scale = window.findChild(QtWidgets.QFrame, "RizumPreviewScaleInput")
        language = window.findChild(QtWidgets.QFrame, "RizumPreviewLanguageInput")
        tabs = window.findChild(QtWidgets.QTabWidget, "RizumPreviewTabs")
        self.assertIsNotNone(scale)
        self.assertIsNotNone(language)
        self.assertIsNotNone(tabs)
        self.assertLess(scale.geometry().top(), tabs.geometry().top())
        self.assertIsNone(window.findChild(QtWidgets.QLabel, "RizumViewRollScaleHint"))

        scale.setValue(1.1)
        language.setCurrentIndex(language.findData("zh_CN"))
        self.app.processEvents()
        self.assertEqual(window.property("rizumPreviewUiScale"), 1.1)
        self.assertEqual(self.app.property("rizumUiFontScale"), 1.1)
        self.assertEqual(self.app.property("rizumPreviewLanguage"), "zh_CN")

    def test_language_selection_rebuilds_localized_tabs(self):
        self.app.setProperty("rizumPreviewLanguage", "zh_CN")
        window = QtWidgets.QWidget()
        self.addCleanup(window.deleteLater)

        tabs = build_preview(window, QtWidgets, False)

        self.assertEqual(tabs.tabText(0), "概览")
        self.assertEqual(tabs.tabText(2), "设置")


if __name__ == "__main__":
    unittest.main()
