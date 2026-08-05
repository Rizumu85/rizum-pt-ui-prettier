import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6 import QtCore, QtGui, QtTest, QtWidgets

from rizum_ui.components import make_compact_stepper


class CompactStepperTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    def _bright_text_y_bounds(self, widget):
        image = QtGui.QImage(
            widget.size(),
            QtGui.QImage.Format.Format_ARGB32,
        )
        image.fill(QtGui.QColor("#202020"))
        widget.render(image)
        text_rows = []
        for y in range(image.height()):
            for x in range(6, 30):
                color = image.pixelColor(x, y)
                if min(color.red(), color.green(), color.blue()) >= 185:
                    text_rows.append(y)
        self.assertTrue(text_rows)
        return min(text_rows), max(text_rows)

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
        QtTest.QTest.keyClicks(stepper._editor, "12.5")
        QtTest.QTest.keyClick(stepper._editor, QtCore.Qt.Key.Key_Return)

        self.assertEqual(stepper.value(), 12.5)

    def test_editing_uses_a_native_cursor_that_tracks_navigation(self):
        stepper = make_compact_stepper(50)
        self.addCleanup(stepper.deleteLater)
        stepper.show()

        QtTest.QTest.mouseClick(
            stepper,
            QtCore.Qt.MouseButton.LeftButton,
            pos=QtCore.QPoint(20, 16),
        )
        self.app.processEvents()

        self.assertIsInstance(stepper._editor, QtWidgets.QLineEdit)
        self.assertTrue(stepper._editor.isVisible())
        self.assertTrue(stepper._editor.hasFocus())
        self.assertEqual(stepper._editor.cursorPosition(), 2)

        QtTest.QTest.keyClick(stepper._editor, QtCore.Qt.Key.Key_Left)
        self.assertEqual(stepper._editor.cursorPosition(), 1)
        QtTest.QTest.mouseClick(
            stepper._editor,
            QtCore.Qt.MouseButton.LeftButton,
            pos=QtCore.QPoint(
                stepper._editor.textMargins().left(),
                stepper._editor.height() // 2,
            ),
        )
        self.assertEqual(stepper._editor.cursorPosition(), 0)
        QtTest.QTest.keyClick(stepper._editor, QtCore.Qt.Key.Key_Right)
        self.assertEqual(stepper._editor.cursorPosition(), 1)
        QtTest.QTest.keyClick(stepper._editor, QtCore.Qt.Key.Key_Delete)
        self.assertEqual(stepper._editor.text(), "5")

    def test_editor_input_surface_cannot_paint_a_second_cursor_or_text_layer(self):
        stepper = make_compact_stepper(50)
        self.addCleanup(stepper.deleteLater)
        stepper.show()

        QtTest.QTest.mouseClick(
            stepper,
            QtCore.Qt.MouseButton.LeftButton,
            pos=QtCore.QPoint(20, 16),
        )
        self.app.processEvents()

        stepper._editor.setStyleSheet(
            "QLineEdit { color: #ff00ff; selection-color: #ff00ff; }"
        )
        image = stepper.grab().toImage()
        magenta_pixels = 0
        for y in range(image.height()):
            for x in range(image.width()):
                color = image.pixelColor(x, y)
                if color.red() > 220 and color.blue() > 220 and color.green() < 40:
                    magenta_pixels += 1

        self.assertEqual(magenta_pixels, 0)
        self.assertTrue(stepper._cursor_timer.isActive())
        self.assertTrue(stepper._cursor_visible)
        self.assertTrue(hasattr(stepper, "_draw_edit_cursor"))

    def test_edit_text_keeps_its_baseline_under_host_line_edit_alignment(self):
        stepper = make_compact_stepper(50)
        self.addCleanup(stepper.deleteLater)
        stepper.setTheme(
            {
                "window_bg": "#202020",
                "text": "#f0f0f0",
                "muted": "#9a9a9a",
                "control_hover": "#4a4a4a",
            }
        )
        stepper.show()
        self.app.processEvents()
        resting_bounds = self._bright_text_y_bounds(stepper)

        QtTest.QTest.mouseClick(
            stepper,
            QtCore.Qt.MouseButton.LeftButton,
            pos=QtCore.QPoint(20, 16),
        )
        stepper._editor.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignLeft
            | QtCore.Qt.AlignmentFlag.AlignTop
        )
        self.app.processEvents()

        self.assertEqual(
            stepper._editor.alignment(),
            QtCore.Qt.AlignmentFlag.AlignLeft
            | QtCore.Qt.AlignmentFlag.AlignVCenter,
        )
        self.assertEqual(
            self._bright_text_y_bounds(stepper),
            resting_bounds,
        )

    def test_native_editor_stays_centered_when_host_bypasses_alignment_override(self):
        for height in (24, 32, 40, 48):
            with self.subTest(height=height):
                stepper = make_compact_stepper(100)
                self.addCleanup(stepper.deleteLater)
                stepper.setCompactHeight(height)
                stepper.show()
                self.app.processEvents()
                resting_bounds = self._bright_text_y_bounds(stepper)

                QtTest.QTest.mouseClick(
                    stepper,
                    QtCore.Qt.MouseButton.LeftButton,
                    pos=QtCore.QPoint(round(20 * height / 32), height // 2),
                )
                QtWidgets.QLineEdit.setAlignment(
                    stepper._editor,
                    QtCore.Qt.AlignmentFlag.AlignLeft
                    | QtCore.Qt.AlignmentFlag.AlignTop,
                )
                self.app.processEvents()
                editing_bounds = self._bright_text_y_bounds(stepper)

                self.assertLessEqual(
                    abs(sum(editing_bounds) - sum(resting_bounds)),
                    1,
                )

    def test_backspace_removes_one_digit_instead_of_the_whole_value(self):
        stepper = make_compact_stepper(50)
        self.addCleanup(stepper.deleteLater)
        stepper.show()

        QtTest.QTest.mouseClick(
            stepper,
            QtCore.Qt.MouseButton.LeftButton,
            pos=QtCore.QPoint(20, 16),
        )
        QtTest.QTest.keyClick(stepper._editor, QtCore.Qt.Key.Key_Backspace)

        self.assertEqual(stepper._editor.text(), "5")
        QtTest.QTest.keyClick(stepper._editor, QtCore.Qt.Key.Key_Return)
        self.assertEqual(stepper.value(), 5)

    def test_clicking_blank_host_space_exits_edit_mode(self):
        host = QtWidgets.QWidget()
        self.addCleanup(host.deleteLater)
        host.setFixedSize(300, 100)
        stepper = make_compact_stepper(50)
        stepper.setParent(host)
        stepper.move(10, 10)
        host.show()
        self.app.processEvents()

        QtTest.QTest.mouseClick(
            stepper,
            QtCore.Qt.MouseButton.LeftButton,
            pos=QtCore.QPoint(20, 16),
        )
        self.assertTrue(stepper._editing)

        QtTest.QTest.mouseClick(
            host,
            QtCore.Qt.MouseButton.LeftButton,
            pos=QtCore.QPoint(250, 80),
        )
        self.app.processEvents()

        self.assertFalse(stepper._editing)
        self.assertFalse(stepper._editor.isVisible())

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
