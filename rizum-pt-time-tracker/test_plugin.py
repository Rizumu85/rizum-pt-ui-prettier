"""Host adapter tests with real Qt and a minimal Painter event dispatcher."""
import importlib
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path
from PySide6 import QtCore, QtWidgets, QtGui

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
module = importlib.import_module('rizum-pt-time-tracker.plugin')


class HostTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old_data = os.environ.get('LOCALAPPDATA')
        os.environ['LOCALAPPDATA'] = self.tmp.name
        self.path = str(Path(self.tmp.name) / 'Body.spp')
        self.callbacks = {}
        self.dock = None
        def add(widget):
            self.dock = QtWidgets.QDockWidget()
            self.dock.setWidget(widget)
            return self.dock
        dispatcher = types.SimpleNamespace(
            connect=lambda event, callback: self.callbacks.update({event: callback}),
            disconnect=lambda event, callback: self.callbacks.pop(event))
        self.host = types.SimpleNamespace(
            project=types.SimpleNamespace(is_open=lambda: bool(self.path), file_path=lambda: self.path),
            event=types.SimpleNamespace(ProjectSaved='saved', ProjectEditionEntered='opened',
                                        ProjectAboutToClose='closing', DISPATCHER=dispatcher),
            ui=types.SimpleNamespace(add_dock_widget=add, delete_ui_element=lambda dock: dock.deleteLater()),
            logging=types.SimpleNamespace(error=lambda message: self.fail(message)))
        sys.modules['substance_painter'] = self.host
        self.plugin = module.Plugin()
        self.plugin.foreground = lambda: True

    def tearDown(self):
        self.plugin.close()
        self.assertFalse(self.callbacks)
        if self.old_data is None:
            os.environ.pop('LOCALAPPDATA', None)
        else:
            os.environ['LOCALAPPDATA'] = self.old_data
        sys.modules.pop('substance_painter', None)
        self.tmp.cleanup()

    def bind(self):
        self.plugin.ledger.bind(self.path, 'Wedding', 'Body')
        self.plugin.clock.switch(self.path)

    def test_save_as_and_close_open_are_distinct(self):
        self.bind()
        original = self.plugin.ledger.binding(self.path)
        self.path = str(Path(self.tmp.name) / 'Hair.spp')
        self.callbacks['saved'](None)
        self.assertEqual(self.plugin.ledger.binding(self.path)['work'], original['work'])
        self.assertTrue(self.plugin.branch)
        self.callbacks['closing'](None)
        self.path = str(Path(self.tmp.name) / 'Other.spp')
        self.callbacks['opened'](None)
        self.assertIsNone(self.plugin.ledger.binding(self.path))
        self.assertIsNone(self.plugin.clock.path)

    def test_inputs_pause_and_deactivation(self):
        self.bind()
        event = QtGui.QKeyEvent(QtCore.QEvent.Type.KeyPress, QtCore.Qt.Key.Key_A, QtCore.Qt.KeyboardModifier.NoModifier)
        self.assertFalse(self.plugin.eventFilter(self.dock, event))
        self.assertIsNotNone(self.plugin.clock.last)
        self.plugin.pause()
        self.plugin.eventFilter(self.dock, event)
        self.assertIsNone(self.plugin.clock.last)
        self.plugin.pause()
        self.plugin.eventFilter(self.dock, event)
        self.plugin.eventFilter(self.plugin.panel, QtCore.QEvent(QtCore.QEvent.Type.ApplicationDeactivate))
        self.assertIsNone(self.plugin.clock.last)

    def test_timer_flush_and_ui(self):
        self.bind()
        self.plugin.clock.input(0, 1000)
        self.plugin.clock.input(60, 1060)
        self.plugin.tick()
        self.assertEqual(self.plugin.panel.total.text(), '00:01:00')
        self.assertFalse(self.plugin.failed)

    def test_closing_does_not_reacquire_old_project(self):
        self.bind()
        self.callbacks['closing'](None)
        self.plugin.tick()
        self.assertIsNone(self.plugin.path)
        self.assertIsNone(self.plugin.clock.path)

    def test_short_sleep_is_excluded(self):
        self.bind()
        self.plugin.clock.input(0, 1000)
        self.plugin.clock.input(10, 1010)
        self.plugin.last_tick -= 20
        self.plugin.tick()
        self.assertIsNone(self.plugin.clock.last)
        self.assertEqual(self.plugin.panel.total.text(), '00:00:10')

    def test_record_panel_does_not_extend_activity(self):
        self.bind()
        event = QtGui.QKeyEvent(QtCore.QEvent.Type.KeyPress, QtCore.Qt.Key.Key_A, QtCore.Qt.KeyboardModifier.NoModifier)
        self.plugin.eventFilter(self.plugin.panel, event)
        self.assertIsNone(self.plugin.clock.last)

    def test_scale_resizes_painted_controls(self):
        panel = self.plugin.panel
        before = panel.pause.height()
        font = panel.font()
        font.setPixelSize(28)
        panel.setFont(font)
        self.assertGreater(panel.pause.height(), before)


if __name__ == '__main__':
    unittest.main()
