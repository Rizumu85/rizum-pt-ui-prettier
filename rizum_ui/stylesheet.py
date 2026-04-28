"""Qt stylesheet generation and application helpers."""

from __future__ import annotations

from .theme import Theme, default_theme


def build_stylesheet(theme: Theme = default_theme) -> str:
    """Return a Painter-friendly Qt stylesheet."""
    radius = theme.radius
    radius_small = theme.radius_small
    return f"""
QWidget {{
    background: {theme.bg};
    color: {theme.text};
    font-family: "{theme.font_family}", "Segoe UI", sans-serif;
    font-size: {theme.font_size}pt;
    selection-background-color: {theme.accent};
    selection-color: #101214;
}}

QDialog, QWidget#RizumSurface {{
    background: {theme.bg};
}}

QFrame#RizumCard {{
    background: {theme.surface};
    border: 1px solid {theme.border_soft};
    border-radius: {radius}px;
}}

QLabel {{
    color: {theme.text};
    background: transparent;
}}

QLabel[muted="true"] {{
    color: {theme.text_muted};
}}

QLabel#RizumFieldLabel {{
    color: {theme.text_muted};
    font-size: {max(theme.font_size - 1, 8)}pt;
}}

QPushButton {{
    min-height: 28px;
    padding: 4px 12px;
    border: 1px solid {theme.border};
    border-radius: {radius}px;
    background: {theme.surface_raised};
    color: {theme.text};
}}

QPushButton:hover {{
    border-color: {theme.accent};
    background: #30343a;
}}

QPushButton:pressed {{
    background: #25282d;
    padding-top: 5px;
    padding-bottom: 3px;
}}

QPushButton:disabled {{
    color: {theme.text_faint};
    background: #202226;
    border-color: {theme.border_soft};
}}

QPushButton[variant="primary"] {{
    color: #07110d;
    background: {theme.accent};
    border-color: {theme.accent};
    font-weight: 600;
}}

QPushButton[variant="primary"]:hover {{
    background: {theme.accent_hover};
    border-color: {theme.accent_hover};
}}

QPushButton[variant="primary"]:pressed {{
    background: {theme.accent_pressed};
    border-color: {theme.accent_pressed};
}}

QPushButton[variant="ghost"] {{
    background: transparent;
    border-color: transparent;
}}

QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit, QPlainTextEdit {{
    min-height: 28px;
    padding: 3px 8px;
    border: 1px solid {theme.border_soft};
    border-radius: {radius_small}px;
    background: {theme.surface_sunken};
    color: {theme.text};
}}

QLineEdit:hover, QComboBox:hover, QSpinBox:hover, QDoubleSpinBox:hover {{
    border-color: {theme.border};
}}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
    border-color: {theme.accent};
}}

QComboBox::drop-down {{
    width: 22px;
    border: 0;
}}

QCheckBox {{
    spacing: 8px;
    color: {theme.text_muted};
    background: transparent;
}}

QCheckBox::indicator {{
    width: 15px;
    height: 15px;
    border-radius: 4px;
    border: 1px solid {theme.border};
    background: {theme.surface_sunken};
}}

QCheckBox::indicator:checked {{
    border-color: {theme.accent};
    background: {theme.accent};
}}

QTreeWidget, QListWidget, QTableWidget {{
    background: {theme.surface_sunken};
    border: 1px solid {theme.border_soft};
    border-radius: {radius}px;
    alternate-background-color: #191b1f;
}}

QTreeWidget::item, QListWidget::item {{
    min-height: 26px;
    padding: 3px 6px;
    border-radius: {radius_small}px;
}}

QTreeWidget::item:selected, QListWidget::item:selected {{
    color: {theme.text};
    background: #284039;
}}

QProgressBar {{
    min-height: 8px;
    border: 0;
    border-radius: 4px;
    background: {theme.surface_sunken};
    text-align: center;
}}

QProgressBar::chunk {{
    border-radius: 4px;
    background: {theme.accent};
}}

QScrollBar:vertical, QScrollBar:horizontal {{
    background: transparent;
    border: 0;
    width: 10px;
    height: 10px;
}}

QScrollBar::handle {{
    background: #3c424a;
    border-radius: 5px;
    min-height: 24px;
}}

QScrollBar::handle:hover {{
    background: #4a525d;
}}

QToolTip {{
    color: {theme.text};
    background: {theme.surface_raised};
    border: 1px solid {theme.border};
    border-radius: {radius_small}px;
    padding: 5px 7px;
}}
"""


def apply_theme(widget_or_app, theme: Theme = default_theme) -> str:
    """Apply the generated stylesheet and return it for debugging."""
    stylesheet = build_stylesheet(theme)
    widget_or_app.setStyleSheet(stylesheet)
    return stylesheet
