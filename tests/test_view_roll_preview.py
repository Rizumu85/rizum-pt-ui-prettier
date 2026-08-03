"""Tests for the View Roll concept preview panel."""

from __future__ import annotations

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6 import QtCore, QtGui, QtWidgets

from rizum_ui import FOOTER_BUTTON_PADDING_X

from view_roll_preview import (
    SHORTCUT_ACTIONS,
    ShortcutCaptureField,
    ViewRollConceptPanel,
)

REPRESENTATIVE_SCALES = (0.75, 1.0, 1.1, 1.5, 2.0)


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


class ViewRollConceptPanelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
        # Pin the host font scale so QSettings on the dev machine cannot leak in.
        cls.app.setProperty("rizumUiFontScale", 1.0)

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

    def test_duplicate_shortcuts_flag_conflict(self):
        panel = self.make_panel()

        panel.shortcut_fields["roll_right"].setShortcut("Alt+Left")
        self.assertTrue(panel.shortcut_fields["roll_left"]._conflicted)
        self.assertTrue(panel.shortcut_fields["roll_right"]._conflicted)
        self.assertFalse(panel.shortcut_fields["roll_reset"]._conflicted)

        panel.shortcut_fields["roll_right"].setShortcut("Alt+Right")
        self.assertFalse(panel.shortcut_fields["roll_left"]._conflicted)
        self.assertFalse(panel.shortcut_fields["roll_right"]._conflicted)

    def test_ui_scale_scales_rows_and_shortcut_fields(self):
        panel = self.make_panel()

        self.assertEqual(panel.shortcut_fields["roll_left"].height(), 30)
        panel.dialog.setSettingsUiScale(1.5)
        self.assertEqual(panel.shortcut_fields["roll_left"].height(), 45)
        self.assertEqual(panel.mode_segment.height(), 45)

        panel.dialog.setSettingsUiScale(0.5)  # bounded to the 0.75 floor
        self.assertEqual(panel.shortcut_fields["roll_left"].height(), 23)
        self.assertEqual(panel.mode_segment.height(), 23)


class ViewRollLayoutRegressionTests(unittest.TestCase):
    """Geometry guards for the 0.75x-2.0x UI scale range.

    Reproduces the defects seen in the launched 1.10x preview: status text
    overlapping the footer actions, clipped Restore/Cancel buttons, and a
    truncated shortcut capture placeholder.
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

    def test_status_line_never_overlaps_footer_buttons(self):
        for scale in REPRESENTATIVE_SCALES:
            with self.subTest(scale=scale):
                panel = self.make_panel(scale)
                # Longest status: a two-way shortcut conflict warning.
                panel.shortcut_fields["roll_right"].setShortcut("Alt+Left")
                QtWidgets.QApplication.processEvents()

                status_rect = self.rect_in_dialog(panel, panel.status_label)
                self.assertGreaterEqual(status_rect.left(), 0)
                self.assertLessEqual(status_rect.right(), panel.dialog.width() - 1)
                for button in (
                    panel.restore_button,
                    panel.cancel_button,
                    panel.save_button,
                ):
                    self.assertFalse(
                        status_rect.intersects(
                            self.rect_in_dialog(panel, button)
                        )
                    )
                # Whatever text is shown must fit the line it sits on.
                shown_width = QtGui.QFontMetrics(
                    panel._status_font()
                ).horizontalAdvance(panel.status_label.text())
                self.assertLessEqual(shown_width, panel.status_label.width() + 1)

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

    def test_dialog_width_stays_compact(self):
        for scale in REPRESENTATIVE_SCALES:
            with self.subTest(scale=scale):
                panel = self.make_panel(scale)
                base = panel.dialog.settingsMetric(300, 240)
                self.assertEqual(panel.dialog.width(), panel._required_dialog_width())
                # Content must fit the scaled compact baseline; the measured
                # fallback exists for wider fonts, not as an invitation to grow.
                self.assertGreaterEqual(panel.dialog.width(), base)
                self.assertLessEqual(panel.dialog.width(), base + 48)


if __name__ == "__main__":
    unittest.main()
