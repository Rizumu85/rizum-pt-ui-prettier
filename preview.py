"""Standalone preview for the Rizum PySide6 UI kit."""

from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path

from rizum_ui import (
    ActionButton,
    Card,
    FieldLabel,
    SectionHeader,
    StatusPill,
    apply_palette_file,
    apply_painter_like_base,
    build_painter_host_preview_stylesheet,
    build_stylesheet,
    make_action_row,
    make_field_row,
    make_icon_button,
    make_inset_separator,
    make_mock_checkbox,
    make_mock_input,
    make_svg_label,
)
from rizum_ui.animation import fade_in

ROOT = Path(__file__).resolve().parent
PREVIEW_FILE = Path(__file__).resolve()
WATCHED_MODULES = [
    "rizum_ui.theme",
    "rizum_ui.host_style",
    "rizum_ui.stylesheet",
    "rizum_ui.components",
    "rizum_ui.animation",
    "rizum_ui",
]
WATCHED_FILES = sorted(
    [PREVIEW_FILE]
    + list((ROOT / "rizum_ui").glob("*.py"))
    + list((ROOT / "icons").glob("*.svg"))
)
PREVIEW_FLAGS = {"--full", "--no-watch", "--scale-1x"}


def configure_preview_scaling():
    """Disable Qt high-DPI scaling for external visual comparison only."""
    if "--scale-1x" not in sys.argv:
        return
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "0"
    os.environ["QT_SCALE_FACTOR"] = "1"
    os.environ["QT_FONT_DPI"] = "96"


def qt_argv():
    """Return argv without preview-only flags so Qt does not consume them."""
    return [arg for arg in sys.argv if arg not in PREVIEW_FLAGS]


def reload_ui_kit():
    """Reload UI-kit modules and refresh imported helpers."""
    global ActionButton
    global Card
    global FieldLabel
    global SectionHeader
    global StatusPill
    global apply_painter_like_base
    global apply_palette_file
    global build_painter_host_preview_stylesheet
    global build_stylesheet
    global make_action_row
    global make_field_row
    global make_icon_button
    global make_inset_separator
    global make_mock_checkbox
    global make_mock_input
    global make_svg_label
    global fade_in

    for module_name in WATCHED_MODULES:
        module = importlib.import_module(module_name)
        importlib.reload(module)

    import rizum_ui
    import rizum_ui.animation

    ActionButton = rizum_ui.ActionButton
    Card = rizum_ui.Card
    FieldLabel = rizum_ui.FieldLabel
    SectionHeader = rizum_ui.SectionHeader
    StatusPill = rizum_ui.StatusPill
    apply_painter_like_base = rizum_ui.apply_painter_like_base
    apply_palette_file = rizum_ui.apply_palette_file
    build_painter_host_preview_stylesheet = rizum_ui.build_painter_host_preview_stylesheet
    build_stylesheet = rizum_ui.build_stylesheet
    make_action_row = rizum_ui.make_action_row
    make_field_row = rizum_ui.make_field_row
    make_icon_button = rizum_ui.make_icon_button
    make_inset_separator = rizum_ui.make_inset_separator
    make_mock_checkbox = rizum_ui.make_mock_checkbox
    make_mock_input = rizum_ui.make_mock_input
    make_svg_label = rizum_ui.make_svg_label
    fade_in = rizum_ui.animation.fade_in


def snapshot_mtimes():
    return {
        path: path.stat().st_mtime_ns
        for path in WATCHED_FILES
        if path.exists()
    }


def restart_preview(app):
    """Start a fresh preview process so edits to preview.py take effect."""
    from PySide6 import QtCore

    args = [str(PREVIEW_FILE), *sys.argv[1:]]
    QtCore.QProcess.startDetached(sys.executable, args, str(ROOT))
    app.quit()


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
    from PySide6 import QtCore
    from PySide6 import QtWidgets as _QtWidgets

    card = Card.create()
    card.setObjectName("RizumDialogCard")
    card.setFixedHeight(232)
    card.resize(358, 232)
    card.setSizePolicy(
        _QtWidgets.QSizePolicy.Policy.Expanding,
        _QtWidgets.QSizePolicy.Policy.Fixed,
    )
    layout = card.layout()
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)

    header_widget = QtWidgets.QWidget()
    header_widget.setFixedHeight(40)
    header_widget.setObjectName("RizumTransparent")
    header_outer = QtWidgets.QVBoxLayout(header_widget)
    header_outer.setContentsMargins(0, 0, 0, 0)
    header_outer.setSpacing(0)
    header_row = QtWidgets.QWidget()
    header_row.setObjectName("RizumTransparent")
    header_row.setFixedHeight(39)
    header_layout = QtWidgets.QHBoxLayout(header_row)
    header_layout.setContentsMargins(16, 0, 16, 0)
    header_layout.setSpacing(0)
    title = QtWidgets.QLabel("UI Font")
    title.setObjectName("RizumDialogTitle")
    header_layout.addWidget(title)
    header_layout.addStretch(1)
    close_icon = make_svg_label("x.svg", 14)
    header_layout.addWidget(close_icon)
    header_outer.addWidget(header_row)
    header_outer.addWidget(make_inset_separator(12))
    layout.addWidget(header_widget)

    main_widget = QtWidgets.QWidget()
    main_widget.setObjectName("RizumTransparent")
    main_layout = QtWidgets.QVBoxLayout(main_widget)
    main_layout.setContentsMargins(16, 16, 16, 16)
    main_layout.setSpacing(12)

    size_control = make_mock_input("1.00", mode="spin")
    main_layout.addWidget(make_field_row("Size", size_control, label_width=32, gap=12, width=88))

    font = make_mock_input("System Default", mode="combo")
    main_layout.addWidget(make_field_row("Font", font, label_width=32, gap=12))

    tool_row = QtWidgets.QHBoxLayout()
    tool_row.setContentsMargins(44, -6, 4, 2)
    tool_row.setSpacing(0)
    icon_group = QtWidgets.QHBoxLayout()
    icon_group.setContentsMargins(0, 0, 0, 0)
    icon_group.setSpacing(4)
    folder_button = make_icon_button("folder.svg", "Open fonts folder")
    refresh_button = make_icon_button("refresh.svg", "Refresh font list")
    icon_group.addWidget(folder_button)
    icon_group.addWidget(refresh_button)
    tool_row.addLayout(icon_group)
    tool_row.addStretch(1)
    hint_widget = QtWidgets.QWidget()
    hint_widget.setObjectName("RizumInlineCheckbox")
    hint_layout = QtWidgets.QHBoxLayout(hint_widget)
    hint_layout.setContentsMargins(6, 3, 6, 3)
    hint_layout.setSpacing(6)
    no_hinting_label = QtWidgets.QLabel("No hinting")
    no_hinting_label.setObjectName("RizumHintLabel")
    hint_layout.addWidget(no_hinting_label)
    no_hinting = make_mock_checkbox()
    hint_layout.addWidget(no_hinting)
    hint_widget.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
    hint_widget.mousePressEvent = (
        lambda event: no_hinting.toggle()
        if event.button() == QtCore.Qt.MouseButton.LeftButton
        else None
    )
    tool_row.addWidget(hint_widget)
    main_layout.addLayout(tool_row)

    layout.addWidget(main_widget)
    layout.addStretch(1)

    footer_widget = QtWidgets.QWidget()
    footer_widget.setObjectName("RizumTransparent")
    footer_widget.setFixedHeight(48)
    footer_outer = QtWidgets.QVBoxLayout(footer_widget)
    footer_outer.setContentsMargins(0, 0, 0, 0)
    footer_outer.setSpacing(0)
    footer_outer.addWidget(make_inset_separator(12))
    footer_row = QtWidgets.QWidget()
    footer_row.setObjectName("RizumTransparent")
    footer_layout = QtWidgets.QHBoxLayout(footer_row)
    footer_layout.setContentsMargins(16, 0, 16, 0)
    footer_layout.setSpacing(8)
    reset_button = ActionButton.create("Reset", "dialog-secondary")
    reset_button.setFixedSize(67, 26)
    apply_button = ActionButton.create("Apply", "dialog-primary")
    apply_button.setFixedSize(69, 26)
    footer_layout.addStretch(1)
    footer_layout.addWidget(reset_button)
    footer_layout.addWidget(apply_button)
    footer_outer.addWidget(footer_row, 1)
    layout.addWidget(footer_widget)
    card.setMinimumWidth(max(218, card.minimumSizeHint().width()))
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


def clear_layout(layout):
    while layout.count():
        item = layout.takeAt(0)
        child_layout = item.layout()
        widget = item.widget()
        if child_layout is not None:
            clear_layout(child_layout)
        if widget is not None:
            widget.deleteLater()


def build_preview(window, QtWidgets, watch_enabled):
    layout = window.layout()
    if layout is None:
        layout = QtWidgets.QVBoxLayout(window)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
    else:
        clear_layout(layout)

    title_row = QtWidgets.QHBoxLayout()
    title_row.addWidget(
        SectionHeader(
            "Rizum UI Prettier",
            "Shared PySide6 components for Substance 3D Painter plugins.",
        ),
        1,
    )

    reload_button = ActionButton.create("Reload", "ghost")
    title_row.addWidget(reload_button)
    watch_label = StatusPill("Watching", "good") if watch_enabled else StatusPill("Manual", "warn")
    title_row.addWidget(watch_label)
    layout.addLayout(title_row)

    grid = QtWidgets.QGridLayout()
    grid.setSpacing(12)
    grid.addWidget(build_bridge_preview(QtWidgets), 0, 0, 2, 1)
    grid.addWidget(build_font_preview(QtWidgets), 0, 1)
    grid.addWidget(build_lab(QtWidgets), 1, 1)
    grid.setColumnStretch(0, 3)
    grid.setColumnStretch(1, 2)
    layout.addLayout(grid, 1)

    return reload_button


def main():
    configure_preview_scaling()
    from PySide6 import QtCore, QtWidgets

    app = QtWidgets.QApplication(qt_argv())
    full_mode = "--full" in sys.argv
    watch_enabled = "--no-watch" not in sys.argv
    palette_path = ROOT / "preview-host-palette.json"
    if not apply_palette_file(app, palette_path):
        apply_painter_like_base(app)
    app.setStyleSheet(
        build_painter_host_preview_stylesheet()
        + build_stylesheet(mode="full" if full_mode else "overlay")
    )

    window = QtWidgets.QWidget()
    window.setObjectName("RizumSurface")
    mode_label = "Full Override" if full_mode else "Painter-like Overlay"
    window.setWindowTitle(f"Rizum UI Prettier Preview - {mode_label}")
    window.resize(980, 620)

    mtimes = snapshot_mtimes()
    preview_mtime = mtimes.get(PREVIEW_FILE)

    def refresh_preview():
        nonlocal mtimes
        next_mtimes = snapshot_mtimes()
        if next_mtimes.get(PREVIEW_FILE) != preview_mtime:
            restart_preview(app)
            return
        reload_ui_kit()
        if not apply_palette_file(app, palette_path):
            apply_painter_like_base(app)
        app.setStyleSheet(
            build_painter_host_preview_stylesheet()
            + build_stylesheet(mode="full" if full_mode else "overlay")
        )
        reload_button = build_preview(window, QtWidgets, watch_enabled)
        reload_button.clicked.connect(refresh_preview)
        mtimes = snapshot_mtimes()

    reload_button = build_preview(window, QtWidgets, watch_enabled)
    reload_button.clicked.connect(refresh_preview)

    if watch_enabled:
        timer = QtCore.QTimer(window)
        timer.setInterval(500)

        def poll_changes():
            nonlocal mtimes
            next_mtimes = snapshot_mtimes()
            if next_mtimes != mtimes:
                if next_mtimes.get(PREVIEW_FILE) != preview_mtime:
                    restart_preview(app)
                else:
                    refresh_preview()

        timer.timeout.connect(poll_changes)
        timer.start()
        window._rizum_watch_timer = timer

    fade_in(window, duration=220)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
