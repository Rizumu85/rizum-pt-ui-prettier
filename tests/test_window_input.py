from __future__ import annotations

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6 import QtCore, QtGui, QtTest, QtWidgets

from rizum_ui.window_input import WindowInputWatch


class Recorder(QtCore.QObject):
    def __init__(self):
        super().__init__()
        self.seen = []

    def eventFilter(self, watched, event):
        self.seen.append((type(watched).__name__, event.type()))
        return False

    def kinds(self, *wanted):
        return [kind for _receiver, kind in self.seen if kind in wanted]


class WindowInputWatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    def setUp(self):
        self.window = QtWidgets.QWidget()
        self.addCleanup(self.window.deleteLater)
        layout = QtWidgets.QVBoxLayout(self.window)
        self.inner = QtWidgets.QFrame()
        self.deep = QtWidgets.QLabel("deep", self.inner)
        QtWidgets.QVBoxLayout(self.inner).addWidget(self.deep)
        layout.addWidget(self.inner)
        self.window.resize(200, 120)
        self.window.show()
        self.app.processEvents()
        self.recorder = Recorder()
        self.watch = WindowInputWatch(self.recorder)
        self.addCleanup(self.watch.stop)

    def test_a_key_is_seen_once_at_the_window(self):
        self.watch.start()
        self.recorder.seen.clear()
        QtTest.QTest.keyClick(self.window.windowHandle(), QtCore.Qt.Key.Key_K)
        self.app.processEvents()
        Type = QtCore.QEvent.Type
        self.assertEqual(self.recorder.kinds(Type.KeyPress), [Type.KeyPress])
        self.assertEqual(self.recorder.kinds(Type.KeyRelease), [Type.KeyRelease])
        self.assertTrue(all(receiver.endswith("Window") for receiver, _kind in self.recorder.seen))

    def test_an_application_filter_gets_the_same_key_several_times(self):
        # What the window filter saves: the press travels up through every
        # widget that does not take it.
        self.app.installEventFilter(self.recorder)
        self.addCleanup(self.app.removeEventFilter, self.recorder)
        self.deep.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.deep.setFocus()
        self.app.processEvents()
        self.recorder.seen.clear()
        QtTest.QTest.keyClick(self.window.windowHandle(), QtCore.Qt.Key.Key_K)
        self.app.processEvents()
        self.assertGreater(len(self.recorder.kinds(QtCore.QEvent.Type.KeyPress)), 1)

    def test_mouse_input_is_seen_and_nothing_else(self):
        self.watch.start()
        self.recorder.seen.clear()
        QtTest.QTest.mouseClick(self.window.windowHandle(), QtCore.Qt.MouseButton.LeftButton, pos=QtCore.QPoint(20, 20))
        timer = QtCore.QTimer()
        timer.start(1)
        QtTest.QTest.qWait(30)
        timer.stop()
        self.window.update()
        self.app.processEvents()
        Type = QtCore.QEvent.Type
        self.assertEqual(self.recorder.kinds(Type.MouseButtonPress), [Type.MouseButtonPress])
        self.assertEqual(self.recorder.kinds(Type.Timer, Type.Paint), [])

    def test_a_window_that_takes_the_focus_is_watched_at_once(self):
        self.watch.start()
        dialog = QtWidgets.QDialog()
        self.addCleanup(dialog.deleteLater)
        dialog.show()
        dialog.windowHandle().requestActivate()
        self.app.processEvents()
        self.recorder.seen.clear()
        QtTest.QTest.keyClick(dialog.windowHandle(), QtCore.Qt.Key.Key_J)
        self.app.processEvents()
        self.assertEqual(len(self.recorder.kinds(QtCore.QEvent.Type.KeyPress)), 1)

    def test_a_menu_that_pops_up_is_watched_at_once(self):
        self.watch.start()
        self.window.windowHandle().requestActivate()
        self.app.processEvents()
        menu = QtWidgets.QMenu(self.window)
        menu.addAction("One")
        self.addCleanup(menu.hide)
        menu.popup(self.window.mapToGlobal(QtCore.QPoint(10, 10)))
        self.app.processEvents()
        self.recorder.seen.clear()
        QtTest.QTest.mouseClick(menu.windowHandle(), QtCore.Qt.MouseButton.LeftButton, pos=QtCore.QPoint(5, 5))
        self.app.processEvents()
        self.assertEqual(len(self.recorder.kinds(QtCore.QEvent.Type.MouseButtonPress)), 1)

    def test_a_window_that_only_appears_is_found_by_the_sweep(self):
        self.watch.start()
        late = QtGui.QWindow()
        self.addCleanup(late.deleteLater)
        late.resize(50, 50)
        late.show()
        self.watch._install()
        self.recorder.seen.clear()
        QtTest.QTest.keyClick(late, QtCore.Qt.Key.Key_L)
        self.app.processEvents()
        self.assertEqual(len(self.recorder.kinds(QtCore.QEvent.Type.KeyPress)), 1)

    def test_stop_takes_the_filter_off_every_window(self):
        self.watch.start()
        self.watch.stop()
        self.recorder.seen.clear()
        QtTest.QTest.keyClick(self.window.windowHandle(), QtCore.Qt.Key.Key_K)
        self.app.processEvents()
        self.assertEqual(self.recorder.seen, [])
        self.assertFalse(self.watch._sweep.isActive())

    def test_start_and_stop_may_repeat(self):
        self.watch.start()
        self.watch.start()
        self.watch.stop()
        self.watch.stop()
        self.watch.start()
        self.recorder.seen.clear()
        QtTest.QTest.keyClick(self.window.windowHandle(), QtCore.Qt.Key.Key_K)
        self.app.processEvents()
        self.assertEqual(len(self.recorder.kinds(QtCore.QEvent.Type.KeyPress)), 1)


if __name__ == "__main__":
    unittest.main()
