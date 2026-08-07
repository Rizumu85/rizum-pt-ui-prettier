from __future__ import annotations

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6 import QtWidgets

from rizum_ui import IconActionButton, PAINTER_DIALOG_STYLE, SecondaryActionButton


def make_button(text="Export", icon_name="action-export.svg"):
    theme = PAINTER_DIALOG_STYLE
    return IconActionButton(
        text,
        icon_name,
        theme["accent"],
        theme["accent_hover"],
        theme["accent_pressed"],
        theme["accent_text"],
    )


class IconActionButtonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    def test_default_size_matches_secondary_action_baseline(self):
        button = make_button()
        self.addCleanup(button.deleteLater)

        self.assertEqual(button.height(), SecondaryActionButton.BASE_HEIGHT)
        self.assertEqual(button.paintedIconSize(), IconActionButton.BASE_ICON_SIZE)

    def test_compact_height_scales_the_painted_icon(self):
        button = make_button()
        self.addCleanup(button.deleteLater)

        button.setCompactHeight(56)
        self.assertEqual(button.height(), 56)
        self.assertEqual(button.paintedIconSize(), 28)

    def test_compact_height_floor_keeps_icon_proportional(self):
        button = make_button()
        self.addCleanup(button.deleteLater)

        button.setCompactHeight(4)
        self.assertEqual(button.height(), SecondaryActionButton.MIN_HEIGHT)
        # round(14 * (21 / 28)) = 10, exactly the 0.75x icon floor.
        self.assertEqual(
            button.paintedIconSize(), IconActionButton.MIN_ICON_SIZE
        )

    def test_painted_icon_size_clamps_to_floor(self):
        button = make_button()
        self.addCleanup(button.deleteLater)

        button.setPaintedIconSize(2)
        self.assertEqual(
            button.paintedIconSize(), IconActionButton.MIN_ICON_SIZE
        )

    def test_size_hint_includes_icon_and_gap(self):
        theme = PAINTER_DIALOG_STYLE
        text_only = SecondaryActionButton(
            "Export",
            theme["accent"],
            theme["accent_hover"],
            theme["accent_pressed"],
            theme["accent_text"],
        )
        with_icon = make_button("Export")
        self.addCleanup(text_only.deleteLater)
        self.addCleanup(with_icon.deleteLater)

        self.assertEqual(
            with_icon.sizeHint().width(),
            text_only.sizeHint().width()
            + with_icon.paintedIconSize()
            + with_icon._icon_gap(),
        )


if __name__ == "__main__":
    unittest.main()
