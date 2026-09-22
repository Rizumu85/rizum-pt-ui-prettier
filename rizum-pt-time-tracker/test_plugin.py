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
        self.path = str(Path(self.tmp.name) / 'Penglai_Wedding.Body.spp')
        self.callbacks = {}
        self.window = QtWidgets.QMainWindow()
        self.viewer = QtWidgets.QWidget(self.window)
        self.viewer.setObjectName('Viewer3D')
        dispatcher = types.SimpleNamespace(
            connect=lambda event, callback: self.callbacks.update({event: callback}),
            disconnect=lambda event, callback: self.callbacks.pop(event))
        self.host = types.SimpleNamespace(
            project=types.SimpleNamespace(is_open=lambda: bool(self.path), file_path=lambda: self.path, is_busy=lambda: False),
            event=types.SimpleNamespace(ProjectSaved='saved', ProjectEditionEntered='opened',
                                        ProjectAboutToClose='closing', LayerStacksModelDataChanged='changed',
                                        BusyStatusChanged='busy', DISPATCHER=dispatcher),
            ui=types.SimpleNamespace(get_main_window=lambda: self.window,
                                     add_menu=lambda menu: self.window.menuBar().addMenu(menu),
                                     delete_ui_element=lambda menu: menu.deleteLater()),
            logging=types.SimpleNamespace(error=lambda message: self.fail(message)))
        sys.modules['substance_painter'] = self.host
        self.plugin = module.Plugin()
        self.plugin.foreground = lambda: True

    def tearDown(self):
        self.plugin.close()
        self.assertFalse(self.callbacks)
        self.window.deleteLater()
        if self.old_data is None:
            os.environ.pop('LOCALAPPDATA', None)
        else:
            os.environ['LOCALAPPDATA'] = self.old_data
        sys.modules.pop('substance_painter', None)
        self.tmp.cleanup()

    def bind(self):
        self.assertIsNotNone(self.plugin.ledger.binding(self.path))

    def test_save_as_and_close_open_are_distinct(self):
        self.bind()
        original = self.plugin.ledger.binding(self.path)
        self.path = str(Path(self.tmp.name) / 'Penglai_Wedding.Hair.spp')
        self.callbacks['saved'](None)
        self.assertEqual(self.plugin.ledger.binding(self.path)['work'], original['work'])
        self.assertEqual(self.plugin.ledger.binding(self.path)['part_name'], 'Hair')
        self.callbacks['closing'](None)
        self.path = str(Path(self.tmp.name) / 'Other.spp')
        self.callbacks['opened'](None)
        self.assertNotEqual(self.plugin.ledger.binding(self.path)['work'], original['work'])
        self.assertIsNotNone(self.plugin.clock.path)

    def test_inputs_pause_and_deactivation(self):
        self.bind()
        event = QtGui.QKeyEvent(QtCore.QEvent.Type.KeyPress, QtCore.Qt.Key.Key_A, QtCore.Qt.KeyboardModifier.NoModifier)
        self.assertFalse(self.plugin.eventFilter(self.viewer, event))
        self.callbacks['changed'](None)
        self.assertIsNotNone(self.plugin.clock.last)
        self.plugin.pause()
        self.plugin.eventFilter(self.viewer, event)
        self.assertIsNone(self.plugin.clock.last)
        self.plugin.pause()
        self.plugin.eventFilter(self.viewer, event)
        self.callbacks['changed'](None)
        self.plugin.eventFilter(self.window, QtCore.QEvent(QtCore.QEvent.Type.ApplicationDeactivate))
        self.assertIsNone(self.plugin.clock.last)

    def test_timer_flush_and_ui(self):
        self.bind()
        self.plugin.clock.input(0, 1000)
        self.plugin.clock.input(60, 1060)
        self.plugin.tick()
        self.plugin.menu_opened()
        self.assertEqual(self.plugin.total_action.text(), 'Total\t00:01:00')
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
        self.plugin.menu_opened()
        self.assertEqual(self.plugin.total_action.text(), 'Total\t00:00:10')

    def test_record_menu_does_not_extend_activity(self):
        self.bind()
        event = QtGui.QKeyEvent(QtCore.QEvent.Type.KeyPress, QtCore.Qt.Key.Key_A, QtCore.Qt.KeyboardModifier.NoModifier)
        self.plugin.menu.popup(QtCore.QPoint(0, 0))
        self.plugin.eventFilter(self.plugin.menu, event)
        self.assertIsNone(self.plugin.clock.last)
        self.plugin.menu.hide()

    def test_native_menu_without_dock(self):
        self.assertFalse(self.window.findChildren(QtWidgets.QDockWidget))
        self.assertIn(self.plugin.menu.menuAction(), self.window.menuBar().actions())
        self.assertEqual(self.plugin.title_action.text(), 'Penglai_Wedding')

    def test_other_menu_clears_pending_confirmation(self):
        self.plugin.activity.offer('candidate', 0, 1000)
        menu = QtWidgets.QMenu(self.window)
        self.plugin.eventFilter(menu, QtCore.QEvent(QtCore.QEvent.Type.Show))
        self.callbacks['changed'](None)
        self.assertIsNone(self.plugin.clock.last)
        self.assertIsNone(self.plugin.activity.pending)

    def test_busy_period_interrupts_session(self):
        self.plugin.clock.input(0, 1000)
        self.plugin.clock.input(10, 1010)
        self.callbacks['busy'](types.SimpleNamespace(busy=True))
        self.assertIsNone(self.plugin.clock.last)
        event = QtGui.QKeyEvent(QtCore.QEvent.Type.KeyPress, QtCore.Qt.Key.Key_A, QtCore.Qt.KeyboardModifier.NoModifier)
        self.plugin.eventFilter(self.viewer, event)
        self.callbacks['changed'](None)
        self.assertIsNone(self.plugin.activity.pending)
        self.callbacks['busy'](types.SimpleNamespace(busy=False))
        self.assertIsNone(self.plugin.clock.last)


if __name__ == '__main__':
    unittest.main()
