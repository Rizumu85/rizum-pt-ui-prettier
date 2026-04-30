"""Standalone preview for the Rizum PySide6 UI kit."""

from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path

from rizum_ui import (
    ActionButton,
    Card,
    SectionHeader,
    StatusPill,
    COMPACT_DOCK_DEFAULT_HEIGHT,
    COMPACT_DOCK_DEFAULT_WIDTH,
    COMPACT_DOCK_MIN_WIDTH,
    apply_palette_file,
    apply_compact_dock_surface,
    apply_painter_like_base,
    build_painter_host_preview_stylesheet,
    build_stylesheet,
    compact_footer_button_width,
    compact_label_width,
    compact_text_width,
    make_compact_dock_card,
    make_compact_dock_layout,
    make_combo_input,
    make_collapsible_group,
    make_field_row,
    make_icon_button,
    make_inset_separator,
    make_inline_checkbox_row,
    make_mock_checkbox,
    make_spin_input,
    make_svg_label,
    set_compact_footer_button_width,
    update_compact_field_row,
    update_inline_checkbox_row,
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
    global SectionHeader
    global StatusPill
    global COMPACT_DOCK_DEFAULT_HEIGHT
    global COMPACT_DOCK_DEFAULT_WIDTH
    global COMPACT_DOCK_MIN_WIDTH
    global apply_compact_dock_surface
    global apply_painter_like_base
    global apply_palette_file
    global build_painter_host_preview_stylesheet
    global build_stylesheet
    global compact_footer_button_width
    global compact_label_width
    global compact_text_width
    global make_compact_dock_card
    global make_compact_dock_layout
    global make_combo_input
    global make_collapsible_group
    global make_field_row
    global make_icon_button
    global make_inset_separator
    global make_inline_checkbox_row
    global make_mock_checkbox
    global make_spin_input
    global make_svg_label
    global set_compact_footer_button_width
    global update_compact_field_row
    global update_inline_checkbox_row
    global fade_in

    for module_name in WATCHED_MODULES:
        module = importlib.import_module(module_name)
        importlib.reload(module)

    import rizum_ui
    import rizum_ui.animation

    ActionButton = rizum_ui.ActionButton
    Card = rizum_ui.Card
    SectionHeader = rizum_ui.SectionHeader
    StatusPill = rizum_ui.StatusPill
    COMPACT_DOCK_DEFAULT_HEIGHT = rizum_ui.COMPACT_DOCK_DEFAULT_HEIGHT
    COMPACT_DOCK_DEFAULT_WIDTH = rizum_ui.COMPACT_DOCK_DEFAULT_WIDTH
    COMPACT_DOCK_MIN_WIDTH = rizum_ui.COMPACT_DOCK_MIN_WIDTH
    apply_compact_dock_surface = rizum_ui.apply_compact_dock_surface
    apply_painter_like_base = rizum_ui.apply_painter_like_base
    apply_palette_file = rizum_ui.apply_palette_file
    build_painter_host_preview_stylesheet = rizum_ui.build_painter_host_preview_stylesheet
    build_stylesheet = rizum_ui.build_stylesheet
    compact_footer_button_width = rizum_ui.compact_footer_button_width
    compact_label_width = rizum_ui.compact_label_width
    compact_text_width = rizum_ui.compact_text_width
    make_compact_dock_card = rizum_ui.make_compact_dock_card
    make_compact_dock_layout = rizum_ui.make_compact_dock_layout
    make_combo_input = rizum_ui.make_combo_input
    make_collapsible_group = rizum_ui.make_collapsible_group
    make_field_row = rizum_ui.make_field_row
    make_icon_button = rizum_ui.make_icon_button
    make_inset_separator = rizum_ui.make_inset_separator
    make_inline_checkbox_row = rizum_ui.make_inline_checkbox_row
    make_mock_checkbox = rizum_ui.make_mock_checkbox
    make_spin_input = rizum_ui.make_spin_input
    make_svg_label = rizum_ui.make_svg_label
    set_compact_footer_button_width = rizum_ui.set_compact_footer_button_width
    update_compact_field_row = rizum_ui.update_compact_field_row
    update_inline_checkbox_row = rizum_ui.update_inline_checkbox_row
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
    from PySide6 import QtCore, QtGui

    window = QtWidgets.QFrame()
    window.setObjectName("RizumExportWindow")
    window.setFixedSize(284, 263)
    window.setSizePolicy(
        QtWidgets.QSizePolicy.Policy.Fixed,
        QtWidgets.QSizePolicy.Policy.Fixed,
    )
    export_family = "Segoe UI"
    font_path = ROOT.parent / "rizum-pt-ui-font" / "fonts" / "MiSans-Regular.ttf"
    if font_path.exists():
        font_id = QtGui.QFontDatabase.addApplicationFont(str(font_path))
        families = QtGui.QFontDatabase.applicationFontFamilies(font_id) if font_id >= 0 else []
        if families:
            export_family = families[0]
    window.setFont(QtGui.QFont(export_family, 9))
    window.setStyleSheet(
        """
QFrame#RizumExportWindow {
    background: #1b1b1b;
    border: 1px solid #414141;
    border-radius: 10px;
    font-family: "__EXPORT_FAMILY__", "Segoe UI", Arial, sans-serif;
}
QFrame#RizumExportHeader,
QFrame#RizumExportTopControls,
QFrame#RizumExportFooter {
    background: transparent;
    border: 0;
}
QLabel#RizumExportTitle {
    color: #e0e0e0;
    font-size: 10pt;
    font-weight: bold;
    background: transparent;
    border: 0;
}
QFrame#RizumExportWindow QLabel:hover {
    background: transparent;
    border: 0;
}
QFrame#RizumExportWindow QLabel#RizumMockText {
    font-size: 9pt;
    font-weight: bold;
    background: transparent;
    border: 0;
}
QLabel#RizumExportItemName {
    color: #e0e0e0;
    font-size: 9pt;
    font-weight: bold;
    background: transparent;
    border: 0;
}
QFrame#RizumExportWindow QLabel#RizumCollapsibleTitle {
    color: #e0e0e0;
    font-size: 9pt;
    font-weight: bold;
    background: transparent;
    border: 0;
}
QFrame#RizumExportWindow QLabel#RizumCollapsibleSubtitle {
    color: #666666;
    font-size: 8pt;
    font-weight: 500;
    background: transparent;
    border: 0;
}
QLabel#RizumExportMeta {
    color: #666666;
    font-size: 8pt;
    font-weight: 500;
    background: transparent;
    border: 0;
}
QFrame#RizumExportTree {
    background: transparent;
    border: 0;
}
QFrame#RizumExportGroup {
    background: transparent;
    border: 0;
    border-radius: 8px;
}
QFrame#RizumExportGroup:hover {
    background: rgba(255, 255, 255, 0.04);
    border: 0;
}
QFrame#RizumExportTreeItem {
    background: transparent;
    border: 0;
    border-radius: 6px;
}
QFrame#RizumExportTreeItemHost {
    background: transparent;
    border: 0;
}
QFrame#RizumExportTreeItem[child="true"]:hover {
    background: rgba(255, 255, 255, 0.06);
    border: 0;
}
QFrame#RizumExportTreeItem[child="false"]:hover {
    background: transparent;
    border: 0;
}
QFrame#RizumExportWindow QLabel#RizumSvgLabel,
QFrame#RizumExportWindow QLabel#RizumSvgLabel:hover {
    background: transparent;
    border: 0;
}
QFrame#RizumExportWindow QPushButton[variant="dialog-secondary"],
QFrame#RizumExportWindow QPushButton[variant="dialog-primary"] {
    font-weight: bold;
}
""".replace("__EXPORT_FAMILY__", export_family.replace('"', '\\"'))
    )

    layout = QtWidgets.QVBoxLayout(window)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)

    header = QtWidgets.QFrame()
    header.setObjectName("RizumExportHeader")
    header.setFixedHeight(40)
    header_layout = QtWidgets.QHBoxLayout(header)
    header_layout.setContentsMargins(16, 0, 16, 0)
    header_layout.setSpacing(0)
    title = QtWidgets.QLabel("Export")
    title.setObjectName("RizumExportTitle")
    header_layout.addWidget(title)
    header_layout.addStretch(1)
    header_layout.addWidget(make_svg_label("x.svg", 14))
    layout.addWidget(header)
    layout.addWidget(make_inset_separator(12, thickness=1))

    top_controls = QtWidgets.QFrame()
    top_controls.setObjectName("RizumExportTopControls")
    top_controls.setFixedHeight(40)
    top_layout = QtWidgets.QHBoxLayout(top_controls)
    top_layout.setContentsMargins(16, 0, 16, 0)
    top_layout.setSpacing(12)
    mode_combo = make_combo_input(["All Sets", "Current Set"])
    mode_combo.setFixedHeight(26)
    top_layout.addWidget(mode_combo)
    separator = QtWidgets.QFrame()
    separator.setFixedSize(1, 14)
    separator.setStyleSheet("background: #414141; border: 0;")
    top_layout.addWidget(separator)
    top_layout.addStretch(1)
    expand_btn = make_icon_button("chevrons-down.svg", "Expand all")
    collapse_btn = make_icon_button("chevrons-up.svg", "Collapse all")
    select_all_btn = make_icon_button("circle-dot.svg", "Select all")
    select_none_btn = make_icon_button("circle-slash.svg", "Select none")
    icon_bar = QtWidgets.QWidget()
    icon_bar.setObjectName("RizumTransparent")
    icon_layout = QtWidgets.QHBoxLayout(icon_bar)
    icon_layout.setContentsMargins(0, 0, 0, 0)
    icon_layout.setSpacing(4)
    icon_layout.addWidget(expand_btn)
    icon_layout.addWidget(collapse_btn)
    spacer_line = QtWidgets.QFrame()
    spacer_line.setFixedSize(1, 14)
    spacer_line.setStyleSheet("background: #333333; border: 0;")
    icon_layout.addSpacing(4)
    icon_layout.addWidget(spacer_line)
    icon_layout.addSpacing(4)
    icon_layout.addWidget(select_all_btn)
    icon_layout.addWidget(select_none_btn)
    top_layout.addWidget(icon_bar)
    layout.addWidget(top_controls)
    layout.addWidget(make_inset_separator(12, thickness=1))

    tree = QtWidgets.QFrame()
    tree.setObjectName("RizumExportTree")
    tree_layout = QtWidgets.QVBoxLayout(tree)
    tree_layout.setContentsMargins(8, 8, 8, 8)
    tree_layout.setSpacing(4)
    layout.addWidget(tree, 1)

    groups = []

    def make_tree_item(name, checkbox, meta="", child=False):
        if child:
            host = QtWidgets.QFrame()
            host.setObjectName("RizumExportTreeItemHost")
            host.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
            host.setFixedHeight(32)
            host_layout = QtWidgets.QHBoxLayout(host)
            host_layout.setContentsMargins(24, 0, 4, 0)
            host_layout.setSpacing(0)

            row = QtWidgets.QFrame()
            row.setObjectName("RizumExportTreeItem")
            row.setProperty("child", "true")
            row.setFixedHeight(32)
            row_layout = QtWidgets.QHBoxLayout(row)
            row_layout.setContentsMargins(8, 4, 4, 4)
            row_layout.setSpacing(10)
            row_layout.addSpacing(0)

            label = QtWidgets.QLabel(name)
            label.setObjectName("RizumExportItemName")
            row_layout.addWidget(label)
            row_layout.addStretch(1)
            row_layout.addWidget(checkbox)
            host_layout.addWidget(row)
            return host

        row = QtWidgets.QFrame()
        row.setObjectName("RizumExportTreeItem")
        row.setProperty("child", "false")
        row.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        row.setFixedHeight(36)
        row_layout = QtWidgets.QHBoxLayout(row)
        row_layout.setContentsMargins(8, 4, 8, 4)
        row_layout.setSpacing(10)
        row_layout.addWidget(make_svg_label("chevron-down.svg", 14))

        if meta:
            text_stack = QtWidgets.QHBoxLayout()
            text_stack.setContentsMargins(0, 0, 0, 0)
            text_stack.setSpacing(4)
            label = QtWidgets.QLabel(name)
            label.setObjectName("RizumExportItemName")
            meta_label = QtWidgets.QLabel(meta)
            meta_label.setObjectName("RizumExportMeta")
            text_stack.addWidget(label)
            text_stack.addWidget(meta_label)
            text_stack.addStretch(1)
            row_layout.addLayout(text_stack)
        row_layout.addStretch(1)
        row_layout.addWidget(checkbox)
        return row

    def update_parent(group):
        checked_count = sum(1 for child in group["children"] if child.isChecked())
        if checked_count == 0:
            group["parent"].setChecked(False)
        elif checked_count == len(group["children"]):
            group["parent"].setChecked(True)
        else:
            group["parent"].setIndeterminate(True)

    def add_group(name, meta, children):
        parent_cb = make_mock_checkbox(True)
        child_cbs = [make_mock_checkbox(True) for _ in children]
        group = {"parent": parent_cb, "children": child_cbs}
        child_rows = []

        for child_name, child_cb in zip(children, child_cbs):
            child_row = make_tree_item(child_name, child_cb, child=True)
            child_row.mousePressEvent = lambda event, cb=child_cb, g=group: (
                cb.toggle(),
                update_parent(g),
            )
            old_mouse = child_cb.mousePressEvent

            def child_mouse(event, cb=child_cb, g=group, old=old_mouse):
                old(event)
                update_parent(g)

            child_cb.mousePressEvent = child_mouse
            child_rows.append(child_row)

        old_parent_mouse = parent_cb.mousePressEvent

        def parent_mouse(event, cb=parent_cb, g=group, old=old_parent_mouse):
            old(event)
            for child_cb in g["children"]:
                child_cb.setChecked(cb.isChecked())

        parent_cb.mousePressEvent = parent_mouse
        group_frame = make_collapsible_group(
            name,
            meta,
            children=child_rows,
            trailing_widget=parent_cb,
            expanded=True,
        )
        group["widget"] = group_frame
        tree_layout.addWidget(group_frame)
        groups.append(group)

    add_group("M_body", "4 Channels", ["basecolor", "User1"])
    tree_layout.addStretch(1)

    footer = QtWidgets.QFrame()
    footer.setObjectName("RizumExportFooter")
    footer.setFixedHeight(42)
    footer_layout = QtWidgets.QHBoxLayout(footer)
    footer_layout.setContentsMargins(16, 0, 16, 0)
    footer_layout.setSpacing(8)
    footer_layout.addStretch(1)
    cancel = ActionButton.create("Cancel", "dialog-secondary")
    export = ActionButton.create("Export", "dialog-primary")
    set_compact_footer_button_width(cancel, 78)
    set_compact_footer_button_width(export, 82)
    footer_layout.addWidget(cancel)
    footer_layout.addWidget(export)
    layout.addWidget(make_inset_separator(12, thickness=1))
    layout.addWidget(footer)

    expand_btn.clicked.connect(lambda: [group["widget"].setExpanded(True) for group in groups])
    collapse_btn.clicked.connect(lambda: [group["widget"].setExpanded(False) for group in groups])
    select_all_btn.clicked.connect(
        lambda: [
            checkbox.setChecked(True)
            for group in groups
            for checkbox in [group["parent"], *group["children"]]
        ]
    )
    select_none_btn.clicked.connect(
        lambda: [
            checkbox.setChecked(False)
            for group in groups
            for checkbox in [group["parent"], *group["children"]]
        ]
    )
    return window


def build_font_preview(QtWidgets):
    from PySide6 import QtGui
    from PySide6 import QtWidgets as _QtWidgets

    panel = QtWidgets.QWidget()
    panel.setObjectName("RizumUiFontPreview")
    panel.setMinimumSize(COMPACT_DOCK_MIN_WIDTH, COMPACT_DOCK_DEFAULT_HEIGHT)
    panel.resize(COMPACT_DOCK_DEFAULT_WIDTH, COMPACT_DOCK_DEFAULT_HEIGHT)
    panel.setSizePolicy(
        _QtWidgets.QSizePolicy.Policy.Fixed,
        _QtWidgets.QSizePolicy.Policy.Fixed,
    )
    apply_compact_dock_surface(panel)
    base_panel_stylesheet = panel.styleSheet()
    outer_layout = make_compact_dock_layout(panel)

    card = make_compact_dock_card()
    card_layout = card.layout()
    outer_layout.addWidget(card)

    main_widget = QtWidgets.QWidget()
    main_widget.setObjectName("RizumTransparent")
    main_layout = QtWidgets.QVBoxLayout(main_widget)
    main_layout.setContentsMargins(12, 12, 12, 6)
    main_layout.setSpacing(10)

    preview_family = ""
    font_dir = ROOT.parent / "rizum-pt-ui-font" / "fonts"
    for font_name in ("MiSans-Regular.ttf", "MiSans-Medium.ttf"):
        font_path = font_dir / font_name
        if not font_path.exists():
            continue
        font_id = QtGui.QFontDatabase.addApplicationFont(str(font_path))
        if font_id < 0:
            continue
        families = QtGui.QFontDatabase.applicationFontFamilies(font_id)
        if families:
            preview_family = families[0]
            break

    base_font = QtGui.QFont(panel.font())
    if preview_family:
        base_font.setFamily(preview_family)
    base_size = base_font.pointSizeF()
    if base_size <= 0:
        base_size = float(base_font.pointSize())
    if base_size <= 0:
        base_size = 11.0

    def label_width():
        return compact_label_width(["Size", "Font"], widget=panel, minimum=28, maximum=56, padding=6)

    def scale_control_width():
        return compact_text_width("2.00", widget=size_control, minimum=66, maximum=84, padding=30)

    current_label_width = label_width()
    size_control = make_spin_input(1.0)
    size_row = make_field_row(
        "Size",
        size_control,
        label_width=current_label_width,
        gap=8,
        width=66,
    )
    main_layout.addWidget(size_row)

    font_combo = make_combo_input()
    for family in ["System Default", "MiSans", "MiSans Demibold", "Inter", "Segoe UI"]:
        font_combo.addItem(family, family)
    font_combo.setFitToContents(False)
    font_combo.setMinimumWidth(54)
    font_row = make_field_row(
        "Font",
        font_combo,
        label_width=current_label_width,
        gap=8,
    )
    main_layout.addWidget(font_row)

    tool_row = QtWidgets.QHBoxLayout()
    tool_row.setContentsMargins(current_label_width + 8, -6, 0, 2)
    tool_row.setSpacing(0)
    icon_group = QtWidgets.QHBoxLayout()
    icon_group.setContentsMargins(0, 0, 0, 0)
    icon_group.setSpacing(4)
    icon_group.addWidget(make_icon_button("folder.svg", "Open fonts folder"))
    icon_group.addWidget(make_icon_button("refresh.svg", "Refresh font list"))
    tool_row.addLayout(icon_group)
    tool_row.addStretch(1)
    no_hinting = make_mock_checkbox()
    hint_widget = make_inline_checkbox_row("No hinting", no_hinting, minimum=88, maximum=150)
    tool_row.addWidget(hint_widget)
    main_layout.addLayout(tool_row)

    card_layout.addWidget(main_widget)
    card_layout.addStretch(1)

    footer_widget = QtWidgets.QWidget()
    footer_widget.setObjectName("RizumTransparent")
    footer_widget.setFixedHeight(48)
    footer_outer = QtWidgets.QVBoxLayout(footer_widget)
    footer_outer.setContentsMargins(0, 0, 0, 0)
    footer_outer.setSpacing(0)
    footer_row = QtWidgets.QWidget()
    footer_row.setObjectName("RizumTransparent")
    footer_layout = QtWidgets.QHBoxLayout(footer_row)
    footer_layout.setContentsMargins(10, 0, 10, 0)
    footer_layout.setSpacing(8)
    footer_layout.addStretch(1)
    reset_button = ActionButton.create("Reset", "dialog-secondary")
    apply_button = ActionButton.create("Apply", "dialog-primary")
    footer_layout.addWidget(reset_button)
    footer_layout.addWidget(apply_button)
    footer_outer.addWidget(footer_row, 1)
    card_layout.addWidget(footer_widget)

    def refresh_metrics(scale=None):
        scale = float(scale if scale is not None else size_control.value())
        point_size = base_size * scale
        panel.setStyleSheet(
            base_panel_stylesheet
            + f"""
QWidget#RizumUiFontPreview,
QWidget#RizumUiFontPreview QLabel#RizumFieldLabel,
QWidget#RizumUiFontPreview QLabel#RizumHintLabel,
QWidget#RizumUiFontPreview QLabel#RizumMockText,
QWidget#RizumUiFontPreview QPushButton[variant="dialog-secondary"],
QWidget#RizumUiFontPreview QPushButton[variant="dialog-primary"],
QWidget#RizumUiFontPreview QMenu#RizumPopupMenu {{
    font-size: {point_size:.2f}pt;
}}
"""
        )
        next_font = QtGui.QFont(base_font)
        next_font.setPointSizeF(point_size)
        for widget in [panel, *panel.findChildren(_QtWidgets.QWidget)]:
            widget.setFont(next_font)

        next_label_width = label_width()
        tool_row.setContentsMargins(next_label_width + 8, -6, 0, 2)
        update_compact_field_row(
            size_row,
            label_width=next_label_width,
            control_width=scale_control_width(),
        )
        update_compact_field_row(font_row, label_width=next_label_width)
        update_inline_checkbox_row(hint_widget, "No hinting", minimum=88, maximum=150)
        set_compact_footer_button_width(
            reset_button,
            compact_footer_button_width(reset_button, minimum=68, maximum=118),
        )
        set_compact_footer_button_width(
            apply_button,
            compact_footer_button_width(apply_button, minimum=72, maximum=112),
        )
        panel.setMinimumWidth(0)
        panel.setMinimumWidth(max(COMPACT_DOCK_MIN_WIDTH, panel.minimumSizeHint().width()))
        panel.setFixedWidth(panel.minimumWidth())

    refresh_metrics()
    size_control.valueChanged.connect(refresh_metrics)
    return panel


def build_lab(QtWidgets):
    card = Card.create()
    layout = card.layout()
    layout.addWidget(SectionHeader("Component Lab", "Quick controls for visual tuning."))

    text = QtWidgets.QFrame()
    text.setObjectName("RizumMockInput")
    text.setFixedHeight(32)
    text_layout = QtWidgets.QHBoxLayout(text)
    text_layout.setContentsMargins(10, 0, 10, 0)
    text_layout.setSpacing(0)
    placeholder = QtWidgets.QLabel("Output folder")
    placeholder.setObjectName("RizumHintLabel")
    text_layout.addWidget(placeholder)
    text_layout.addStretch(1)
    layout.addWidget(text)

    progress = QtWidgets.QProgressBar()
    progress.setObjectName("RizumLabProgress")
    progress.setRange(0, 100)
    progress.setValue(62)
    progress.setFixedHeight(28)
    progress.setStyleSheet(
        """
QProgressBar#RizumLabProgress {
    background: #222222;
    border: 1px solid #333333;
    border-radius: 0;
    color: #1b1b1b;
    text-align: center;
}
QProgressBar#RizumLabProgress::chunk {
    background: #ffffff;
    border-radius: 0;
}
"""
    )
    layout.addWidget(progress)

    output = QtWidgets.QPlainTextEdit()
    output.setObjectName("RizumLabOutput")
    output.setPlainText("Preview changes here before copying them into Painter.")
    output.setMinimumHeight(90)
    output.setStyleSheet(
        """
QPlainTextEdit#RizumLabOutput {
    background: #222222;
    border: 1px solid transparent;
    border-radius: 6px;
    color: #e0e0e0;
    padding: 8px;
}
"""
    )
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
    from PySide6 import QtCore

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
    grid.addWidget(
        build_bridge_preview(QtWidgets),
        0,
        0,
        2,
        1,
        QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignLeft,
    )
    grid.addWidget(build_font_preview(QtWidgets), 0, 1)
    grid.addWidget(build_lab(QtWidgets), 1, 1)
    grid.setColumnStretch(0, 0)
    grid.setColumnStretch(1, 1)
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
