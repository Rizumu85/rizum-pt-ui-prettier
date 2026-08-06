from __future__ import annotations

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6 import QtCore, QtGui, QtWidgets

from rizum_ui import make_segmented_control


class SegmentedControlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    def make_control(self):
        return make_segmented_control(
            [
                ("Continuous", "continuous"),
                ("15°", "step_15"),
                ("Custom", "custom"),
            ],
            current="step_15",
        )

    def _render_control(self, scale, current, hovered=-1):
        host = QtWidgets.QWidget()
        self.addCleanup(host.deleteLater)
        host.setObjectName("SegmentedControlTestHost")
        host.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        host.setStyleSheet(
            """
QWidget#SegmentedControlTestHost { background: #202123; }
QFrame { background: #1b1b1b; border: 1px solid #414141; border-radius: 8px; }
"""
        )
        layout = QtWidgets.QVBoxLayout(host)
        layout.setContentsMargins(4, 4, 4, 4)
        control = self.make_control()
        control.setCurrentData(current, emit=False)
        control.setCornerRadius(8)
        control.setPaintInset(1.5)
        control.setCompactHeight(max(23, round(30 * scale)))
        control.setFixedWidth(max(control.sizeHint().width(), round(323 * scale)))
        control._hovered_index = hovered
        layout.addWidget(control)
        host.show()
        host.setFocus()
        control.clearFocus()
        self.app.processEvents()

        image = host.grab().toImage()
        origin = control.mapTo(host, QtCore.QPoint(0, 0))
        return control, image, origin

    def test_selects_options_by_data(self):
        control = self.make_control()
        changes = []
        control.currentDataChanged.connect(changes.append)

        control.setCurrentData("custom")

        self.assertEqual(control.currentIndex(), 2)
        self.assertEqual(control.currentText(), "Custom")
        self.assertEqual(control.currentData(), "custom")
        self.assertEqual(changes, ["custom"])

    def test_compact_height_scales_and_clamps(self):
        control = self.make_control()
        default_width = control.sizeHint().width()

        control.setCompactHeight(24)
        compact_width = control.sizeHint().width()

        self.assertEqual(control.height(), 24)
        self.assertLessEqual(compact_width, default_width)

        control.setCompactHeight(10)
        self.assertEqual(control.height(), 23)

    def test_keyboard_navigation_changes_selection(self):
        control = self.make_control()
        control.setFocus()

        key_event = QtGui.QKeyEvent(
            QtCore.QEvent.Type.KeyPress,
            QtCore.Qt.Key.Key_Right,
            QtCore.Qt.KeyboardModifier.NoModifier,
        )
        QtWidgets.QApplication.sendEvent(control, key_event)

        self.assertEqual(control.currentData(), "custom")

    def test_selection_motion_restrains_edge_overshoot(self):
        control = self.make_control()
        control.show()
        self.app.processEvents()

        control.setCurrentData("custom", animate=True)

        self.assertIsInstance(control._animation, QtCore.QParallelAnimationGroup)
        self.assertEqual(control._animation.animationCount(), 2)
        for index in range(control._animation.animationCount()):
            animation = control._animation.animationAt(index)
            self.assertEqual(animation.duration(), 220)
            self.assertEqual(
                animation.easingCurve().type(),
                QtCore.QEasingCurve.Type.OutCubic,
            )

        control.setCurrentData("step_15", animate=True)
        for index in range(control._animation.animationCount()):
            animation = control._animation.animationAt(index)
            self.assertEqual(
                animation.easingCurve().type(),
                QtCore.QEasingCurve.Type.OutBack,
            )

    def test_theme_palette_is_configured_on_the_shared_component(self):
        control = self.make_control()

        control.setTheme(
            {
                "segment_bg": "#eaeaea",
                "segment_slider_bg": "#ffffff",
                "segment_active_text": "#1d1d1f",
                "muted": "#86868b",
                "hover": "rgba(0, 0, 0, 0.03)",
            }
        )

        self.assertEqual(control._theme["track"].name(), "#eaeaea")
        self.assertEqual(control._theme["slider"].name(), "#ffffff")
        self.assertEqual(control._theme["active_text"].name(), "#1d1d1f")
        self.assertEqual(control._theme["muted"].name(), "#86868b")

    def test_selected_and_hovered_end_caps_stay_mirrored_at_ui_scales(self):
        for scale in (0.75, 1.0, 1.1, 1.5, 2.0):
            cases = (
                (("continuous", -1), ("custom", -1)),
                (("step_15", 0), ("step_15", 2)),
            )
            for left_state, right_state in cases:
                left, left_image, left_origin = self._render_control(
                    scale, *left_state
                )
                right, right_image, right_origin = self._render_control(
                    scale, *right_state
                )
                cap_width = max(4, round(10 * scale))
                for x in range(cap_width):
                    for y in range(left.height()):
                        left_color = left_image.pixelColor(
                            left_origin.x() + x,
                            left_origin.y() + y,
                        )
                        right_color = right_image.pixelColor(
                            right_origin.x() + right.width() - 1 - x,
                            right_origin.y() + y,
                        )
                        channel_delta = max(
                            abs(left_color.red() - right_color.red()),
                            abs(left_color.green() - right_color.green()),
                            abs(left_color.blue() - right_color.blue()),
                            abs(left_color.alpha() - right_color.alpha()),
                        )
                        self.assertLessEqual(
                            channel_delta,
                            2,
                            f"asymmetric cap at scale={scale}, x={x}, y={y}",
                        )

    def test_pt_bridge_preview_uses_the_shared_segmented_control(self):
        from preview import build_settings_preview

        window = build_settings_preview(QtWidgets)
        self.addCleanup(window.deleteLater)
        controls = [
            child
            for child in window.findChildren(QtWidgets.QFrame)
            if child.objectName() == "RizumSegmentedControl"
        ]

        self.assertEqual(len(controls), 1)
        self.assertEqual(controls[0].currentData(), "dark")
        self.assertTrue(hasattr(controls[0], "setTheme"))
        self.assertEqual(
            len(window.findChildren(QtWidgets.QFrame, "RizumInsetSeparator")),
            1,
        )

    def test_bridge_preview_has_no_footer_separator(self):
        from preview import build_bridge_preview

        window = build_bridge_preview(QtWidgets)
        self.addCleanup(window.deleteLater)

        self.assertEqual(
            len(window.findChildren(QtWidgets.QFrame, "RizumInsetSeparator")),
            1,
        )


if __name__ == "__main__":
    unittest.main()
