from __future__ import annotations

import os
import unittest
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6 import QtCore, QtWidgets

from preview import PREVIEW_LANGUAGES, _PREVIEW_TEXT, build_preview


SUPPORTED_LANGUAGE_CODES = {
    "en",
    "de",
    "es",
    "fr",
    "it",
    "ja_JP",
    "ko",
    "pt",
    "zh_CN",
}


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

    def test_language_picker_covers_the_painter_i18n_set(self):
        language_codes = {code for _label, code in PREVIEW_LANGUAGES}
        self.assertEqual(language_codes, SUPPORTED_LANGUAGE_CODES)
        self.assertEqual(set(_PREVIEW_TEXT), SUPPORTED_LANGUAGE_CODES - {"en"})

    def test_failed_rebuild_preserves_the_last_good_preview(self):
        window = QtWidgets.QWidget()
        self.addCleanup(window.deleteLater)
        window.setProperty("rizumPreviewUiScale", 1.0)

        original_tabs = build_preview(window, QtWidgets, False)
        window.show()
        self.app.processEvents()
        original_descendant_count = len(window.findChildren(QtWidgets.QWidget))
        original_top_levels = set(self.app.topLevelWidgets())

        with mock.patch(
            "view_roll_preview.build_view_roll_preview",
            side_effect=RuntimeError("incomplete source reload"),
        ):
            for _attempt in range(5):
                with self.assertRaisesRegex(RuntimeError, "incomplete source reload"):
                    build_preview(window, QtWidgets, False)
                self.app.sendPostedEvents(
                    None,
                    QtCore.QEvent.Type.DeferredDelete,
                )
                self.app.processEvents()

        self.assertIs(
            window.findChild(QtWidgets.QTabWidget, "RizumPreviewTabs"),
            original_tabs,
        )
        self.assertEqual(
            len(window.findChildren(QtWidgets.QWidget)),
            original_descendant_count,
        )
        self.assertFalse(set(self.app.topLevelWidgets()) - original_top_levels)

    def test_successful_rebuild_swaps_in_a_visible_preview(self):
        window = QtWidgets.QWidget()
        self.addCleanup(window.deleteLater)
        window.setProperty("rizumPreviewUiScale", 1.0)

        original_tabs = build_preview(window, QtWidgets, False)
        window.show()
        self.app.processEvents()
        rebuilt_tabs = build_preview(window, QtWidgets, False)
        self.app.sendPostedEvents(None, QtCore.QEvent.Type.DeferredDelete)
        self.app.processEvents()

        self.assertIsNot(rebuilt_tabs, original_tabs)
        self.assertIs(
            window.findChild(QtWidgets.QTabWidget, "RizumPreviewTabs"),
            rebuilt_tabs,
        )
        self.assertTrue(rebuilt_tabs.isVisible())
        self.assertEqual(window.layout().count(), 1)


if __name__ == "__main__":
    unittest.main()
