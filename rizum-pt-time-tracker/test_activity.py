import tempfile
import unittest
from pathlib import Path
from PySide6 import QtWidgets
from core import Ledger, ActivityClock
from activity import ActivityPolicy, input_context


class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ledger = Ledger(Path(self.tmp.name) / 'time.sqlite3')
        self.path = str(Path(self.tmp.name) / 'Work.spp')
        self.binding = self.ledger.auto_bind(self.path)
        self.clock = ActivityClock(self.ledger)
        self.clock.switch(self.path)
        self.policy = ActivityPolicy(self.clock)

    def tearDown(self):
        self.ledger.close()
        self.tmp.cleanup()

    def offer(self, kind, seconds):
        self.policy.offer(kind, seconds, 1000+seconds)

    def total(self):
        self.clock.flush()
        return sum(row['total'] for row in self.ledger.summary(self.binding['work']))

    def test_plugin_testing_gap_never_bridged(self):
        self.offer('viewport', 0)
        self.offer('viewport', 10)
        self.offer('excluded', 11)
        self.offer('excluded', 30)
        self.offer('viewport', 40)
        self.offer('viewport', 50)
        self.assertEqual(self.total(), 20)

    def test_native_ui_requires_document_evidence(self):
        self.offer('candidate', 0)
        self.policy.confirm(0.1)
        self.offer('candidate', 10)
        self.policy.confirm(10.2)
        self.assertEqual(self.total(), 10)

    def test_unconfirmed_ui_breaks_continuity(self):
        self.offer('viewport', 0)
        self.offer('viewport', 10)
        self.offer('candidate', 11)
        self.policy.expire(12)
        self.offer('viewport', 15)
        self.offer('viewport', 20)
        self.assertEqual(self.total(), 15)

    def test_background_changes_do_not_count(self):
        self.policy.confirm(0)
        self.policy.confirm(10)
        self.assertIsNone(self.clock.last)

    def test_stale_model_event_does_not_confirm(self):
        self.offer('candidate', 0)
        self.policy.confirm(2)
        self.assertIsNone(self.clock.last)

    def test_plugin_input_cancels_pending_native_confirmation(self):
        self.offer('candidate', 0)
        self.offer('excluded', 0.1)
        self.policy.confirm(0.2)
        self.assertIsNone(self.clock.last)

    def test_repeated_model_events_cannot_extend_work(self):
        self.offer('candidate', 0)
        self.policy.confirm(0.1)
        self.policy.confirm(0.2)
        self.policy.confirm(60)
        self.assertEqual(self.total(), 0)

    def test_second_unconfirmed_input_does_not_keep_old_session(self):
        self.offer('viewport', 0)
        self.offer('candidate', 10)
        self.offer('candidate', 10.1)
        self.policy.confirm(10.2)
        self.assertEqual(self.total(), 0)


class ContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    def test_viewport_and_plugin_ancestry(self):
        window = QtWidgets.QMainWindow()
        viewer = QtWidgets.QWidget(window)
        viewer.setObjectName('Viewer3D')
        canvas = QtWidgets.QWidget(viewer)
        self.assertEqual(input_context(canvas, window), 'viewport')
        plugin = QtWidgets.QWidget(window)
        plugin.setObjectName('RizumLiquifyPanel')
        child = QtWidgets.QLineEdit(plugin)
        self.assertEqual(input_context(child, window), 'excluded')
        settings = QtWidgets.QDialog(window)
        self.assertEqual(input_context(QtWidgets.QLineEdit(settings), window), 'excluded')
        native = QtWidgets.QLineEdit(window)
        self.assertEqual(input_context(native, window), 'candidate')
        self.assertEqual(input_context(window.menuBar(), window), 'excluded')
        window.deleteLater()


if __name__ == '__main__':
    unittest.main()
