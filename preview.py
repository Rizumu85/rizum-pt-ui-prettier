"""Standalone preview for the Rizum PySide6 UI kit."""

from __future__ import annotations

import sys

from rizum_ui import (
    ActionButton,
    Card,
    FieldLabel,
    SectionHeader,
    StatusPill,
    apply_theme,
    make_action_row,
)
from rizum_ui.animation import fade_in


def build_bridge_preview(QtWidgets):
    card = Card.create()
    layout = card.layout()
    layout.addWidget(
        SectionHeader(
            "PT Bridge",
            "Export Painter texture stacks into bridge-ready Photoshop payloads.",
        )
    )

    scope_row = QtWidgets.QHBoxLayout()
    scope_row.addWidget(FieldLabel.create("Scope"))
    scope = QtWidgets.QComboBox()
    scope.addItems(["Current Stack", "All Stacks", "Selected Channels"])
    scope_row.addWidget(scope, 1)
    scope_row.addWidget(StatusPill("Ready", "good"))
    layout.addLayout(scope_row)

    target_list = QtWidgets.QTreeWidget()
    target_list.setHeaderHidden(True)
    for target, channels in {
        "Body / BaseColor / 3 channels": ["Base Color", "Roughness", "Normal"],
        "Hair / User2 / 2 channels": ["Mask", "Opacity"],
    }.items():
        item = QtWidgets.QTreeWidgetItem([target])
        target_list.addTopLevelItem(item)
        for channel in channels:
            item.addChild(QtWidgets.QTreeWidgetItem([channel]))
        item.setExpanded(True)
    layout.addWidget(target_list, 1)

    export_pngs = QtWidgets.QCheckBox("Export PNGs")
    export_pngs.setChecked(True)
    layout.addWidget(export_pngs)

    layout.addWidget(
        make_action_row(
            ActionButton.create("Settings", "ghost"),
            ActionButton.create("Export", "primary"),
        )
    )
    return card


def build_font_preview(QtWidgets):
    card = Card.create()
    layout = card.layout()
    layout.addWidget(
        SectionHeader(
            "UI Font",
            "Tune Painter font size and family for this session.",
        )
    )

    form = QtWidgets.QFormLayout()

    scale = QtWidgets.QDoubleSpinBox()
    scale.setRange(0.75, 2.0)
    scale.setValue(1.05)
    scale.setSingleStep(0.05)
    form.addRow(FieldLabel.create("Size"), scale)

    font = QtWidgets.QComboBox()
    font.addItems(["System Default", "MiSans", "Inter", "Segoe UI"])
    form.addRow(FieldLabel.create("Font"), font)

    no_hinting = QtWidgets.QCheckBox("No hinting")
    no_hinting.setChecked(True)
    form.addRow(FieldLabel.create("Render"), no_hinting)
    layout.addLayout(form)

    layout.addWidget(
        make_action_row(
            ActionButton.create("Reset"),
            ActionButton.create("Apply", "primary"),
        )
    )
    layout.addStretch(1)
    return card


def build_lab(QtWidgets):
    card = Card.create()
    layout = card.layout()
    layout.addWidget(SectionHeader("Component Lab", "Quick controls for visual tuning."))

    text = QtWidgets.QLineEdit()
    text.setPlaceholderText("Output folder")
    layout.addWidget(text)

    progress = QtWidgets.QProgressBar()
    progress.setRange(0, 100)
    progress.setValue(62)
    layout.addWidget(progress)

    output = QtWidgets.QPlainTextEdit()
    output.setPlainText("Preview changes here before copying them into Painter.")
    output.setMinimumHeight(90)
    layout.addWidget(output)

    row = QtWidgets.QHBoxLayout()
    row.addWidget(StatusPill("Synced", "good"))
    row.addWidget(StatusPill("Preview", "info"))
    row.addWidget(StatusPill("Needs SP reload", "warn"))
    row.addStretch(1)
    layout.addLayout(row)
    return card


def main():
    from PySide6 import QtWidgets

    app = QtWidgets.QApplication(sys.argv)
    apply_theme(app)

    window = QtWidgets.QWidget()
    window.setObjectName("RizumSurface")
    window.setWindowTitle("Rizum UI Prettier Preview")
    window.resize(980, 620)

    layout = QtWidgets.QVBoxLayout(window)
    layout.setContentsMargins(16, 16, 16, 16)
    layout.setSpacing(12)

    header = SectionHeader(
        "Rizum UI Prettier",
        "Shared PySide6 components for Substance 3D Painter plugins.",
    )
    layout.addWidget(header)

    grid = QtWidgets.QGridLayout()
    grid.setSpacing(12)
    grid.addWidget(build_bridge_preview(QtWidgets), 0, 0, 2, 1)
    grid.addWidget(build_font_preview(QtWidgets), 0, 1)
    grid.addWidget(build_lab(QtWidgets), 1, 1)
    grid.setColumnStretch(0, 3)
    grid.setColumnStretch(1, 2)
    layout.addLayout(grid, 1)

    fade_in(window, duration=220)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
