from __future__ import annotations

import gc
import os
import sys
import unittest
import weakref
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6 import QtCore, QtWidgets

from rizum_ui import make_export_tree_item, make_mock_checkbox


def _settle(app):
    for _ in range(3):
        app.processEvents()


class ExportTreeHoverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    def _panel(self):
        panel = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(panel)
        rows = [
            make_export_tree_item("M_body", make_mock_checkbox(True), meta="4"),
            make_export_tree_item("basecolor", make_mock_checkbox(True), child=True),
        ]
        for row in rows:
            layout.addWidget(row)
        panel.show()
        _settle(self.app)
        return panel, rows

    def _destroy(self, panel):
        panel.deleteLater()
        self.app.sendPostedEvents(None, QtCore.QEvent.Type.DeferredDelete)

    def test_rows_of_a_destroyed_panel_are_collected(self):
        # Every row used to outlive its panel, with its label and checkbox.
        panel, rows = self._panel()
        gone = [weakref.ref(row) for row in rows]
        gone += [weakref.ref(row._rizum_hover_filter) for row in rows]
        gone += [weakref.ref(row._rizum_checkbox) for row in rows]
        self._destroy(panel)
        del panel, rows
        _settle(self.app)
        gc.collect()

        alive = sum(reference() is not None for reference in gone)
        self.assertEqual(alive, 0, f"{alive} of {len(gone)} wrappers outlived the panel")

    def test_leave_clears_the_hover_once_the_pointer_is_off_the_row(self):
        panel, rows = self._panel()
        self.addCleanup(panel.deleteLater)
        hover_filter = rows[1]._rizum_hover_filter
        hover_filter.set_hovered(True)
        self.assertTrue(rows[1]._rizum_row.property("hovered"))

        self.app.sendEvent(rows[1], QtCore.QEvent(QtCore.QEvent.Type.Leave))
        self.assertTrue(rows[1]._rizum_row.property("hovered"))
        _settle(self.app)

        self.assertFalse(rows[1]._rizum_row.property("hovered"))

    def test_a_row_destroyed_in_the_turn_of_its_leave_raises_nothing(self):
        # Painter removes a panel while the pointer is still on one of its
        # rows; the refresh the Leave asked for must die with the row.
        panel, rows = self._panel()
        for row in rows:
            self.app.sendEvent(row, QtCore.QEvent(QtCore.QEvent.Type.Leave))
        self._destroy(panel)
        del panel, rows
        raised = []
        with mock.patch.object(sys, "excepthook", lambda *error: raised.append(error)):
            _settle(self.app)

        self.assertEqual(raised, [])


if __name__ == "__main__":
    unittest.main()
