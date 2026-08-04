import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6 import QtCore, QtTest, QtWidgets

from rizum_ui.components import make_compact_stepper


class CompactStepperTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    def test_decimal_value_can_be_typed_directly(self):
        stepper = make_compact_stepper(
            5.0,
            minimum=0.1,
            maximum=180.0,
            step=0.5,
            decimals=1,
        )
        stepper.show()

        QtTest.QTest.mouseClick(
            stepper,
            QtCore.Qt.MouseButton.LeftButton,
            pos=QtCore.QPoint(20, 16),
        )
        QtTest.QTest.keyClicks(stepper, "12.5")
        QtTest.QTest.keyClick(stepper, QtCore.Qt.Key.Key_Return)

        self.assertEqual(stepper.value(), 12.5)

    def test_compact_height_scales_frame_and_painted_geometry(self):
        stepper = make_compact_stepper(8)
        stepper.setCompactHeight(40)

        self.assertEqual(stepper.height(), 40)
        self.assertEqual(stepper.width(), 150)
        self.assertEqual(stepper.value(), 8)
        self.assertIsInstance(stepper.value(), int)

    def test_default_hover_matches_pt_bridge_dark_theme(self):
        shared_default = make_compact_stepper(8)
        bridge_themed = make_compact_stepper(8)
        bridge_themed.setTheme(
            {
                "window_bg": "#1b1b1b",
                "text": "#e0e0e0",
                "muted": "#9e9e9e",
                "control_hover": "rgba(255, 255, 255, 0.08)",
            }
        )

        self.assertEqual(
            shared_default._hover_color().rgba(),
            bridge_themed._hover_color().rgba(),
        )


if __name__ == "__main__":
    unittest.main()
