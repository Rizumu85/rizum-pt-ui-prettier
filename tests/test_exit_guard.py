from __future__ import annotations

import os
import unittest
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6 import QtCore, QtWidgets

from rizum_ui import exit_guard


class ExitGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    def setUp(self):
        self.app.setProperty(exit_guard.DONE_PROPERTY, None)

    def tearDown(self):
        self.app.setProperty(exit_guard.DONE_PROPERTY, None)

    def _timer_event(self, target):
        self.app.sendEvent(target, QtCore.QTimerEvent(1))

    def test_first_timer_event_of_a_static_object_ends_the_guard(self):
        # A plain QObject stands in for Qt's pixmap cache, which cannot be
        # reached from Python except through an event filter.
        stand_in = QtCore.QObject()
        with mock.patch.object(exit_guard, "STATIC_CLASSES", frozenset({"QObject"})):
            guard = exit_guard.install()
            self.assertIsNotNone(guard)
            self._timer_event(stand_in)
        self.assertIs(stand_in.property(exit_guard.PYSIDE_PROPERTY), True)
        self.assertTrue(self.app.property(exit_guard.DONE_PROPERTY))
        self.assertIsNone(exit_guard.install())

    def test_other_objects_and_events_are_left_alone(self):
        timer = QtCore.QTimer()
        plain = QtCore.QObject()
        guard = exit_guard.install()
        self._timer_event(timer)
        self._timer_event(plain)
        self.app.sendEvent(plain, QtCore.QEvent(QtCore.QEvent.Type.User))
        self.assertIsNone(timer.property(exit_guard.PYSIDE_PROPERTY))
        self.assertIsNone(plain.property(exit_guard.PYSIDE_PROPERTY))
        self.assertFalse(self.app.property(exit_guard.DONE_PROPERTY))
        exit_guard.remove(guard)

    def test_a_removed_guard_no_longer_acts(self):
        stand_in = QtCore.QObject()
        with mock.patch.object(exit_guard, "STATIC_CLASSES", frozenset({"QObject"})):
            guard = exit_guard.install()
            exit_guard.remove(guard)
            self._timer_event(stand_in)
        self.assertIsNone(stand_in.property(exit_guard.PYSIDE_PROPERTY))
        self.assertFalse(self.app.property(exit_guard.DONE_PROPERTY))


if __name__ == "__main__":
    unittest.main()
