"""Tests for the View Roll concept preview panel."""

from __future__ import annotations

import os
import subprocess
import sys
import textwrap
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6 import QtCore, QtGui, QtTest, QtWidgets

from rizum_ui import (
    FOOTER_BUTTON_PADDING_X,
    PAINTER_FOOTER_MARGIN_BOTTOM,
    SecondaryActionButton,
    ShortcutCaptureField,
    TextActionButton,
    make_segmented_control,
)

from view_roll_preview import (
    DESIGN_VARIANTS,
    SHORTCUT_ACTIONS,
    _VIEW_ROLL_TEXT,
    ViewRollComparisonPanel,
    ViewRollConceptPanel,
)

REPRESENTATIVE_SCALES = (0.75, 1.0, 1.1, 1.5, 2.0)
SUPPORTED_TRANSLATION_CODES = {
    "de",
    "es",
    "fr",
    "it",
    "ja_JP",
    "ko",
    "pt",
    "zh_CN",
}


class ViewRollTranslationTests(unittest.TestCase):
    def test_every_supported_language_has_the_complete_view_roll_catalog(self):
        self.assertEqual(set(_VIEW_ROLL_TEXT), SUPPORTED_TRANSLATION_CODES)
        expected_keys = set(_VIEW_ROLL_TEXT["zh_CN"])
        for language, catalog in _VIEW_ROLL_TEXT.items():
            with self.subTest(language=language):
                self.assertEqual(set(catalog), expected_keys)


class ShortcutCaptureFieldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    def test_compact_height_scales_and_floors_at_three_quarters(self):
        field = ShortcutCaptureField("Roll 3D Left")
        self.addCleanup(field.deleteLater)

        self.assertEqual(field.height(), 30)
        field.setCompactHeight(40)
        self.assertEqual(field.height(), 40)
        field.setCompactHeight(10)
        self.assertEqual(field.height(), 23)

    def test_clear_slot_only_exists_with_shortcut(self):
        field = ShortcutCaptureField("Roll 3D Left")
        self.addCleanup(field.deleteLater)

        self.assertTrue(field._clear_rect().isEmpty())
        field.setShortcut("Alt+Left", emit=False)
        self.assertFalse(field._clear_rect().isEmpty())
        field.setShortcut("", emit=False)
        self.assertTrue(field._clear_rect().isEmpty())

    def test_cancel_capture_restores_previous_shortcut(self):
        field = ShortcutCaptureField("Roll 3D Left")
        self.addCleanup(field.deleteLater)

        field.setShortcut("Alt+Left", emit=False)
        field.startCapture()
        self.assertTrue(field.isCapturing())
        field.cancelCapture()
        self.assertFalse(field.isCapturing())
        self.assertEqual(field.shortcut(), "Alt+Left")

    def test_capture_keeps_the_existing_field_width(self):
        field = ShortcutCaptureField("Roll 3D Left")
        self.addCleanup(field.deleteLater)
        field.setShortcut("Alt+Left", emit=False)
        resting_width = field.width()

        field.startCapture()

        self.assertEqual(field._display_text(), "Type shortcut…")
        self.assertEqual(field.width(), resting_width)
        field.cancelCapture()
        self.assertEqual(field.width(), resting_width)

    def test_conflict_feedback_stays_inside_the_field_without_resizing_it(self):
        field = ShortcutCaptureField("Roll 3D Left")
        self.addCleanup(field.deleteLater)
        field.setShortcut("Alt+Left", emit=False)
        resting_width = field.width()

        field.setConflicted(True)

        self.assertEqual(field.width(), resting_width)
        self.assertFalse(field._conflict_rect().isEmpty())
        self.assertEqual(field.accessibleDescription(), "Shortcut conflict")
        field.setConflicted(False)
        self.assertTrue(field._conflict_rect().isEmpty())
        self.assertEqual(field.accessibleDescription(), "")


class ViewRollConceptPanelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
        # Pin the host font scale so QSettings on the dev machine cannot leak in.
        cls.app.setProperty("rizumUiFontScale", 1.0)

    def setUp(self):
        self.app.setProperty("rizumPreviewLanguage", "en")

    def make_panel(self):
        panel = ViewRollConceptPanel()
        self.addCleanup(panel.deleteLater)
        return panel

    def test_defaults_are_not_dirty(self):
        panel = self.make_panel()

        self.assertFalse(panel.is_dirty())
        self.assertFalse(panel.save_button.isEnabled())

    def test_editing_marks_dirty_and_cancel_restores(self):
        panel = self.make_panel()

        panel.angle_stepper.setValue(90)
        self.assertTrue(panel.is_dirty())
        self.assertTrue(panel.save_button.isEnabled())
        panel.cancel_changes()
        self.assertFalse(panel.is_dirty())
        self.assertEqual(panel.angle_stepper.value(), 45)

    def test_save_then_restore_defaults_marks_dirty(self):
        panel = self.make_panel()

        panel.speed_stepper.setValue(120)
        panel.save_changes()
        self.assertFalse(panel.is_dirty())
        panel.restore_defaults()
        self.assertEqual(panel.speed_stepper.value(), 90)
        self.assertTrue(panel.is_dirty())

    def test_mode_reveals_follow_segment(self):
        panel = self.make_panel()

        panel.mode_segment.setCurrentData("continuous", animate=False, emit=False)
        panel._apply_mode_reveals(animate=False)
        self.assertEqual(panel.speed_reveal.progress(), 1.0)
        self.assertEqual(panel.angle_reveal.progress(), 0.0)

        panel.mode_segment.setCurrentData("custom", animate=False, emit=False)
        panel._apply_mode_reveals(animate=False)
        self.assertEqual(panel.speed_reveal.progress(), 0.0)
        self.assertEqual(panel.angle_reveal.progress(), 1.0)

    def test_codex_parameter_switch_is_atomic_without_graphics_effects(self):
        panel = ViewRollConceptPanel(design_variant="codex")
        self.addCleanup(panel.deleteLater)
        panel.show()
        QtWidgets.QApplication.processEvents()

        panel.parameter_slot.setMode("continuous", animate=False)
        stable_height = panel.dialog.height()
        panel.parameter_slot.setMode("custom", animate=True)
        QtWidgets.QApplication.processEvents()

        self.assertEqual(
            panel.parameter_slot.height(), panel.parameter_slot.expandedHeight()
        )
        self.assertEqual(panel.dialog.height(), stable_height)
        self.assertEqual(panel.speed_row.geometry(), panel.angle_row.geometry())
        self.assertEqual(panel.parameter_slot.rowOpacity("continuous"), 0.0)
        self.assertEqual(panel.parameter_slot.rowOpacity("custom"), 1.0)
        self.assertIs(panel.parameter_slot._layout.currentWidget(), panel.angle_row)
        self.assertFalse(panel.speed_row.isVisible())
        self.assertTrue(panel.angle_row.isVisible())
        self.assertIsNone(panel.speed_row.graphicsEffect())
        self.assertIsNone(panel.angle_row.graphicsEffect())

    def test_codex_parameter_is_visible_and_unclipped_on_first_expansion_frame(self):
        panel = ViewRollConceptPanel(design_variant="codex")
        self.addCleanup(panel.deleteLater)
        panel.show()
        QtWidgets.QApplication.processEvents()

        panel.parameter_slot.setMode("step_15", animate=False)
        panel.parameter_slot.setMode("continuous", animate=True)

        self.assertEqual(
            panel.parameter_slot.height(), panel.parameter_slot.expandedHeight()
        )
        self.assertTrue(
            panel.parameter_slot.rect().contains(panel.speed_row.geometry())
        )
        self.assertEqual(panel.parameter_slot.rowOpacity("continuous"), 1.0)
        QtWidgets.QApplication.processEvents()
        image = panel.parameter_slot.grab().toImage()
        background = image.pixelColor(0, 0)
        painted_pixels = sum(
            sum(
                abs(channel - background_channel)
                for channel, background_channel in zip(
                    image.pixelColor(x, y).getRgb()[:3],
                    background.getRgb()[:3],
                )
            )
            > 18
            for y in range(image.height())
            for x in range(image.width())
        )
        self.assertGreater(painted_pixels, 100)

    def test_codex_mode_slot_keeps_one_gap_when_collapsed_or_expanded(self):
        panel = ViewRollConceptPanel(design_variant="codex")
        self.addCleanup(panel.deleteLater)
        panel.show()
        QtWidgets.QApplication.processEvents()
        mode_row = panel.mode_label.parentWidget()
        spacing = panel._body_layout.spacing()
        collapsed_height = panel.dialog.height()

        self.assertEqual(
            panel._section_shortcuts.y() - (mode_row.y() + mode_row.height()),
            spacing,
        )

        panel.parameter_slot.setMode("continuous", animate=False)
        QtWidgets.QApplication.processEvents()

        self.assertEqual(
            panel.parameter_slot.y() - (mode_row.y() + mode_row.height()),
            spacing,
        )
        self.assertEqual(
            panel._section_shortcuts.y()
            - (panel.parameter_slot.y() + panel.parameter_slot.height()),
            spacing,
        )
        self.assertEqual(
            panel.dialog.height() - collapsed_height,
            panel.parameter_slot.expandedHeight() + spacing,
        )

    def test_codex_mode_caps_are_symmetric_at_the_host_dpi(self):
        probe = textwrap.dedent(
            """
            from pathlib import Path

            from PySide6 import QtCore, QtGui, QtWidgets

            import preview
            from rizum_ui import (
                apply_painter_like_base,
                build_painter_host_preview_stylesheet,
                build_stylesheet,
            )
            from view_roll_preview import ViewRollConceptPanel

            app = QtWidgets.QApplication([])
            font_root = Path.cwd().parent / "rizum-pt-ui-font" / "fonts"
            for filename in ("MiSans-Regular.ttf", "MiSans-Medium.ttf"):
                QtGui.QFontDatabase.addApplicationFont(str(font_root / filename))
            app.setFont(QtGui.QFont("MiSans"))
            apply_painter_like_base(app)
            app.setStyleSheet(
                build_painter_host_preview_stylesheet()
                + build_stylesheet(mode="full")
                + preview.PREVIEW_CANVAS_STYLESHEET
            )
            app.setProperty("rizumUiFontScale", 1.0)
            renders = []
            controls_fit = True
            for mode in ("continuous", "custom"):
                panel = ViewRollConceptPanel(design_variant="codex")
                panel.show()
                app.processEvents()
                control = panel.mode_segment
                control.setCurrentData(mode, animate=False, emit=False)
                app.processEvents()
                controls_fit = controls_fit and control.parentWidget().contentsRect().contains(
                    control.geometry()
                )
                image = panel.grab().toImage()
                origin = control.mapTo(panel, QtCore.QPoint(0, 0))
                dpr = image.devicePixelRatio()
                left = int(origin.x() * dpr + 0.5)
                top = int(origin.y() * dpr + 0.5)
                right = int((origin.x() + control.width()) * dpr + 0.5)
                bottom = int((origin.y() + control.height()) * dpr + 0.5)
                renders.append((image, left, top, right, bottom))

            left_render, right_render = renders
            left_image, left, left_top, _left_right, left_bottom = left_render
            right_image, _right_left, right_top, right, right_bottom = right_render
            max_delta = 0
            for x in range(4):
                for y in range(min(left_bottom - left_top, right_bottom - right_top)):
                    left_color = left_image.pixelColor(left + x, left_top + y)
                    right_color = right_image.pixelColor(
                        right - 1 - x, right_top + y
                    )
                    max_delta = max(
                        max_delta,
                        abs(left_color.red() - right_color.red()),
                        abs(left_color.green() - right_color.green()),
                        abs(left_color.blue() - right_color.blue()),
                        abs(left_color.alpha() - right_color.alpha()),
                    )
            print(int(controls_fit), max_delta)
            """
        )
        environment = os.environ.copy()
        environment.update(
            {
                "QT_QPA_PLATFORM": "offscreen",
                "QT_SCALE_FACTOR": "1.125",
                "QT_FONT_DPI": "96",
            }
        )
        result = subprocess.run(
            [sys.executable, "-c", probe],
            cwd=os.path.dirname(os.path.dirname(__file__)),
            env=environment,
            check=True,
            capture_output=True,
            text=True,
        )

        controls_fit, max_delta = (int(value) for value in result.stdout.split())
        self.assertEqual(controls_fit, 1)
        self.assertLessEqual(max_delta, 8)

    def test_duplicate_shortcuts_flag_conflict(self):
        panel = self.make_panel()
        footer_height = panel._footer.height()

        panel.shortcut_fields["roll_right"].setShortcut("Alt+Left")
        self.assertTrue(panel.shortcut_fields["roll_left"]._conflicted)
        self.assertTrue(panel.shortcut_fields["roll_right"]._conflicted)
        self.assertFalse(panel.shortcut_fields["roll_reset"]._conflicted)
        self.assertFalse(
            panel.shortcut_fields["roll_left"]._conflict_rect().isEmpty()
        )
        self.assertEqual(panel._footer.height(), footer_height)

        panel.shortcut_fields["roll_right"].setShortcut("Alt+Right")
        self.assertFalse(panel.shortcut_fields["roll_left"]._conflicted)
        self.assertFalse(panel.shortcut_fields["roll_right"]._conflicted)

    def test_footer_has_no_persistent_status_slot(self):
        panel = self.make_panel()

        self.assertFalse(hasattr(panel, "status_reveal"))
        self.assertEqual(
            panel._footer.findChildren(
                QtWidgets.QLabel, "RizumSettingsFooterHint"
            ),
            [],
        )

    def test_save_button_carries_dirty_state_without_a_footer_message(self):
        panel = self.make_panel()

        panel.angle_stepper.setValue(90)
        self.assertTrue(panel.save_button.isEnabled())

        panel.save_changes()
        self.assertFalse(panel.save_button.isEnabled())

        panel.speed_stepper.setValue(120)
        self.assertTrue(panel.save_button.isEnabled())
        panel.cancel_changes()
        self.assertFalse(panel.save_button.isEnabled())

    def test_codex_save_button_animates_dirty_and_saved_feedback_in_place(self):
        panel = ViewRollConceptPanel(design_variant="codex")
        self.addCleanup(panel.deleteLater)
        panel.show()
        QtWidgets.QApplication.processEvents()
        button = panel.save_button
        resting_size = button.size()
        self.assertFalse(button.isEnabled())
        self.assertEqual(button.activationProgress(), 0.0)

        panel.angle_stepper.setValue(90)
        self.assertTrue(button.isEnabled())
        self.assertEqual(button.activationDuration(), 140)
        QtTest.QTest.qWait(160)
        self.assertAlmostEqual(button.activationProgress(), 1.0, places=2)
        self.assertEqual(button.size(), resting_size)

        panel.save_changes()
        self.assertFalse(button.isEnabled())
        self.assertTrue(button.feedbackActive())
        self.assertEqual(button.feedbackDuration(), 500)
        QtTest.QTest.qWait(130)
        self.assertGreater(button.checkProgress(), 0.8)
        self.assertEqual(button.size(), resting_size)

        QtTest.QTest.qWait(420)
        self.assertFalse(button.feedbackActive())
        self.assertEqual(button.checkProgress(), 0.0)
        self.assertEqual(button.activationProgress(), 0.0)
        self.assertEqual(button.text(), "Save")
        self.assertEqual(button.size(), resting_size)

    def test_capture_prompt_stays_inside_the_field(self):
        panel = self.make_panel()
        field = panel.shortcut_fields["roll_left"]
        footer_height = panel._footer.height()

        field.startCapture()

        self.assertEqual(field._display_text(), "Type shortcut…")
        self.assertEqual(panel._footer.height(), footer_height)
        field.cancelCapture()
        self.assertEqual(field._display_text(), "Alt+Left")
        self.assertEqual(panel._footer.height(), footer_height)

    def test_save_failure_uses_a_transient_overlay_without_committing(self):
        def fail_save(_state):
            raise OSError("Read-only settings store")

        panel = ViewRollConceptPanel(save_handler=fail_save)
        self.addCleanup(panel.deleteLater)
        panel.show()
        QtWidgets.QApplication.processEvents()
        stable_size = panel.dialog.size()
        panel.angle_stepper.setValue(90)

        self.assertFalse(panel.save_changes())

        self.assertTrue(panel.is_dirty())
        self.assertTrue(panel.save_button.isEnabled())
        self.assertTrue(panel.error_notice.isVisible())
        self.assertEqual(panel.error_notice.message(), "Could not save changes.")
        self.assertIsNot(panel.error_notice.parentWidget(), panel._footer)
        self.assertEqual(panel.dialog.size(), stable_size)

    def test_ui_scale_scales_rows_and_shortcut_fields(self):
        panel = self.make_panel()

        self.assertEqual(panel.shortcut_fields["roll_left"].height(), 30)
        self.assertEqual(panel.error_notice.height(), 32)
        panel.dialog.setSettingsUiScale(1.5)
        self.assertEqual(panel.shortcut_fields["roll_left"].height(), 45)
        self.assertEqual(panel.mode_segment.height(), 45)
        self.assertEqual(panel.error_notice.height(), 48)

        panel.dialog.setSettingsUiScale(0.5)  # bounded to the 0.75 floor
        self.assertEqual(panel.shortcut_fields["roll_left"].height(), 23)
        self.assertEqual(panel.mode_segment.height(), 23)
        self.assertEqual(panel.error_notice.height(), 24)

    def test_ui_scale_preserves_the_one_x_dialog_proportions(self):
        panel = self.make_panel()
        panel.show()
        QtWidgets.QApplication.processEvents()
        panel.dialog.setSettingsUiScale(1.0)
        base_size = panel.dialog.size()

        panel.dialog.setSettingsUiScale(1.1)
        QtWidgets.QApplication.processEvents()

        self.assertEqual(panel.dialog.width(), round(base_size.width() * 1.1))
        self.assertAlmostEqual(
            panel.dialog.height(),
            round(base_size.height() * 1.1),
            delta=1,
        )


class SegmentedControlHostStyleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    def test_host_qframe_fill_does_not_cover_the_antialiasing_inset(self):
        host = QtWidgets.QWidget()
        self.addCleanup(host.deleteLater)
        host.setObjectName("SegmentedControlTestHost")
        host.setStyleSheet(
            """
QWidget#SegmentedControlTestHost { background: #202123; }
QFrame { background: #1b1b1b; border: 1px solid transparent; border-radius: 8px; }
"""
        )
        layout = QtWidgets.QVBoxLayout(host)
        layout.setContentsMargins(4, 4, 4, 4)
        control = make_segmented_control(
            [("Continuous", "continuous"), ("15°", "step"), ("Custom", "custom")],
            current="step",
        )
        control.setPaintInset(1)
        layout.addWidget(control)
        host.show()
        QtWidgets.QApplication.processEvents()

        image = host.grab().toImage()
        origin = control.mapTo(host, QtCore.QPoint(0, 0))
        y = origin.y() + control.height() // 2
        edge = image.pixelColor(origin.x() + control.width() - 1, y)
        outside = image.pixelColor(origin.x() + control.width(), y)
        self.assertEqual(edge, outside)


class ViewRollComparisonPanelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
        cls.app.setProperty("rizumUiFontScale", 1.0)

    def test_comparison_contains_all_three_independent_directions(self):
        comparison = ViewRollComparisonPanel()
        self.addCleanup(comparison.deleteLater)

        self.assertEqual(list(comparison.panels), ["original", "codex", "kimi"])
        self.assertEqual(
            [panel.design_variant for panel in comparison.panels.values()],
            ["original", "codex", "kimi"],
        )
        self.assertEqual(len(set(map(id, comparison.panels.values()))), 3)

    def test_original_stays_default_while_alternatives_apply_their_tokens(self):
        original = ViewRollConceptPanel(design_variant="original")
        codex = ViewRollConceptPanel(design_variant="codex")
        kimi = ViewRollConceptPanel(design_variant="kimi")
        for panel in (original, codex, kimi):
            self.addCleanup(panel.deleteLater)

        self.assertIsNone(original.mode_segment._corner_radius)
        self.assertEqual(codex._visual_style["surface"], "#202020")
        self.assertEqual(codex.mode_segment._corner_radius, 8)
        self.assertEqual(codex.mode_segment._paint_inset, 1.5)
        self.assertIsNotNone(codex.parameter_slot)
        self.assertEqual(
            codex.parameter_slot._layout.stackingMode(),
            QtWidgets.QStackedLayout.StackingMode.StackOne,
        )
        self.assertEqual(original.speed_reveal._duration, 140)
        self.assertEqual(kimi.angle_reveal._duration, 140)
        codex._apply_mode_reveals(animate=False)
        body_margins = codex._body_layout.contentsMargins()
        self.assertEqual((body_margins.left(), body_margins.right()), (20, 20))
        mode_margins = codex.mode_segment.parentWidget().layout().contentsMargins()
        self.assertEqual((mode_margins.left(), mode_margins.right()), (0, 0))
        footer_margins = codex._button_layout.contentsMargins()
        self.assertEqual((footer_margins.left(), footer_margins.right()), (20, 20))
        self.assertEqual(codex.dialog.settingsFrameWidth(), 0)
        self.assertEqual(codex.dialog.settingsFrameBottomWidth(), 0)
        self.assertFalse(codex.dialog.settingsBottomEdgeExtensionEnabled())
        self.assertEqual(
            codex._section_rotation.height(), kimi._section_rotation.height()
        )
        self.assertEqual(codex._section_rotation.height(), 26)
        self.assertEqual(codex._button_row.height(), kimi._button_row.height())
        self.assertEqual(codex._button_row.height(), 32)
        self.assertEqual(codex._footer.layout().contentsMargins().top(), 14)
        self.assertEqual(codex._footer.layout().contentsMargins().bottom(), 16)
        self.assertEqual(codex._footer.layout().spacing(), 0)
        self.assertIsNotNone(codex._footer_separator)
        self.assertEqual(codex._footer_separator.height(), 1)
        self.assertEqual(
            len(
                codex._footer_separator.findChildren(
                    QtWidgets.QFrame, "RizumInsetSeparator"
                )
            ),
            1,
        )
        self.assertIsNone(original._footer_separator)
        self.assertIsNone(kimi._footer_separator)
        self.assertIsInstance(codex.restore_button, TextActionButton)
        self.assertIsInstance(codex.cancel_button, SecondaryActionButton)
        restore_left = codex.restore_button.mapTo(
            codex.dialog, QtCore.QPoint(0, 0)
        ).x()
        section_left = codex._section_rotation.mapTo(
            codex.dialog, QtCore.QPoint(0, 0)
        ).x()
        self.assertEqual(restore_left, section_left)
        self.assertEqual(
            codex.restore_button.width(), codex.restore_button.sizeHint().width()
        )
        for codex_button, kimi_button in (
            (codex.cancel_button, kimi.cancel_button),
            (codex.save_button, kimi.save_button),
        ):
            self.assertEqual(codex_button.height(), kimi_button.height())
            self.assertEqual(codex_button.height(), 28)
        footer_metrics = QtGui.QFontMetrics(codex._footer_button_font())
        for button in (
            codex.cancel_button,
            codex.save_button,
        ):
            expected = (
                footer_metrics.horizontalAdvance(button.text())
                + 2 * FOOTER_BUTTON_PADDING_X
                + 2
                + 14
            )
            self.assertGreaterEqual(button.width(), expected)
        self.assertIn(
            "QPushButton#RizumViewRollSave {\n"
            "    color: #202020;\n"
            "    background: #f2f2f2;\n"
            "    border-radius: 6px;",
            codex.dialog.settingsSurface().styleSheet(),
        )
        self.assertEqual(kimi.mode_segment._corner_radius, 4)
        self.assertEqual(kimi._visual_style["surface"], "#26282c")
        self.assertEqual(codex._visual_style["control"], "#333333")
        self.assertEqual(codex._visual_style["control_hover"], "#444444")
        self.assertEqual(codex._visual_style["control_pressed"], "#2c2c2c")
        for panel in (codex, kimi):
            stylesheet = panel.dialog.settingsSurface().styleSheet()
            self.assertIn(
                "QPushButton#RizumViewRollRestore {\n"
                "    color:",
                stylesheet,
            )
            self.assertIn("background: transparent;\n    border: 0;", stylesheet)
            self.assertIn(
                "QPushButton#RizumViewRollRestore:hover",
                stylesheet,
            )
        self.assertEqual(
            [DESIGN_VARIANTS[key]["label"] for key in ("original", "codex", "kimi")],
            ["Original", "Codex", "Kimi K3"],
        )


class ViewRollLayoutRegressionTests(unittest.TestCase):
    """Geometry guards for the 0.75x-2.0x UI scale range.

    Reproduces the defects seen in the launched 1.10x preview: feedback
    changing footer geometry, clipped Restore/Cancel buttons, and a truncated
    shortcut capture placeholder.
    """

    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
        # Pin the host font scale so QSettings on the dev machine cannot leak in.
        cls.app.setProperty("rizumUiFontScale", 1.0)

    def make_panel(self, scale):
        panel = ViewRollConceptPanel()
        self.addCleanup(panel.deleteLater)
        # showEvent re-syncs the scale from the pinned 1.0, so set the target
        # scale only after the panel is shown and laid out once.
        panel.show()
        panel.dialog.setSettingsUiScale(scale)
        QtWidgets.QApplication.processEvents()
        return panel

    def rect_in_dialog(self, panel, widget):
        top_left = widget.mapTo(panel.dialog, QtCore.QPoint(0, 0))
        return QtCore.QRect(top_left, widget.size())

    def test_footer_buttons_fit_without_overlap_or_clipping(self):
        for scale in REPRESENTATIVE_SCALES:
            with self.subTest(scale=scale):
                panel = self.make_panel(scale)
                dialog_width = panel.dialog.width()
                metrics = QtGui.QFontMetrics(panel._footer_button_font())

                buttons = (
                    panel.restore_button,
                    panel.cancel_button,
                    panel.save_button,
                )
                rects = [self.rect_in_dialog(panel, button) for button in buttons]
                for button, rect in zip(buttons, rects):
                    self.assertGreaterEqual(rect.left(), 0)
                    self.assertLessEqual(rect.right(), dialog_width - 1)
                    text_width = metrics.horizontalAdvance(button.text())
                    content_width = button.width() - (
                        2 * FOOTER_BUTTON_PADDING_X + 2
                    )
                    self.assertLessEqual(
                        text_width,
                        content_width,
                        f"{button.text()!r} clips at {scale}x",
                    )
                for index, rect in enumerate(rects):
                    for other in rects[index + 1 :]:
                        self.assertFalse(rect.intersects(other))

    def test_initial_show_preserves_view_roll_surface_rules(self):
        panel = ViewRollConceptPanel()
        self.addCleanup(panel.deleteLater)
        concept_rule = "QWidget#RizumViewRollBody"
        self.assertIn(concept_rule, panel.dialog.settingsSurface().styleSheet())

        panel.show()
        QtWidgets.QApplication.processEvents()

        self.assertIn(concept_rule, panel.dialog.settingsSurface().styleSheet())

    def test_noninteractive_rows_have_no_hover_surface(self):
        panel = self.make_panel(1.0)

        self.assertNotIn(
            "QFrame#RizumViewRollRow:hover",
            panel.dialog.settingsSurface().styleSheet(),
        )

    def test_footer_separates_restore_from_commit_actions(self):
        panel = self.make_panel(1.1)
        margins = panel._button_layout.contentsMargins()
        spacing = panel._button_layout.spacing()
        restore = self.rect_in_dialog(panel, panel.restore_button)
        cancel = self.rect_in_dialog(panel, panel.cancel_button)
        save = self.rect_in_dialog(panel, panel.save_button)
        row = self.rect_in_dialog(panel, panel._button_row)

        self.assertEqual(restore.left(), row.left() + margins.left())
        self.assertEqual(save.right(), row.right() - margins.right())
        self.assertEqual(save.left() - cancel.right() - 1, spacing)
        self.assertGreater(cancel.left() - restore.right() - 1, spacing)

    def test_restore_button_width_tracks_its_label(self):
        panel = self.make_panel(1.1)
        text_width = QtGui.QFontMetrics(
            panel._footer_button_font()
        ).horizontalAdvance(panel.restore_button.text())
        chrome_width = 2 * FOOTER_BUTTON_PADDING_X + 2

        self.assertLessEqual(
            panel.restore_button.width() - text_width - chrome_width,
            panel._metric(6, 5),
        )

    def test_shortcut_feedback_never_changes_footer_geometry(self):
        for scale in REPRESENTATIVE_SCALES:
            with self.subTest(scale=scale):
                panel = self.make_panel(scale)
                stable_footer_height = panel._footer.height()
                stable_dialog_height = panel.dialog.height()

                field = panel.shortcut_fields["roll_left"]
                field.startCapture()
                self.assertEqual(field._display_text(), "Type shortcut…")
                self.assertEqual(panel._footer.height(), stable_footer_height)
                self.assertEqual(panel.dialog.height(), stable_dialog_height)
                field.cancelCapture()

                panel.shortcut_fields["roll_right"].setShortcut("Alt+Left")
                QtWidgets.QApplication.processEvents()
                self.assertFalse(field._conflict_rect().isEmpty())
                self.assertEqual(panel._footer.height(), stable_footer_height)
                self.assertEqual(panel.dialog.height(), stable_dialog_height)

    def test_shortcut_fields_fit_placeholder_at_every_scale(self):
        for scale in REPRESENTATIVE_SCALES:
            with self.subTest(scale=scale):
                panel = self.make_panel(scale)
                for _action_id, action_name in SHORTCUT_ACTIONS:
                    field = panel.shortcut_fields[_action_id]
                    self.assertEqual(field.width(), field.sizeHint().width())
                    metrics = QtGui.QFontMetrics(field._font())
                    for text in ("Type shortcut…", field.shortcut()):
                        available = (
                            field.width()
                            - field._scaled(10)
                            - field._clear_slot_width()
                            - field._scaled(8)
                        )
                        self.assertLessEqual(
                            metrics.horizontalAdvance(text),
                            available,
                            f"{action_name} truncates {text!r} at {scale}x",
                        )
                    rect = self.rect_in_dialog(panel, field)
                    self.assertLessEqual(rect.right(), panel.dialog.width() - 1)

    def test_shortcut_names_remain_visible_without_overlapping_fields(self):
        for scale in REPRESENTATIVE_SCALES:
            with self.subTest(scale=scale):
                panel = self.make_panel(scale)
                for action_id, _action_name in SHORTCUT_ACTIONS:
                    field = panel.shortcut_fields[action_id]
                    label = field._rizum_name_label
                    label_rect = self.rect_in_dialog(panel, label)
                    field_rect = self.rect_in_dialog(panel, field)
                    self.assertGreater(label.width(), 0)
                    self.assertGreaterEqual(label_rect.left(), 0)
                    self.assertFalse(label_rect.intersects(field_rect))

    def test_dialog_width_stays_compact(self):
        for scale in REPRESENTATIVE_SCALES:
            with self.subTest(scale=scale):
                panel = self.make_panel(scale)
                base = panel.dialog.settingsMetric(300, 240)
                # Exact fit: the width is the compact baseline, grown only by
                # what the measured content genuinely demands — never more.
                self.assertEqual(panel.dialog.width(), panel._required_dialog_width())
                self.assertGreaterEqual(panel.dialog.width(), base)
                # Runaway-growth cap. The offscreen test font engine measures
                # glyphs ~1.8x wider than production fonts, so an absolute
                # pixel bound cannot be tight; 1.5x the baseline still catches
                # double-scaling bugs at the non-1.0 scales.
                self.assertLessEqual(panel.dialog.width(), base + base // 2)

    def test_name_labels_render_full_text_at_every_scale(self):
        """"Speed" clipped to "Speec" when widths were guessed per character."""
        for scale in REPRESENTATIVE_SCALES:
            with self.subTest(scale=scale):
                panel = self.make_panel(scale)
                for label in panel._name_labels:
                    metrics = QtGui.QFontMetrics(label.font())
                    self.assertLessEqual(
                        metrics.horizontalAdvance(label.text()),
                        label.width(),
                        f"{label.text()!r} clips at {scale}x",
                    )
                for block in panel._texts_blocks:
                    meta = block._rizum_meta_label
                    metrics = QtGui.QFontMetrics(meta.font())
                    self.assertLessEqual(
                        metrics.horizontalAdvance(meta.text()),
                        meta.width(),
                        f"{meta.text()!r} clips at {scale}x",
                    )

    def test_tall_row_text_block_centers_against_stepper(self):
        """The name+meta stack sits as one tight unit beside the stepper."""
        for scale in REPRESENTATIVE_SCALES:
            with self.subTest(scale=scale):
                panel = self.make_panel(scale)
                for texts, stepper in (
                    (panel.speed_texts, panel.speed_stepper),
                    (panel.angle_texts, panel.angle_stepper),
                ):
                    row = stepper.parentWidget()
                    name = texts._rizum_name_label
                    meta = texts._rizum_meta_label
                    # Tight stack: exactly name + spacing + meta, no stretch.
                    self.assertEqual(
                        texts.height(),
                        name.height() + texts.layout().spacing() + meta.height(),
                    )
                    self.assertLessEqual(
                        texts.layout().spacing(), panel._metric(2, 1)
                    )
                    block_center = texts.mapTo(
                        row, QtCore.QPoint(0, texts.height() // 2)
                    ).y()
                    stepper_center = stepper.mapTo(
                        row, QtCore.QPoint(0, stepper.height() // 2)
                    ).y()
                    self.assertLessEqual(abs(block_center - stepper_center), 1)
                    # The block stays inside the row's content box.
                    margins = row.layout().contentsMargins()
                    block_top = texts.mapTo(row, QtCore.QPoint(0, 0)).y()
                    self.assertGreaterEqual(block_top, margins.top())
                    self.assertLessEqual(
                        block_top + texts.height(),
                        row.height() - margins.bottom(),
                    )

    def test_footer_rhythm_keeps_vertical_breathing_room(self):
        """The actions-only footer keeps a fixed visual rhythm."""
        for scale in REPRESENTATIVE_SCALES:
            with self.subTest(scale=scale):
                panel = self.make_panel(scale)
                gap = panel._metric(8, 6)

                footer = self.rect_in_dialog(panel, panel._footer)
                buttons = self.rect_in_dialog(panel, panel._button_row)
                self.assertEqual(
                    buttons.top() - footer.top(), panel._metric(6, 5) + gap
                )
                self.assertEqual(
                    footer.bottom() - buttons.bottom(),
                    panel._metric(PAINTER_FOOTER_MARGIN_BOTTOM, 11),
                )
                collapsed_footer_height = panel._footer.height()
                collapsed_dialog_height = panel.dialog.height()

                panel.shortcut_fields["roll_left"].startCapture()
                panel.shortcut_fields["roll_right"].setShortcut("Alt+Left")
                QtWidgets.QApplication.processEvents()
                self.assertEqual(
                    panel._footer.height(), collapsed_footer_height
                )
                self.assertEqual(
                    panel.dialog.height(), collapsed_dialog_height
                )
                margins = panel._button_layout.contentsMargins()
                self.assertEqual(margins.left(), panel._metric(16, 12))
                self.assertEqual(margins.right(), panel._metric(16, 12))

                separators = panel._footer.findChildren(
                    QtWidgets.QFrame, "RizumInsetSeparator"
                )
                self.assertEqual(separators, [])

    def test_segmented_control_paints_fills_without_edge_stroke(self):
        """Focus raises the track fill; no 1px outline is ever drawn."""
        panel = self.make_panel(1.0)
        control = panel.mode_segment

        def grab_focused(focused):
            if focused:
                control.hasFocus = lambda: True
            else:
                # The offscreen window can hand this control real focus;
                # drop it so the "plain" grab is deterministic.
                control.clearFocus()
            try:
                return control.grab().toImage()
            finally:
                if focused:
                    del control.hasFocus

        plain = grab_focused(False)
        focused = grab_focused(True)
        width, height = plain.width(), plain.height()

        # The old focus ring lived on the outermost edge pixels; the fill
        # design leaves them untouched whether focused or not. Tolerance 4
        # covers antialiasing of the lifted track; the old 1px ring shifted
        # these pixels by ~25.
        for point in (
            (width // 2, 0),
            (width // 2, height - 1),
            (0, height // 2),
            (width - 1, height // 2),
        ):
            before = plain.pixelColor(*point)
            after = focused.pixelColor(*point)
            self.assertLessEqual(
                abs(before.value() - after.value()),
                4,
                f"edge stroke appears at {point}",
            )

        # Track still lifts on focus, sampled inside an unselected segment
        # away from its text.
        rects = control._segment_rects()
        idle_index = (control.currentIndex() + 1) % control.count()
        idle_rect = rects[idle_index]
        track_point = (
            int(idle_rect.left()) + 2,
            int(idle_rect.center().y()) - int(idle_rect.height() // 4),
        )
        before = plain.pixelColor(*track_point)
        after = focused.pixelColor(*track_point)
        self.assertGreater(after.value(), before.value())

        # The selected segment keeps its accent fill.
        current = rects[control.currentIndex()]
        selected = plain.pixelColor(
            int(current.center().x()), int(current.top()) + 1
        )
        self.assertGreater(selected.value(), 200)

        # Hover keeps its light overlay on the segment under the pointer.
        control._hovered_index = idle_index
        control.update()
        hovered = grab_focused(False)
        self.assertGreater(
            hovered.pixelColor(*track_point).value(),
            plain.pixelColor(*track_point).value(),
        )


if __name__ == "__main__":
    unittest.main()
