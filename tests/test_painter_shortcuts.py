"""Painter's registered shortcuts and the clashes a plugin key would cause."""

import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PySide6 import QtGui, QtWidgets  # noqa: E402

from rizum_ui import painter_shortcuts  # noqa: E402


class PainterShortcutsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    def setUp(self):
        self.main = QtWidgets.QMainWindow()
        self.addCleanup(self.main.deleteLater)

    def action(self, text, key, parent=None):
        action = QtGui.QAction(text, parent or self.main)
        action.setShortcut(QtGui.QKeySequence(key))
        (parent or self.main).addAction(action)
        return action

    def test_actions_and_shortcuts_are_listed_by_their_key(self):
        self.action("&Invert tool color", "X")
        self.action("Paint\tCtrl+1", "Ctrl+1")
        menu = QtWidgets.QMenu(self.main)
        self.action("Eraser", "X", menu)
        shortcut = QtGui.QShortcut(QtGui.QKeySequence("Shift+Z"), self.main)
        shortcut.setObjectName("curve_snap_to_mesh")
        index = painter_shortcuts.registered_shortcut_index(self.main)
        self.assertEqual(index["X"], ["Invert tool color", "Eraser"])
        self.assertEqual(index["Ctrl+1"], ["Paint"])
        self.assertEqual(index["Shift+Z"], ["curve_snap_to_mesh"])

    def test_the_plugins_own_action_is_not_a_clash(self):
        own = self.action("Switch to previous brush", "`")
        index = painter_shortcuts.registered_shortcut_index(self.main, ignore=[own])
        self.assertEqual(painter_shortcuts.shortcut_conflicts("`", index), [])
        self.action("Something of Painter's", "`")
        index = painter_shortcuts.registered_shortcut_index(self.main, ignore=[own])
        self.assertEqual(painter_shortcuts.shortcut_conflicts("`", index), ["Something of Painter's"])

    def test_keys_compare_in_their_portable_spelling(self):
        self.action("Focus mode", "Alt+Q")
        index = painter_shortcuts.registered_shortcut_index(self.main)
        self.assertEqual(painter_shortcuts.shortcut_conflicts("alt+q", index), ["Focus mode"])
        self.assertEqual(painter_shortcuts.shortcut_conflicts("", index), [])
        self.assertEqual(painter_shortcuts.canonical(" Shift+z "), "Shift+Z")


if __name__ == "__main__":
    unittest.main()
