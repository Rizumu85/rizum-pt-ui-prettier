"""Reusable PySide6 widgets for Rizum Painter plugins."""

from __future__ import annotations


class Card:
    """Factory for a compact framed surface."""

    @staticmethod
    def create(parent=None):
        from PySide6 import QtWidgets

        frame = QtWidgets.QFrame(parent)
        frame.setObjectName("RizumCard")
        layout = QtWidgets.QVBoxLayout(frame)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        return frame


class FieldLabel:
    """Factory for compact form labels."""

    @staticmethod
    def create(text, parent=None):
        from PySide6 import QtWidgets

        label = QtWidgets.QLabel(text, parent)
        label.setObjectName("RizumFieldLabel")
        return label


class SectionHeader:
    """A title/subtitle pair for dense plugin panels."""

    def __new__(cls, title, subtitle="", parent=None):
        from PySide6 import QtWidgets

        widget = QtWidgets.QWidget(parent)
        widget.setObjectName("RizumSectionHeader")
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet("font-weight: 700; font-size: 12pt;")
        layout.addWidget(title_label)

        if subtitle:
            subtitle_label = QtWidgets.QLabel(subtitle)
            subtitle_label.setProperty("muted", True)
            subtitle_label.setWordWrap(True)
            layout.addWidget(subtitle_label)

        return widget


class ActionButton:
    """Primary or secondary button factory."""

    @staticmethod
    def create(text, variant="secondary", parent=None):
        from PySide6 import QtWidgets

        button = QtWidgets.QPushButton(text, parent)
        if variant != "secondary":
            button.setProperty("variant", variant)
        return button


class PillButton:
    """Compact rounded button for secondary toolbar actions."""

    @staticmethod
    def create(text, parent=None):
        from PySide6 import QtWidgets

        button = QtWidgets.QPushButton(text, parent)
        button.setProperty("variant", "ghost")
        button.setMinimumWidth(34)
        return button


class StatusPill:
    """Small colored status label."""

    def __new__(cls, text, tone="neutral", parent=None):
        from PySide6 import QtWidgets

        label = QtWidgets.QLabel(text, parent)
        label.setObjectName("RizumStatusPill")
        colors = {
            "good": ("#12372b", "#54d6a2"),
            "info": ("#172c4a", "#6aa8ff"),
            "warn": ("#3d2d12", "#f2b85b"),
            "bad": ("#421b22", "#ff6f7d"),
            "neutral": ("#272b31", "#b3bac4"),
        }
        bg, fg = colors.get(tone, colors["neutral"])
        label.setStyleSheet(
            f"background: {bg}; color: {fg}; border-radius: 7px; padding: 3px 8px;"
        )
        return label


def make_action_row(*buttons, parent=None):
    """Create a right-aligned action row."""
    from PySide6 import QtWidgets

    widget = QtWidgets.QWidget(parent)
    layout = QtWidgets.QHBoxLayout(widget)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(8)
    layout.addStretch(1)
    for button in buttons:
        layout.addWidget(button)
    return widget
