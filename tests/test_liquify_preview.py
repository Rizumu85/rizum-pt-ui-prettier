from __future__ import annotations

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6 import QtCore, QtTest, QtWidgets

from liquify_preview import LiquifyPreviewPanel, build_liquify_preview
from rizum_ui import AnimatedSaveButton, SecondaryActionButton, StatusBanner


class LiquifyPreviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    def setUp(self):
        self.app.setProperty("rizumUiFontScale", 1.0)
        self.app.setProperty("rizumPreviewLanguage", "en")

    def make_panel(self, state="ready", width_mode="standard"):
        panel = LiquifyPreviewPanel(state, width_mode)
        self.addCleanup(panel.deleteLater)
        panel.show()
        self.app.processEvents()
        return panel

    def test_page_exposes_one_interactive_latest_prototype(self):
        page = build_liquify_preview(QtWidgets)
        self.addCleanup(page.deleteLater)

        self.assertIsInstance(page._rizum_panel, LiquifyPreviewPanel)
        self.assertEqual(page._rizum_panel.state(), "ready")
        self.assertEqual(page._rizum_state_control.currentData(), "ready")
        self.assertEqual(page._rizum_width_control.currentData(), "standard")
        self.assertEqual(
            len(page.findChildren(QtWidgets.QFrame, "RizumCompactDockCard")),
            1,
        )

    def test_six_workflow_states_own_the_primary_and_apply_actions(self):
        panel = self.make_panel()
        expectations = {
            "empty": ("Create Target", False, "neutral"),
            "ready": ("Start Liquify", True, "good"),
            "active": ("Return to Painting", True, "accent"),
            "repair": ("Repair and Start", False, "warn"),
            "blocked": ("Start Liquify", False, "warn"),
            "complete": ("Create Target", False, "good"),
        }
        for state, (primary, can_apply, tone) in expectations.items():
            panel.setState(state)
            self.app.processEvents()
            self.assertEqual(panel.primary_button.text(), primary)
            self.assertEqual(panel.apply_button.isEnabled(), can_apply)
            self.assertEqual(panel.status_banner.tone(), tone)
            self.assertTrue(panel.new_target_button.isVisible())

    def test_primary_action_and_fixed_plus_follow_the_recommended_flow(self):
        panel = self.make_panel("empty", "narrow")

        QtTest.QTest.mouseClick(
            panel.primary_button,
            QtCore.Qt.MouseButton.LeftButton,
        )
        self.assertEqual(panel.state(), "active")
        QtTest.QTest.mouseClick(
            panel.primary_button,
            QtCore.Qt.MouseButton.LeftButton,
        )
        self.assertEqual(panel.state(), "ready")
        QtTest.QTest.mouseClick(
            panel.new_target_button,
            QtCore.Qt.MouseButton.LeftButton,
        )
        self.assertEqual(panel.state(), "active")

    def test_blockers_expand_in_place_without_enabling_apply(self):
        panel = self.make_panel("blocked")
        base_height = panel.height()

        QtTest.QTest.mouseClick(
            panel.status_banner._action,
            QtCore.Qt.MouseButton.LeftButton,
        )
        self.app.processEvents()

        self.assertTrue(panel.blocker_details.isVisible())
        self.assertGreater(panel.height(), base_height)
        self.assertEqual(panel.status_banner.actionText(), "Hide")
        self.assertFalse(panel.apply_button.isEnabled())

    def test_shared_controls_and_compact_metrics_scale_from_one_baseline(self):
        panel = self.make_panel("ready", "narrow")

        self.assertIsInstance(panel.status_banner, StatusBanner)
        self.assertIsInstance(panel.primary_button, SecondaryActionButton)
        self.assertIsInstance(panel.apply_button, AnimatedSaveButton)
        self.assertEqual(panel.width(), 250)
        self.assertEqual(panel.target_combo.height(), 32)
        self.assertEqual(panel.status_banner.height(), 54)
        self.assertEqual(panel._footer.height(), 48)
        self.assertEqual(panel.new_target_button.size(), QtCore.QSize(22, 22))

        self.app.setProperty("rizumUiFontScale", 1.5)
        panel.refreshMetrics()
        self.app.processEvents()
        self.assertEqual(panel.width(), 375)
        self.assertEqual(panel.target_combo.height(), 48)
        self.assertEqual(panel.status_banner.height(), 81)
        self.assertEqual(panel._footer.height(), 72)
        self.assertEqual(panel.new_target_button.size(), QtCore.QSize(33, 33))

    def test_status_banner_scales_its_action_and_updates_in_place(self):
        banner = StatusBanner("Needs repair", "Managed layers are incomplete", "warn", "Repair")
        self.addCleanup(banner.deleteLater)

        self.assertEqual(banner.height(), 54)
        self.assertEqual(banner.actionText(), "Repair")
        self.assertEqual(banner.tone(), "warn")
        banner.setCompactHeight(81)
        self.assertEqual(banner.height(), 81)
        self.assertGreaterEqual(banner._action.height(), 39)
        banner.setStatus("Ready", "", "good")
        self.assertEqual(banner.title(), "Ready")
        self.assertEqual(banner.tone(), "good")
        self.assertFalse(banner._action.isVisible())

    def test_all_preview_languages_build_at_narrow_width(self):
        for language in ("en", "de", "es", "fr", "it", "ja_JP", "ko", "pt", "zh_CN"):
            self.app.setProperty("rizumPreviewLanguage", language)
            panel = self.make_panel("empty", "narrow")
            self.assertEqual(panel.width(), 250)
            self.assertLessEqual(panel.primary_button.sizeHint().width(), panel.width() - 24)


if __name__ == "__main__":
    unittest.main()
