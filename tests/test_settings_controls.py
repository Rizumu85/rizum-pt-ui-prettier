from __future__ import annotations

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6 import QtCore, QtGui, QtTest, QtWidgets

from rizum_ui import (
    AnimatedSaveButton,
    ModeParameterSlot,
    SecondaryActionButton,
    SettingsToggle,
    ShortcutCaptureField,
    TextActionButton,
)


class SettingsControlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    def test_text_action_scales_from_its_compact_height(self):
        button = TextActionButton("Restore")
        self.addCleanup(button.deleteLater)

        button.setCompactHeight(35)

        self.assertEqual(button.height(), 35)
        self.assertGreater(button.width(), 40)

    def test_save_button_exposes_clean_dirty_and_feedback_states(self):
        button = AnimatedSaveButton("Save")
        self.addCleanup(button.deleteLater)
        self.assertFalse(button.isEnabled())

        button.setDirty(True, animate=False)
        self.assertTrue(button.isEnabled())
        self.assertTrue(button.isDirty())

        button.showSavedFeedback()
        self.assertFalse(button.isEnabled())
        self.assertTrue(button.feedbackActive())

    def test_secondary_action_measures_from_its_painted_font(self):
        button = SecondaryActionButton("Cancel")
        self.addCleanup(button.deleteLater)

        button.setCompactHeight(28)

        self.assertEqual(button.height(), 28)
        self.assertGreater(button.sizeHint().width(), 45)
        self.assertLessEqual(button.sizeHint().width(), 90)

    def test_secondary_action_fades_new_text_without_delaying_state(self):
        button = SecondaryActionButton("Start Liquify")
        self.addCleanup(button.deleteLater)
        button.show()
        self.app.processEvents()

        button.setAnimatedText("Back to Paint")

        self.assertEqual(button.text(), "Back to Paint")
        self.assertLess(button.contentOpacity(), 0.4)
        QtTest.QTest.qWait(button.TEXT_TRANSITION_DURATION + 30)
        self.assertGreater(button.contentOpacity(), 0.98)

    def test_secondary_action_animates_to_a_visible_neutral_hover_fill(self):
        button = SecondaryActionButton("Cancel")
        self.addCleanup(button.deleteLater)
        button.setFixedWidth(80)
        button.show()
        self.app.processEvents()

        self.assertEqual(button._background.name(), "#333333")
        self.assertEqual(button._hover_background.name(), "#444444")
        button.enterEvent(
            QtGui.QEnterEvent(
                QtCore.QPointF(4, 4),
                QtCore.QPointF(4, 4),
                QtCore.QPointF(4, 4),
            )
        )
        QtTest.QTest.qWait(button.HOVER_DURATION + 30)
        self.assertGreater(button.hoverProgress(), 0.98)
        hovered = button.grab().toImage().pixelColor(6, button.height() // 2)
        self.assertEqual(hovered.name(), "#444444")

        button.leaveEvent(QtCore.QEvent(QtCore.QEvent.Type.Leave))
        QtTest.QTest.qWait(button.HOVER_DURATION + 30)
        self.assertLess(button.hoverProgress(), 0.02)

    def test_settings_toggle_scales_and_tracks_its_state(self):
        toggle = SettingsToggle(checked=True)
        self.addCleanup(toggle.deleteLater)

        self.assertTrue(toggle.isChecked())
        self.assertEqual(toggle.size().toTuple(), (36, 20))

        toggle.setCompactHeight(30)
        self.assertEqual(toggle.size().toTuple(), (54, 30))

        toggle.click()
        self.assertFalse(toggle.isChecked())

    def test_active_save_animates_from_soft_white_to_white_on_hover(self):
        button = AnimatedSaveButton("Save")
        self.addCleanup(button.deleteLater)
        button.setDirty(True, animate=False)
        button.setFixedWidth(80)
        button.show()
        self.app.processEvents()

        button.setHoverProgress(0.0)
        normal = button.grab().toImage().pixelColor(6, button.height() // 2)
        button.setHoverProgress(1.0)
        hovered = button.grab().toImage().pixelColor(6, button.height() // 2)

        self.assertEqual(normal.name(), "#f2f2f2")
        self.assertEqual(hovered.name(), "#ffffff")

    def test_saved_checkmark_offsets_down_at_every_compact_height(self):
        button = AnimatedSaveButton("Save")
        self.addCleanup(button.deleteLater)

        for height in (21, 28, 35):
            with self.subTest(height=height):
                button.setCompactHeight(height)
                button.setFixedWidth(72)
                bounds = button._checkmark_polygon().boundingRect()
                button_center = QtCore.QRectF(button.rect()).center()
                scale = height / AnimatedSaveButton.BASE_HEIGHT

                self.assertAlmostEqual(
                    bounds.center().x(),
                    button_center.x(),
                    delta=0.01,
                )
                # Locks the deliberate +1.0 design px (scaled) downward drop:
                # a mathematically centered check reads optically high against
                # the Save label in live Painter (user report).
                self.assertAlmostEqual(
                    bounds.center().y(),
                    button_center.y() + 1.0 * scale,
                    delta=0.01,
                )

    def test_parameter_slot_switches_rows_atomically(self):
        speed = QtWidgets.QWidget()
        angle = QtWidgets.QWidget()
        slot = ModeParameterSlot({"continuous": speed, "custom": angle}, 46)
        self.addCleanup(slot.deleteLater)

        slot.setMode("continuous")
        self.assertEqual(slot.height(), 46)
        self.assertIs(slot._layout.currentWidget(), speed)

        slot.setMode("custom", animate=True)
        self.assertEqual(slot.height(), 46)
        self.assertIs(slot._layout.currentWidget(), angle)
        self.assertIsNone(speed.graphicsEffect())
        self.assertIsNone(angle.graphicsEffect())

        slot.setMode("step_15")
        self.assertEqual(slot.height(), 0)

    def test_collapsed_parameter_slot_keeps_one_layout_gap(self):
        host = QtWidgets.QWidget()
        self.addCleanup(host.deleteLater)
        layout = QtWidgets.QVBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        mode_row = QtWidgets.QWidget()
        mode_row.setFixedHeight(40)
        parameter_row = QtWidgets.QWidget()
        slot = ModeParameterSlot({"continuous": parameter_row}, 46)
        shortcuts_section = QtWidgets.QWidget()
        shortcuts_section.setFixedHeight(36)
        layout.addWidget(mode_row)
        layout.addWidget(slot)
        layout.addWidget(shortcuts_section)

        slot.setMode("step_15")

        self.assertTrue(slot.isHidden())
        self.assertEqual(host.sizeHint().height(), 40 + 2 + 36)

    def test_parameter_slot_stays_transparent_under_painter_qframe_style(self):
        host = QtWidgets.QWidget()
        self.addCleanup(host.deleteLater)
        host.setObjectName("ParameterSlotTestHost")
        host.setStyleSheet(
            """
QWidget#ParameterSlotTestHost { background: #202123; }
QFrame { background: #aa0000; border: 0; border-radius: 8px; }
"""
        )
        layout = QtWidgets.QVBoxLayout(host)
        layout.setContentsMargins(8, 8, 8, 8)
        row = QtWidgets.QWidget()
        row.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)
        slot = ModeParameterSlot({"continuous": row}, 46)
        slot.setMode("continuous")
        layout.addWidget(slot)
        host.show()
        self.app.processEvents()

        image = host.grab().toImage().convertToFormat(
            QtGui.QImage.Format.Format_ARGB32
        )
        origin = slot.mapTo(host, QtCore.QPoint(0, 0))
        self.assertEqual(
            image.pixelColor(origin).name(),
            "#202123",
            "the mode slot must not add a background behind Speed or Angle",
        )

    def test_shortcut_rounding_survives_painter_qframe_style(self):
        host = QtWidgets.QWidget()
        self.addCleanup(host.deleteLater)
        host.setStyleSheet(
            """
QWidget { background: #202123; }
QFrame { background: #aa0000; border: 0; border-radius: 0; }
"""
        )
        layout = QtWidgets.QVBoxLayout(host)
        layout.setContentsMargins(8, 8, 8, 8)
        field = ShortcutCaptureField(
            "Roll 3D Left",
            "Shift+Num+4",
            visual_style={"control": "#303236", "field_radius": 6},
        )
        field.setFixedWidth(150)
        layout.addWidget(field)
        host.show()
        self.app.processEvents()

        image = host.grab().toImage().convertToFormat(
            QtGui.QImage.Format.Format_ARGB32
        )
        origin = field.mapTo(host, QtCore.QPoint(0, 0))
        self.assertEqual(
            image.pixelColor(origin).name(),
            "#202123",
            "Painter's generic QFrame fill must not square off the field corner",
        )


if __name__ == "__main__":
    unittest.main()
