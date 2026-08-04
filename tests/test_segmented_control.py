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

    def test_selection_motion_matches_bridge_theme_switch(self):
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
                QtCore.QEasingCurve.Type.OutBack,
            )


if __name__ == "__main__":
    unittest.main()
