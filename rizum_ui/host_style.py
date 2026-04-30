"""Host style helpers for previewing without Substance 3D Painter."""

from __future__ import annotations

import json
from pathlib import Path


PALETTE_ROLES = [
    "Window",
    "WindowText",
    "Base",
    "AlternateBase",
    "ToolTipBase",
    "ToolTipText",
    "Text",
    "Button",
    "ButtonText",
    "BrightText",
    "Highlight",
    "HighlightedText",
]


def apply_painter_like_base(app):
    """Apply a dark Qt baseline that approximates Painter's host chrome."""
    from PySide6 import QtGui, QtWidgets

    app.setStyle(QtWidgets.QStyleFactory.create("Fusion"))

    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.ColorRole.Window, QtGui.QColor("#1f2023"))
    palette.setColor(QtGui.QPalette.ColorRole.WindowText, QtGui.QColor("#e6e8eb"))
    palette.setColor(QtGui.QPalette.ColorRole.Base, QtGui.QColor("#17181b"))
    palette.setColor(QtGui.QPalette.ColorRole.AlternateBase, QtGui.QColor("#24262a"))
    palette.setColor(QtGui.QPalette.ColorRole.ToolTipBase, QtGui.QColor("#2b2e33"))
    palette.setColor(QtGui.QPalette.ColorRole.ToolTipText, QtGui.QColor("#f4f6f8"))
    palette.setColor(QtGui.QPalette.ColorRole.Text, QtGui.QColor("#e6e8eb"))
    palette.setColor(QtGui.QPalette.ColorRole.Button, QtGui.QColor("#2a2d32"))
    palette.setColor(QtGui.QPalette.ColorRole.ButtonText, QtGui.QColor("#f4f6f8"))
    palette.setColor(QtGui.QPalette.ColorRole.BrightText, QtGui.QColor("#ff6f7d"))
    palette.setColor(QtGui.QPalette.ColorRole.Highlight, QtGui.QColor("#4d8f78"))
    palette.setColor(QtGui.QPalette.ColorRole.HighlightedText, QtGui.QColor("#07110d"))
    app.setPalette(palette)


def build_painter_host_preview_stylesheet() -> str:
    """Return generic host-control styles for the standalone preview only."""
    return """
QWidget {
    background: #111111;
    color: #e0e0e0;
}

QLabel {
    background: transparent;
    color: #e0e0e0;
}

QFrame, QGroupBox {
    background: #1b1b1b;
    border: 1px solid transparent;
    border-radius: 8px;
}

QFrame:hover, QGroupBox:hover {
    border-color: #414141;
}

QFrame#RizumDialogCard {
    background: #1b1b1b;
    border: 1px solid #414141;
    border-radius: 10px;
}

QFrame#RizumInsetSeparator {
    background: #414141;
    border: 0;
    max-height: 1px;
}

QLabel#RizumDialogTitle {
    color: #e0e0e0;
    font-size: 13px;
    font-weight: 600;
    background: transparent;
    border: 0;
}

QLabel#RizumDialogTitle:hover {
    background: transparent;
    border: 0;
}

QLabel#RizumFieldLabel {
    color: #9e9e9e;
    font-size: 13px;
    font-weight: 500;
    background: transparent;
    border: 0;
}

QLabel#RizumFieldLabel:hover {
    background: transparent;
    border: 0;
}

QPushButton {
    min-height: 32px;
    padding: 5px 18px;
    background: #343434;
    color: #e0e0e0;
    border: 1px solid transparent;
    border-radius: 16px;
}

QPushButton:hover {
    background: #3b3b3b;
    border-color: transparent;
}

QPushButton:pressed {
    background: #2b2b2b;
    border-color: transparent;
}

QPushButton[variant="icon"] {
    min-width: 26px;
    max-width: 26px;
    min-height: 26px;
    max-height: 26px;
    padding: 0;
    background: transparent;
    border: 1px solid transparent;
    border-radius: 4px;
}

QPushButton[variant="icon"]:hover {
    background: #303034;
}

QPushButton[variant="icon"]:pressed {
    background: #242426;
}

QPushButton[variant="dialog-secondary"] {
    min-height: 24px;
    max-height: 24px;
    padding: 0 18px;
    color: #e0e0e0;
    background: #343434;
    border: 1px solid transparent;
    border-radius: 13px;
    font-size: 12px;
    font-weight: 500;
}

QPushButton[variant="dialog-secondary"]:hover {
    background: #3b3b3b;
}

QPushButton[variant="dialog-secondary"]:pressed {
    background: #2b2b2b;
}

QPushButton[variant="dialog-primary"] {
    min-height: 24px;
    max-height: 24px;
    padding: 0 18px;
    color: #1b1b1b;
    background: #ffffff;
    border: 1px solid transparent;
    border-radius: 13px;
    font-size: 12px;
    font-weight: 600;
}

QPushButton[variant="dialog-primary"]:hover {
    background: #e0e0e0;
}

QPushButton[variant="dialog-primary"]:pressed {
    background: #b8b8b8;
}

QWidget#RizumActionRow {
    background: transparent;
}

QWidget#RizumTransparent {
    background: transparent;
}

QWidget#RizumInlineCheckbox {
    background: transparent;
    border-radius: 6px;
}

QLabel#RizumHintLabel {
    color: #9e9e9e;
    font-size: 11px;
    font-weight: 500;
    background: transparent;
    border: 0;
}

QPushButton[variant="icon"][compact="true"] {
    min-width: 22px;
    max-width: 22px;
    min-height: 22px;
    max-height: 22px;
}

QLabel#RizumHintLabel:hover {
    background: transparent;
    border: 0;
}

QWidget#RizumInlineCheckbox:hover {
    background: rgba(255, 255, 255, 13);
}

QFrame#RizumMockInput {
    background: transparent;
    border: 1px solid transparent;
    border-radius: 6px;
}

QFrame#RizumMockInput:hover {
    background: rgba(255, 255, 255, 13);
    border-color: transparent;
}

QLabel#RizumMockText {
    color: #e0e0e0;
    font-size: 13px;
    background: transparent;
    border: 0;
}

QLabel#RizumMockText:hover {
    background: transparent;
    border: 0;
}

QWidget#RizumMockIcon, QWidget#RizumMockIcon:hover,
QWidget#RizumChevronIcon, QWidget#RizumChevronIcon:hover,
QLabel#RizumSvgLabel, QLabel#RizumSvgLabel:hover {
    background: transparent;
    border: 0;
}

QFrame#RizumCollapsibleGroup {
    background: transparent;
    border: 0;
    border-radius: 8px;
}

QFrame#RizumCollapsibleGroup:hover {
    background: rgba(255, 255, 255, 10);
    border: 0;
}

QFrame#RizumCollapsibleHeader,
QFrame#RizumCollapsibleContent,
QWidget#RizumCollapsibleContentInner,
QWidget#RizumCollapsibleChevron {
    background: transparent;
    border: 0;
}

QFrame#RizumCollapsibleHeader:hover {
    background: transparent;
    border: 0;
}

QLabel#RizumCollapsibleTitle {
    color: #e0e0e0;
    font-size: 13px;
    font-weight: 600;
    background: transparent;
    border: 0;
}

QLabel#RizumCollapsibleSubtitle {
    color: #666666;
    font-size: 11px;
    font-weight: 500;
    background: transparent;
    border: 0;
}

QLabel#RizumCollapsibleTitle:hover,
QLabel#RizumCollapsibleSubtitle:hover {
    background: transparent;
    border: 0;
}

QFrame#RizumMockCheckbox {
    background: transparent;
    border: 1.5px solid #ffffff;
    border-radius: 3px;
}

QFrame#RizumMockCheckbox[checked="true"] {
    background: #ffffff;
    border: 1.5px solid #ffffff;
}

QFrame#RizumMockCheckbox[checked="false"] {
    background: transparent;
    border: 1.5px solid #ffffff;
}

QMenu#RizumPopupMenu {
    background: #1b1b1b;
    color: #e0e0e0;
    border: 1px solid #414141;
    border-radius: 6px;
    padding: 4px;
    font-size: 12px;
}

QMenu#RizumPopupMenu::item {
    padding: 6px 22px 6px 8px;
    border-radius: 4px;
}

QMenu#RizumPopupMenu::item:selected {
    background: rgba(255, 255, 255, 13);
    color: #e0e0e0;
}

QComboBox, QLineEdit, QSpinBox, QDoubleSpinBox, QTextEdit, QPlainTextEdit {
    min-height: 32px;
    padding: 4px 10px;
    background: #222222;
    color: #e0e0e0;
    border: 1px solid transparent;
    border-radius: 6px;
    selection-background-color: #a0686a;
    selection-color: #ffffff;
}

QComboBox:hover, QLineEdit:hover, QSpinBox:hover, QDoubleSpinBox:hover {
    border-color: #5a5a5a;
}

QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
    width: 20px;
    background: transparent;
    border: 0;
}

QComboBox::drop-down {
    width: 22px;
    border: 0;
}

QComboBox QAbstractItemView {
    background: #222222;
    color: #e0e0e0;
    border: 1px solid #414141;
    selection-background-color: #343434;
    selection-color: #ffffff;
}

QTreeWidget, QListWidget, QTableWidget {
    background: #222222;
    color: #e0e0e0;
    border: 1px solid transparent;
    alternate-background-color: #1f1f1f;
    selection-background-color: rgba(255, 255, 255, 20);
    selection-color: #ffffff;
}

QTreeWidget::item, QListWidget::item {
    min-height: 30px;
    padding: 4px 10px;
}

QTreeWidget:hover, QListWidget:hover, QTableWidget:hover {
    border-color: #414141;
}

QCheckBox {
    background: transparent;
    color: #e0e0e0;
    spacing: 10px;
}

QCheckBox::indicator {
    width: 20px;
    height: 20px;
    border-radius: 6px;
    border: 0;
    background: #343434;
}

QCheckBox::indicator:checked {
    background: #ffffff;
}

QCheckBox::indicator:hover {
    background: #454545;
}

QProgressBar {
    min-height: 20px;
    background: #222222;
    border: 1px solid #414141;
    color: #ffffff;
    text-align: center;
}

QProgressBar::chunk {
    background: #1473e6;
}
"""


def capture_app_palette(app):
    """Return a serializable snapshot of the current QApplication palette."""
    from PySide6 import QtGui

    palette = app.palette()
    values = {}
    for role_name in PALETTE_ROLES:
        role = getattr(QtGui.QPalette.ColorRole, role_name)
        values[role_name] = palette.color(role).name()
    return values


def save_app_palette(app, path):
    """Write the current QApplication palette snapshot to disk."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "palette": capture_app_palette(app),
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def apply_palette_file(app, path):
    """Apply a palette JSON exported from the Painter preview plugin."""
    from PySide6 import QtGui, QtWidgets

    path = Path(path)
    if not path.exists():
        return False

    payload = json.loads(path.read_text(encoding="utf-8"))
    values = payload.get("palette") or {}
    if not values:
        return False
    if not _looks_dark(values):
        return False

    app.setStyle(QtWidgets.QStyleFactory.create("Fusion"))
    palette = app.palette()
    for role_name, color_value in values.items():
        role = getattr(QtGui.QPalette.ColorRole, role_name, None)
        if role is None:
            continue
        palette.setColor(role, QtGui.QColor(color_value))
    app.setPalette(palette)
    return True


def _looks_dark(values):
    candidates = [
        values.get("Window"),
        values.get("Base"),
        values.get("Button"),
    ]
    colors = [value for value in candidates if value]
    if not colors:
        return False
    return sum(_luminance(value) for value in colors) / len(colors) < 145


def _luminance(hex_color):
    value = hex_color.lstrip("#")
    if len(value) != 6:
        return 255
    red = int(value[0:2], 16)
    green = int(value[2:4], 16)
    blue = int(value[4:6], 16)
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue
