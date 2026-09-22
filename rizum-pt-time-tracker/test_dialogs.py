import importlib
import os
from pathlib import Path
import sys
import tempfile
import unittest

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from PySide6 import QtWidgets
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
dialogs = importlib.import_module('rizum-pt-time-tracker.dialogs')
core = importlib.import_module('rizum-pt-time-tracker.core')


class DialogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    def test_assignment_validation_and_shared_controls(self):
        with tempfile.TemporaryDirectory() as directory:
            db = core.Ledger(Path(directory) / 'test.sqlite3')
            try:
                path = str(Path(directory) / 'Work.Hair.spp')
                binding = db.auto_bind(path)
                dialog = dialogs.AssignmentDialog(db, path)
                self.assertFalse(dialog.save_button.isDirty())
                self.assertEqual(dialog.selection()[2:], (binding['work'], binding['part']))
                dialog.part.setCurrentIndex(0)
                dialog.part_name.setText('Face')
                self.assertTrue(dialog.save_button.isDirty())
                dialog.part_name.setText(' ')
                self.assertFalse(dialog.save_button.isDirty())
                self.assertFalse(dialog.findChildren(QtWidgets.QComboBox))
                dialog.deleteLater()
            finally:
                db.close()

    def test_number_dialog_and_scale(self):
        dialog = dialogs.NumberDialog('Idle timeout', 'Seconds', 120, 30, 1800, step=30)
        self.assertFalse(dialog.save_button.isDirty())
        dialog.number.setValue(150)
        self.assertTrue(dialog.save_button.isDirty())
        for scale in (0.75, 1.1, 2.0, 1.0):
            dialog.setSettingsUiScale(scale)
            dialog.show()
            self.app.processEvents()
            self.assertGreaterEqual(dialog.save_button.width(), dialog.save_button.sizeHint().width())
            self.assertEqual(dialog.number.value(), 150)
        dialog.close()
        dialog.deleteLater()

    def test_history_empty_and_populated(self):
        for rows in ([], [{'start': 1000, 'seconds': 90, 'part_name': 'Hair', 'manual': False}]):
            dialog = dialogs.HistoryDialog('Work', rows)
            self.assertEqual(dialog.table.rowCount(), len(rows))
            self.assertEqual(dialog.save_button.text(), 'Done')
            dialog.show()
            self.app.processEvents()
            if rows:
                self.assertEqual(dialog.table.palette().base().color().name(), '#202020')
            dialog.close()
            dialog.deleteLater()
