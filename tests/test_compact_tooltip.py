"""Regression tests for compact tooltip sizing."""

from __future__ import annotations

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6 import QtGui, QtWidgets

from rizum_ui.components import install_compact_tooltip


class CompactTooltipMetricsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    def make_tooltip(self, owner_point_size, scale):
        owner = QtWidgets.QPushButton()
        font = QtGui.QFont(owner.font())
        font.setPointSizeF(owner_point_size)
        owner.setFont(font)
        install_compact_tooltip(owner, "Open fonts folder")
        owner.setCompactTooltipScale(scale)
        tooltip_filter = owner._rizum_compact_tooltip_filter
        tooltip = tooltip_filter._ensure_tooltip()
        tooltip.polishMetrics()
        tooltip.adjustSize()
        return owner, tooltip

    def test_explicit_scale_is_independent_of_owner_point_size(self):
        small_owner, small = self.make_tooltip(8.0, 1.0)
        large_owner, large = self.make_tooltip(14.0, 1.0)
        self.addCleanup(small_owner.deleteLater)
        self.addCleanup(large_owner.deleteLater)

        self.assertEqual(small._label.font().pixelSize(), 14)
        self.assertEqual(large._label.font().pixelSize(), 14)
        self.assertEqual(small._layout.contentsMargins().left(), 12)
        self.assertEqual(large._layout.contentsMargins().left(), 12)

    def test_ui_scale_grows_font_and_popup_padding(self):
        owner, tooltip = self.make_tooltip(9.0, 1.1)
        self.addCleanup(owner.deleteLater)

        margins = tooltip._layout.contentsMargins()
        self.assertEqual(tooltip._label.font().pixelSize(), 15)
        self.assertEqual((margins.left(), margins.top()), (13, 8))

    def test_host_label_stylesheet_cannot_shrink_tooltip_font(self):
        previous_stylesheet = self.app.styleSheet()
        self.app.setStyleSheet("QLabel { font-size: 8px; }")
        self.addCleanup(self.app.setStyleSheet, previous_stylesheet)

        owner, tooltip = self.make_tooltip(9.0, 1.0)
        self.addCleanup(owner.deleteLater)
        tooltip.show()
        self.app.processEvents()

        self.assertEqual(tooltip._label.font().pixelSize(), 14)


if __name__ == "__main__":
    unittest.main()
