from __future__ import annotations

from PySide6 import QtWidgets
from PySide6.QtCore import QSettings
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QDialog
import substance_painter.logging as logging
import substance_painter.ui as sp_ui

from .ui import (
    DEFAULT_DRAG_DISTANCE,
    SETTINGS_APPLICATION,
    SETTINGS_KEY,
    SETTINGS_ORGANIZATION,
    SettingsDialog,
)


class RizumDragDistanceSettings:
    def __init__(self):
        self.menu = None
        self.current_action = None
        self.settings_action = None

        self.apply_current_settings()
        self.setup_menu()

    def setup_menu(self) -> None:
        main_window = sp_ui.get_main_window()
        self.menu = QtWidgets.QMenu("Drag Distance", main_window)
        self.menu.setObjectName("rizum_pt_drag_distance_menu")

        self.current_action = QAction(
            f"Current: {DEFAULT_DRAG_DISTANCE} pixels",
            self.menu,
        )
        self.current_action.setEnabled(False)
        self.menu.addAction(self.current_action)

        self.settings_action = QAction("Drag Distance Settings...", self.menu)
        self.settings_action.triggered.connect(self.open_settings)
        self.menu.addAction(self.settings_action)

        sp_ui.add_menu(self.menu)
        self.update_current_action_text()

    def get_current_drag_distance(self) -> int:
        return QtWidgets.QApplication.startDragDistance()

    def apply_current_settings(self) -> None:
        settings = QSettings(SETTINGS_ORGANIZATION, SETTINGS_APPLICATION)
        drag_distance = settings.value(
            SETTINGS_KEY,
            DEFAULT_DRAG_DISTANCE,
            type=int,
        )

        QtWidgets.QApplication.setStartDragDistance(drag_distance)
        logging.info(f"Drag distance set to {drag_distance} pixels")
        self.update_current_action_text()

    def update_current_action_text(self) -> None:
        if self.current_action is not None:
            current_distance = self.get_current_drag_distance()
            self.current_action.setText(f"Current: {current_distance} pixels")

    def open_settings(self) -> None:
        dialog = SettingsDialog(sp_ui.get_main_window())
        if dialog.exec() == QDialog.DialogCode.Accepted:
            dialog.save_settings()
            self.apply_current_settings()
