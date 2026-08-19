from __future__ import annotations

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6 import QtCore, QtTest, QtWidgets

from liquify_preview import (
    LiquifyPreviewPanel,
    LiquifyPreviewPanelV2,
    build_liquify_preview,
)
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

    def test_page_places_codex_and_kimi_v2_side_by_side(self):
        page = build_liquify_preview(QtWidgets)
        self.addCleanup(page.deleteLater)

        self.assertIsInstance(page._rizum_panel, LiquifyPreviewPanel)
        self.assertIsInstance(page._rizum_panel_v2, LiquifyPreviewPanelV2)
        self.assertEqual(page._rizum_panel.state(), "ready")
        self.assertEqual(page._rizum_panel_v2.state(), "ready")
        self.assertEqual(page._rizum_state_control.currentData(), "ready")
        self.assertEqual(page._rizum_width_control.currentData(), "standard")
        self.assertEqual(
            len(page.findChildren(QtWidgets.QFrame, "RizumCompactDockCard")),
            2,
        )
        tags = [
            label.text()
            for label in page.findChildren(QtWidgets.QLabel, "RizumPreviewToolLabel")
        ]
        self.assertIn("CODEX", tags)
        self.assertIn("KIMI K3 V2", tags)
        self.assertNotIn("complete", LiquifyPreviewPanel.STATES)
        self.assertEqual(page._rizum_state_control.findData("complete"), -1)

    def test_state_and_width_controls_drive_both_panels(self):
        page = build_liquify_preview(QtWidgets)
        self.addCleanup(page.deleteLater)
        page.show()
        self.app.processEvents()

        state_control = page._rizum_state_control
        state_control.setCurrentIndex(state_control.findData("blocked"))
        self.app.processEvents()
        self.assertEqual(page._rizum_panel.state(), "blocked")
        self.assertEqual(page._rizum_panel_v2.state(), "blocked")

        width_control = page._rizum_width_control
        width_control.setCurrentIndex(width_control.findData("narrow"))
        self.app.processEvents()
        self.assertEqual(page._rizum_panel.width(), 250)
        self.assertEqual(page._rizum_panel_v2.width(), 250)

        page._rizum_panel_v2.setState("active")
        self.app.processEvents()
        self.assertEqual(page._rizum_panel.state(), "active")
        self.assertEqual(state_control.currentData(), "active")

    def test_five_workflow_states_own_the_primary_and_apply_actions(self):
        panel = self.make_panel()
        expectations = {
            "empty": ("Create Target", False, "neutral"),
            "ready": ("Start Liquify", True, "good"),
            "active": ("Return to Painting", True, "accent"),
            "repair": ("Repair and Start", False, "warn"),
            "blocked": ("Start Liquify", False, "warn"),
        }
        for state, (primary, can_apply, tone) in expectations.items():
            panel.setState(state)
            self.app.processEvents()
            self.assertEqual(panel.primary_button.text(), primary)
            self.assertEqual(panel.apply_button.isEnabled(), can_apply)
            self.assertEqual(panel.status_banner.tone(), tone)
            self.assertTrue(panel.new_target_button.isVisible())

    def test_apply_uses_transient_confirmation_instead_of_applied_state(self):
        panel = self.make_panel("ready")

        panel._apply()
        QtTest.QTest.qWait(260)
        self.app.processEvents()

        self.assertEqual(panel.state(), "empty")
        self.assertTrue(panel._apply_confirmation.isVisible())
        self.assertEqual(
            panel._apply_confirmation.title(),
            "Applied to 3 layers",
        )

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


class LiquifyPreviewPanelV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    def setUp(self):
        self.app.setProperty("rizumUiFontScale", 1.0)
        self.app.setProperty("rizumPreviewLanguage", "en")

    def make_panel(self, state="ready", width_mode="standard"):
        panel = LiquifyPreviewPanelV2(state, width_mode)
        self.addCleanup(panel.deleteLater)
        panel.show()
        self.app.processEvents()
        return panel

    def test_ready_state_uses_the_same_status_hierarchy_as_other_states(self):
        panel = self.make_panel("ready")

        self.assertTrue(panel.status_banner.isVisible())
        self.assertEqual(panel.status_banner.title(), "Ready")
        self.assertEqual(panel.status_banner.subtitle(), "3 layers")
        self.assertNotIn("Folder", panel.status_banner.title())
        self.assertNotIn("Character", panel.status_banner.title())
        self.assertEqual(panel.status_banner.tone(), "good")
        self.assertEqual(panel.primary_button.text(), "Start Liquify")
        self.assertTrue(panel.apply_button.isEnabled())
        self.assertEqual(
            panel._target_layout.count(),
            3,
            "target row should hold combo + create + menu only",
        )

    def test_five_states_drive_banner_visibility_primary_and_apply(self):
        panel = self.make_panel()
        expectations = {
            "empty": ("Create Target", False, True, "neutral", ""),
            "ready": ("Start Liquify", True, True, "good", ""),
            "active": ("Back to Paint", True, True, "accent", ""),
            "repair": ("Repair & Start", False, True, "warn", ""),
            "blocked": ("Start Liquify", False, True, "warn", "View"),
        }
        for state, (primary, can_apply, banner_on, tone, action) in expectations.items():
            panel.setState(state)
            self.app.processEvents()
            self.assertEqual(panel.primary_button.text(), primary, state)
            self.assertEqual(panel.apply_button.isEnabled(), can_apply, state)
            self.assertEqual(panel.status_banner.isVisible(), banner_on, state)
            if banner_on:
                self.assertEqual(panel.status_banner.tone(), tone, state)
                self.assertEqual(panel.status_banner.actionText(), action, state)

    def test_apply_uses_transient_confirmation_instead_of_applied_state(self):
        panel = self.make_panel("ready")

        panel._apply()
        QtTest.QTest.qWait(260)
        self.app.processEvents()

        self.assertEqual(panel.state(), "empty")
        self.assertTrue(panel._apply_confirmation.isVisible())
        self.assertEqual(
            panel._apply_confirmation.title(),
            "Applied to 3 layers",
        )

    def test_ready_state_matches_codex_status_rhythm(self):
        v2 = self.make_panel("ready")
        codex = LiquifyPreviewPanel("ready")
        self.addCleanup(codex.deleteLater)
        codex.show()
        self.app.processEvents()
        self.assertEqual(v2.status_banner.height(), codex.status_banner.height())
        self.assertEqual(v2.height(), codex.height())

    def test_target_menu_hosts_maintenance_and_clear_flow(self):
        panel = self.make_panel("ready")
        texts = [
            action.text()
            for action in panel._menu.actions()
            if not action.isSeparator()
        ]
        for expected in (
            "Refresh Targets",
            "Repair Target",
            "Add Selected Layers",
            "Remove Selected Layers",
            "Clear Flow",
            "Delete Target",
            "Copy Diagnostics",
        ):
            self.assertIn(expected, texts)
        self.assertEqual(
            sum(action.isSeparator() for action in panel._menu.actions()),
            3,
        )
        self.assertEqual(
            [
                None if action.isSeparator() else action.text()
                for action in panel._menu.actions()
            ],
            [
                "Refresh Targets",
                "Repair Target",
                "Delete Target",
                None,
                "Add Selected Layers",
                "Remove Selected Layers",
                None,
                "Clear Flow",
                None,
                "Copy Diagnostics",
            ],
        )
        menu_style = panel._menu.styleSheet()
        self.assertIn("QMenu#RizumPopupMenu::separator", menu_style)
        self.assertIn("QMenu#RizumPopupMenu::icon", menu_style)
        self.assertIn("position: relative", menu_style)
        self.assertIn("left: 6px", menu_style)
        for action in (
            panel._refresh_action,
            panel._repair_action,
            panel._clear_action,
            panel._delete_action,
        ):
            self.assertFalse(action.icon().isNull())

        # Default combo target is a folder: membership actions stay disabled.
        panel._sync_menu_actions()
        self.assertTrue(panel._repair_action.isEnabled())
        self.assertTrue(panel._clear_action.isEnabled())
        self.assertFalse(panel._add_action.isEnabled())
        self.assertFalse(panel._remove_action.isEnabled())
        self.assertFalse(panel._delete_action.isEnabled())

        panel.target_combo.setCurrentIndex(panel.target_combo.findData("set"))
        panel._sync_menu_actions()
        self.assertTrue(panel._add_action.isEnabled())
        self.assertTrue(panel._remove_action.isEnabled())
        self.assertTrue(panel._delete_action.isEnabled())

        panel.setState("empty")
        self.assertFalse(panel._repair_action.isEnabled())
        self.assertFalse(panel._clear_action.isEnabled())

    def test_clear_flow_flashes_confirmation_then_restores(self):
        panel = self.make_panel("active")

        panel._clear_action.trigger()
        self.app.processEvents()
        self.assertTrue(panel.status_banner.isVisible())
        self.assertEqual(panel.status_banner.title(), "Flow cleared")
        self.assertEqual(panel.status_banner.tone(), "good")

        QtTest.QTest.qWait(1000)
        self.app.processEvents()
        self.assertEqual(panel.state(), "active")
        self.assertEqual(panel.status_banner.title(), "Liquify active")

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

    def test_compact_metrics_scale_from_one_baseline(self):
        panel = self.make_panel("blocked", "narrow")

        self.assertIsInstance(panel.status_banner, StatusBanner)
        self.assertIsInstance(panel.primary_button, SecondaryActionButton)
        self.assertIsInstance(panel.apply_button, AnimatedSaveButton)
        self.assertEqual(panel.width(), 250)
        self.assertEqual(panel.target_combo.height(), 32)
        self.assertEqual(panel.status_banner.height(), 54)
        self.assertEqual(panel._footer.height(), 48)
        self.assertEqual(panel.new_target_button.size(), QtCore.QSize(22, 22))
        self.assertEqual(panel.more_button.size(), QtCore.QSize(22, 22))

        self.app.setProperty("rizumUiFontScale", 1.5)
        panel.refreshMetrics()
        self.app.processEvents()
        self.assertEqual(panel.width(), 375)
        self.assertEqual(panel.target_combo.height(), 48)
        self.assertEqual(panel.status_banner.height(), 81)
        self.assertEqual(panel._footer.height(), 72)
        self.assertEqual(panel.new_target_button.size(), QtCore.QSize(33, 33))

    def test_all_preview_languages_build_at_narrow_width(self):
        for language in ("en", "de", "es", "fr", "it", "ja_JP", "ko", "pt", "zh_CN"):
            self.app.setProperty("rizumPreviewLanguage", language)
            for state in LiquifyPreviewPanelV2.STATES:
                panel = self.make_panel(state, "narrow")
                self.assertEqual(panel.width(), 250)
                self.assertLessEqual(
                    panel.primary_button.sizeHint().width(),
                    panel.width() - 24,
                    f"{language}/{state}",
                )


if __name__ == "__main__":
    unittest.main()
