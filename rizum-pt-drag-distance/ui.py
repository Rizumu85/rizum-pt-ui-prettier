from __future__ import annotations

from PySide6 import QtCore, QtWidgets

from .rizum_ui import (
    PAINTER_DIALOG_STYLE,
    PainterSettingsDialog,
    SecondaryActionButton,
    make_compact_stepper,
)


SETTINGS_ORGANIZATION = "RizumDragDistance"
SETTINGS_APPLICATION = "Settings"
SETTINGS_KEY = "drag_distance"
DEFAULT_DRAG_DISTANCE = 50

_WINDOW_SURFACE = PAINTER_DIALOG_STYLE["surface"]
_CONTROL_BACKGROUND = PAINTER_DIALOG_STYLE["control"]
_CONTROL_HOVER = PAINTER_DIALOG_STYLE["control_hover"]
_CONTROL_PRESSED = PAINTER_DIALOG_STYLE["control_pressed"]
_TEXT = PAINTER_DIALOG_STYLE["text"]
_TEXT_MUTED = PAINTER_DIALOG_STYLE["muted"]
_PRIMARY = PAINTER_DIALOG_STYLE["accent"]


class SettingsDialog(PainterSettingsDialog):
    """Compact drag-distance settings using the shared Painter UI kit."""

    BASE_WIDTH = 250
    BASE_HEIGHT = 96

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("RizumDragDistanceDialog")
        self.setWindowTitle("Drag Distance Settings")
        self.setModal(True)

        body = QtWidgets.QWidget()
        body.setObjectName("RizumDragDistanceBody")
        self._body_layout = QtWidgets.QVBoxLayout(body)
        self._body_layout.setSpacing(12)
        self.settingsSurfaceLayout().addWidget(body)

        self._value_row = QtWidgets.QWidget()
        self._value_row.setObjectName("RizumDragDistanceRow")
        value_layout = QtWidgets.QHBoxLayout(self._value_row)
        value_layout.setContentsMargins(0, 0, 0, 0)
        value_layout.setSpacing(8)

        text_block = QtWidgets.QWidget()
        text_block.setObjectName("RizumDragDistanceTexts")
        text_layout = QtWidgets.QVBoxLayout(text_block)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(1)

        self._name_label = QtWidgets.QLabel("Drag distance")
        self._name_label.setObjectName("RizumSettingsItemName")
        self._unit_label = QtWidgets.QLabel("pixels")
        self._unit_label.setObjectName("RizumSettingsItemMeta")
        text_layout.addWidget(self._name_label)
        text_layout.addWidget(self._unit_label)

        self.spin_box = make_compact_stepper(
            value=DEFAULT_DRAG_DISTANCE,
            minimum=1,
            maximum=100,
            step=1,
        )
        self.spin_box.setTheme(
            {
                "window_bg": _WINDOW_SURFACE,
                "text": _TEXT,
                "muted": _TEXT_MUTED,
                "control_hover": _CONTROL_HOVER,
            }
        )

        value_layout.addWidget(text_block)
        value_layout.addStretch(1)
        value_layout.addWidget(self.spin_box)
        self._body_layout.addWidget(self._value_row)

        self._button_row = QtWidgets.QWidget()
        self._button_row.setObjectName("RizumDragDistanceFooter")
        self._button_layout = QtWidgets.QHBoxLayout(self._button_row)
        self._button_layout.setContentsMargins(0, 0, 0, 0)
        self._button_layout.setSpacing(8)

        self.cancel_button = SecondaryActionButton(
            "Cancel",
            background=_CONTROL_BACKGROUND,
            hover_background=_CONTROL_HOVER,
            pressed_background=_CONTROL_PRESSED,
            text_color=_TEXT,
        )
        self.ok_button = SecondaryActionButton(
            "OK",
            background=_PRIMARY,
            hover_background=PAINTER_DIALOG_STYLE["accent_hover"],
            pressed_background=PAINTER_DIALOG_STYLE["accent_pressed"],
            text_color=_WINDOW_SURFACE,
        )
        self.cancel_button.clicked.connect(self.reject)
        self.ok_button.clicked.connect(self.accept)
        self._button_layout.addWidget(self.cancel_button, 1)
        self._button_layout.addWidget(self.ok_button, 1)
        self._body_layout.addWidget(self._button_row)

        self.settingsUiScaleChanged.connect(self._apply_ui_scale)
        self.load_settings()
        self._apply_ui_scale(self.settingsUiScale())

    def _apply_ui_scale(self, scale: float) -> None:
        del scale
        self._update_surface_stylesheet()
        surface = self.settingsSurface()
        surface.setStyleSheet(
            surface.styleSheet()
            + f"""
QFrame#RizumPainterSettingsSurface {{
    background: {_WINDOW_SURFACE};
}}
QWidget#RizumDragDistanceBody,
QWidget#RizumDragDistanceRow,
QWidget#RizumDragDistanceTexts,
QWidget#RizumDragDistanceFooter {{
    background: transparent;
    border: 0;
}}
"""
        )

        margin_x = self.settingsMetric(16, 12)
        margin_top = self.settingsMetric(12, 9)
        margin_bottom = self.settingsMetric(12, 9)
        spacing = self.settingsMetric(12, 9)
        control_height = self.settingsMetric(32, 24)
        button_height = self.settingsMetric(28, 21)

        self._body_layout.setContentsMargins(
            margin_x,
            margin_top,
            margin_x,
            margin_bottom,
        )
        self._body_layout.setSpacing(spacing)
        self._button_layout.setSpacing(self.settingsMetric(8, 6))
        self._value_row.setFixedHeight(control_height)
        self._button_row.setFixedHeight(button_height)
        self.spin_box.setCompactHeight(control_height)
        self.cancel_button.setCompactHeight(button_height)
        self.ok_button.setCompactHeight(button_height)

        ui_scale = self.settingsUiScale()
        self.setFixedSize(
            int(round(self.BASE_WIDTH * ui_scale)),
            int(round(self.BASE_HEIGHT * ui_scale)),
        )

    def load_settings(self) -> None:
        settings = QtCore.QSettings(
            SETTINGS_ORGANIZATION,
            SETTINGS_APPLICATION,
        )
        drag_distance = settings.value(
            SETTINGS_KEY,
            DEFAULT_DRAG_DISTANCE,
            type=int,
        )
        self.spin_box.setValue(drag_distance, emit=False)

    def save_settings(self) -> None:
        settings = QtCore.QSettings(
            SETTINGS_ORGANIZATION,
            SETTINGS_APPLICATION,
        )
        settings.setValue(SETTINGS_KEY, self.spin_box.value())

    def get_drag_distance(self) -> int:
        return int(self.spin_box.value())
