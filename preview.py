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
    COMPACT_DOCK_DEFAULT_HEIGHT,
    COMPACT_DOCK_DEFAULT_WIDTH,
    COMPACT_DOCK_MIN_WIDTH,
    animate_drag_tree_item_added,
    apply_compact_dock_surface,
    apply_painter_like_base,
    build_painter_host_preview_stylesheet,
    build_stylesheet,
    compact_action_bar_width,
    compact_footer_button_width,
    compact_label_width,
    compact_progress_width,
    compact_text_width,
    make_compact_action_bar,
    make_compact_dock_card,
    make_compact_dock_layout,
    make_compact_icon_toolbar,
    make_compact_stepper,
    make_combo_input,
    make_collapsible_group,
    make_drag_collapsible_group,
    make_drag_tree_item,
    make_dock_actions_panel,
    make_export_tree_item,
    make_field_row,
    make_icon_button,
    make_inset_separator,
    make_inline_checkbox_row,
    make_mock_checkbox,
    make_progress_panel,
    make_spin_input,
    make_svg_label,
    set_compact_footer_button_width,
    update_compact_field_row,
    update_export_tree_item,
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
PREVIEW_CANVAS_STYLESHEET = """
QWidget#RizumSurface {
    background: #2b2b2b;
}

QTabWidget#RizumPreviewTabs::pane {
    background: transparent;
    border: 0;
}

QTabWidget#RizumPreviewTabs QStackedWidget#qt_tabwidget_stackedwidget {
    background: transparent;
    border: 0;
}

QTabBar::base {
    background: transparent;
    border: 0;
}

QTabBar::tab {
    background: #2b2b2b;
    color: #e0e0e0;
    border: 0;
    border-top: 2px solid #414141;
    border-top-left-radius: 5px;
    border-top-right-radius: 5px;
    padding: 4px 12px 4px 12px;
    margin: 2px 2px 0 0;
}

QTabBar::tab:selected,
QTabBar::tab:hover {
    background: #2b2b2b;
    border: 0;
    border-top: 2px solid #414141;
}

QTabBar::tab:selected {
    padding: 8px 16px 6px 16px;
    margin-top: 0;
}
"""


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
    global COMPACT_DOCK_DEFAULT_HEIGHT
    global COMPACT_DOCK_DEFAULT_WIDTH
    global COMPACT_DOCK_MIN_WIDTH
    global animate_drag_tree_item_added
    global apply_compact_dock_surface
    global apply_painter_like_base
    global build_painter_host_preview_stylesheet
    global build_stylesheet
    global compact_action_bar_width
    global compact_footer_button_width
    global compact_label_width
    global compact_progress_width
    global compact_text_width
    global make_compact_action_bar
    global make_compact_dock_card
    global make_compact_dock_layout
    global make_compact_icon_toolbar
    global make_compact_stepper
    global make_combo_input
    global make_collapsible_group
    global make_drag_collapsible_group
    global make_drag_tree_item
    global make_dock_actions_panel
    global make_export_tree_item
    global make_field_row
    global make_icon_button
    global make_inset_separator
    global make_inline_checkbox_row
    global make_mock_checkbox
    global make_progress_panel
    global make_spin_input
    global make_svg_label
    global set_compact_footer_button_width
    global update_compact_field_row
    global update_export_tree_item
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
    COMPACT_DOCK_DEFAULT_HEIGHT = rizum_ui.COMPACT_DOCK_DEFAULT_HEIGHT
    COMPACT_DOCK_DEFAULT_WIDTH = rizum_ui.COMPACT_DOCK_DEFAULT_WIDTH
    COMPACT_DOCK_MIN_WIDTH = rizum_ui.COMPACT_DOCK_MIN_WIDTH
    animate_drag_tree_item_added = rizum_ui.animate_drag_tree_item_added
    apply_compact_dock_surface = rizum_ui.apply_compact_dock_surface
    apply_painter_like_base = rizum_ui.apply_painter_like_base
    build_painter_host_preview_stylesheet = rizum_ui.build_painter_host_preview_stylesheet
    build_stylesheet = rizum_ui.build_stylesheet
    compact_action_bar_width = rizum_ui.compact_action_bar_width
    compact_footer_button_width = rizum_ui.compact_footer_button_width
    compact_label_width = rizum_ui.compact_label_width
    compact_progress_width = rizum_ui.compact_progress_width
    compact_text_width = rizum_ui.compact_text_width
    make_compact_action_bar = rizum_ui.make_compact_action_bar
    make_compact_dock_card = rizum_ui.make_compact_dock_card
    make_compact_dock_layout = rizum_ui.make_compact_dock_layout
    make_compact_icon_toolbar = rizum_ui.make_compact_icon_toolbar
    make_compact_stepper = rizum_ui.make_compact_stepper
    make_combo_input = rizum_ui.make_combo_input
    make_collapsible_group = rizum_ui.make_collapsible_group
    make_drag_collapsible_group = rizum_ui.make_drag_collapsible_group
    make_drag_tree_item = rizum_ui.make_drag_tree_item
    make_dock_actions_panel = rizum_ui.make_dock_actions_panel
    make_export_tree_item = rizum_ui.make_export_tree_item
    make_field_row = rizum_ui.make_field_row
    make_icon_button = rizum_ui.make_icon_button
    make_inset_separator = rizum_ui.make_inset_separator
    make_inline_checkbox_row = rizum_ui.make_inline_checkbox_row
    make_mock_checkbox = rizum_ui.make_mock_checkbox
    make_progress_panel = rizum_ui.make_progress_panel
    make_spin_input = rizum_ui.make_spin_input
    make_svg_label = rizum_ui.make_svg_label
    set_compact_footer_button_width = rizum_ui.set_compact_footer_button_width
    update_compact_field_row = rizum_ui.update_compact_field_row
    update_export_tree_item = rizum_ui.update_export_tree_item
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
    window.setFixedSize(260, 263)
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
    border: 0;
    border-radius: 10px;
    font-family: "__EXPORT_FAMILY__", "Segoe UI", Arial, sans-serif;
}
QFrame#RizumExportHeader,
QWidget#RizumExportTopControls,
QFrame#RizumExportFooter {
    background: transparent;
    border: 0;
}
QLabel#RizumExportTitle {
    color: #e0e0e0;
    font-size: 10pt;
    font-weight: 400;
    background: transparent;
    border: 0;
}
QFrame#RizumExportWindow QLabel:hover {
    background: transparent;
    border: 0;
}
QFrame#RizumExportWindow QLabel#RizumMockText {
    font-size: 9pt;
    font-weight: 400;
    background: transparent;
    border: 0;
}
QLabel#RizumExportItemName {
    color: #e0e0e0;
    font-size: 9pt;
    font-weight: 400;
    background: transparent;
    border: 0;
}
QFrame#RizumExportWindow QLabel#RizumCollapsibleTitle {
    color: #e0e0e0;
    font-size: 9pt;
    font-weight: 400;
    background: transparent;
    border: 0;
}
QFrame#RizumExportWindow QLabel#RizumCollapsibleSubtitle {
    color: #666666;
    font-size: 8pt;
    font-weight: 400;
    background: transparent;
    border: 0;
}
QLabel#RizumExportMeta {
    color: #666666;
    font-size: 8pt;
    font-weight: 400;
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
QFrame#RizumExportTreeItem:hover {
    background: transparent;
    border: 0;
}
QFrame#RizumExportTreeItem[hovered="true"][child="true"] {
    background: rgba(255, 255, 255, 0.06);
    border: 0;
}
QFrame#RizumExportTreeItem[hovered="true"][child="false"] {
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
    font-weight: 400;
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
    layout.addWidget(make_inset_separator(12, thickness=2))

    mode_combo = make_combo_input(["All Sets", "Current Set"])
    mode_combo.setCompactHeight(26)
    expand_btn = make_icon_button("chevrons-down.svg", "Expand all")
    collapse_btn = make_icon_button("chevrons-up.svg", "Collapse all")
    select_all_btn = make_icon_button("circle-dot.svg", "Select all")
    select_none_btn = make_icon_button("circle-slash.svg", "Select none")
    for button in (expand_btn, collapse_btn, select_all_btn, select_none_btn):
        button.setProperty("accent", True)
    icon_bar = make_compact_icon_toolbar(
        expand_btn,
        collapse_btn,
        None,
        select_all_btn,
        select_none_btn,
    )
    top_controls = make_compact_action_bar(
        [mode_combo],
        icon_bar,
        object_name="RizumExportTopControls",
        spacing=0,
    )
    layout.addWidget(top_controls)
    layout.addWidget(make_inset_separator(12, thickness=2))

    tree = QtWidgets.QFrame()
    tree.setObjectName("RizumExportTree")
    tree_layout = QtWidgets.QVBoxLayout(tree)
    tree_layout.setContentsMargins(8, 8, 8, 8)
    tree_layout.setSpacing(4)
    layout.addWidget(tree, 1)

    groups = []

    def make_tree_item(name, checkbox, meta="", child=False):
        return make_export_tree_item(name, checkbox, meta=meta, child=child)

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
        group = {"parent": parent_cb, "children": child_cbs, "rows": []}
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
            group["rows"].append(child_row)

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
    footer_layout.addWidget(cancel)
    footer_layout.addWidget(export)
    layout.addWidget(make_inset_separator(12, thickness=2))
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

    def refresh_layout():
        top_controls.refreshLayout()
        window.setFixedWidth(
            compact_action_bar_width([mode_combo], icon_bar, minimum=260, spacing_budget=4)
        )
        for group in groups:
            for row in group["rows"]:
                row.refreshLayout()
            group["widget"].refreshLayout()
        cancel.refreshLayout(minimum=78, maximum=140)
        export.refreshLayout(minimum=82, maximum=140)

    window.refreshLayout = refresh_layout
    refresh_layout()
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
    folder_btn = make_icon_button("folder.svg", "Open fonts folder")
    refresh_btn = make_icon_button("refresh.svg", "Refresh font list")
    folder_btn.setProperty("accent", True)
    refresh_btn.setProperty("accent", True)
    icon_group.addWidget(folder_btn)
    icon_group.addWidget(refresh_btn)
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
        reset_button.refreshLayout(minimum=68, maximum=118)
        apply_button.refreshLayout(minimum=72, maximum=112)
        panel.setMinimumWidth(0)
        panel.setMinimumWidth(max(COMPACT_DOCK_MIN_WIDTH, panel.minimumSizeHint().width()))
        panel.setFixedWidth(panel.minimumWidth())

    refresh_metrics()
    size_control.valueChanged.connect(refresh_metrics)
    return panel


def build_lab(QtWidgets):
    from PySide6 import QtCore

    card = Card.create()
    card.setStyleSheet(
        card.styleSheet()
        + """
QWidget#RizumSectionHeader {
    background: transparent;
    border: 0;
}
QPlainTextEdit#RizumLabOutput {
    background: #222222;
    border: 0;
    border-radius: 8px;
    color: #e0e0e0;
    padding: 8px;
}
QPlainTextEdit#RizumLabOutput QAbstractScrollArea::corner {
    background: #222222;
    border: 0;
}
"""
    )
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

    progress = make_progress_panel(
        "Exporting Textures",
        62,
        "12 of 28 maps remaining",
    )
    layout.addWidget(progress)

    progress_controls = QtWidgets.QHBoxLayout()
    progress_controls.setContentsMargins(0, 0, 0, 0)
    progress_controls.setSpacing(6)

    def make_progress_button(text, value, status, meta):
        button = ActionButton.create(text, "dialog-secondary")
        set_compact_footer_button_width(button, 54)
        button.clicked.connect(lambda: progress.setProgress(value, status, meta))
        return button

    progress_controls.addWidget(
        make_progress_button("10%", 10, "Preparing...", "Processing assets...")
    )
    progress_controls.addWidget(
        make_progress_button("75%", 75, "Exporting...", "Processing assets...")
    )
    progress_controls.addWidget(
        make_progress_button("100%", 100, "Complete", "Task completed successfully.")
    )
    loop_button = ActionButton.create("Loop", "dialog-secondary")
    set_compact_footer_button_width(loop_button, 58)

    def play_progress_loop():
        progress.setProgress(10, "Preparing...", "Processing assets...")
        QtCore.QTimer.singleShot(
            520,
            lambda: progress.setProgress(75, "Exporting...", "Processing assets..."),
        )
        QtCore.QTimer.singleShot(
            1040,
            lambda: progress.setProgress(100, "Complete", "Task completed successfully."),
        )

    loop_button.clicked.connect(play_progress_loop)
    progress_controls.addWidget(loop_button)
    progress_controls.addStretch(1)
    layout.addLayout(progress_controls)

    output = QtWidgets.QPlainTextEdit()
    output.setObjectName("RizumLabOutput")
    output.setPlainText("Preview changes here before copying them into Painter.")
    output.setMinimumHeight(90)
    layout.addWidget(output)

    return card


def build_dock_actions_preview(QtWidgets):
    """Build the dock actions reference panel from dock_actions_pro_v3.html."""
    from PySide6 import QtCore

    page = QtWidgets.QWidget()
    page.setObjectName("RizumDockActionsPreview")
    layout = QtWidgets.QVBoxLayout(page)
    layout.setContentsMargins(0, 12, 0, 0)
    layout.setSpacing(0)
    layout.addWidget(
        make_dock_actions_panel(),
        0,
        QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignHCenter,
    )
    layout.addStretch(1)
    return page


def build_settings_preview(QtWidgets):
    """Build the PT Bridge settings reference panel from pt-bridge-settings-gemini.html."""
    from PySide6 import QtCore, QtGui, QtWidgets as _QtWidgets

    themes = {
        "dark": {
            "window_bg": "#1b1b1b",
            "border": "#414141",
            "text": "#e0e0e0",
            "muted": "#9e9e9e",
            "faint": "#666666",
            "primary_bg": "#ffffff",
            "primary_text": "#1b1b1b",
            "secondary": "#343434",
            "hover": "rgba(255, 255, 255, 0.04)",
            "control_hover": "rgba(255, 255, 255, 0.08)",
            "segment_slider_bg": "#ffffff",
            "segment_slider_shadow": None,
            "segment_active_text": "#1b1b1b",
            "icon_hover_bg": "rgba(255, 255, 255, 0.04)",
            "primary_hover_bg": "#e0e0e0",
            "primary_pressed_bg": "#b8b8b8",
            "toggle_off": QtGui.QColor("#343434"),
            "toggle_border": QtGui.QColor(0, 0, 0, 0),
            "toggle_knob_off": QtGui.QColor("#a0a0a0"),
            "toggle_knob_on": QtGui.QColor("#a0a0a0"),
            "window_border_css": "1px solid transparent",
            "segment_bg": QtGui.QColor("#343434"),
        },
        "light": {
            "window_bg": "#ffffff",
            "border": "#e5e5e5",
            "text": "#1d1d1f",
            "muted": "#86868b",
            "faint": "#a1a1a6",
            "primary_bg": "#1d1d1f",
            "primary_text": "#ffffff",
            "secondary": "#e5e5e7",
            "hover": "rgba(0, 0, 0, 0.03)",
            "control_hover": "rgba(0, 0, 0, 0.07)",
            "segment_slider_bg": "#ffffff",
            "segment_slider_shadow": None,
            "segment_active_text": "#1d1d1f",
            "icon_hover_bg": "rgba(0, 0, 0, 0.03)",
            "primary_hover_bg": "#323234",
            "primary_pressed_bg": "#000000",
            "toggle_off": QtGui.QColor("#e6e6e6"),
            "toggle_border": QtGui.QColor(0, 0, 0, 0),
            "toggle_knob_off": QtGui.QColor("#ffffff"),
            "toggle_knob_on": QtGui.QColor("#ffffff"),
            "window_border_css": "1px solid #e5e5e5",
            "segment_bg": QtGui.QColor("#eaeaea"),
        },
    }

    class ThemeSegmentControl(_QtWidgets.QFrame):
        def __init__(self):
            super().__init__()
            self._options = ["Light", "Dark", "System"]
            self._padding = 2.0
            self._widths = [54.55, 52.50, 67.88]
            self._positions = [2.0, 56.55, 109.05]
            self._active = 1
            self._theme = themes["dark"]
            self._animation = None
            self._callback = None
            self.setObjectName("RizumSettingsThemeSegment")
            self.setFixedSize(179, 30)
            self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
            self.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
            self._slider_x = self._positions[self._active]
            self._slider_width = self._widths[self._active]

        def setChangedCallback(self, callback):
            self._callback = callback

        def setTheme(self, theme):
            self._theme = theme
            self.update()

        def getSliderX(self):
            return self._slider_x

        def setSliderX(self, value):
            self._slider_x = float(value)
            self.update()

        def getSliderWidth(self):
            return self._slider_width

        def setSliderWidth(self, value):
            self._slider_width = float(value)
            self.update()

        sliderX = QtCore.Property(float, getSliderX, setSliderX)
        sliderWidth = QtCore.Property(float, getSliderWidth, setSliderWidth)

        def setActive(self, name, animate=True, emit=False):
            index = {"light": 0, "dark": 1, "system": 2}.get(str(name).lower(), 1)
            if index == self._active and not emit:
                self.update()
                return
            self._active = index
            end_x = self._positions[index]
            end_width = self._widths[index]
            if self._animation is not None:
                self._animation.stop()
            if animate:
                group = QtCore.QParallelAnimationGroup(self)
                for prop, start, end in (
                    (b"sliderX", self._slider_x, end_x),
                    (b"sliderWidth", self._slider_width, end_width),
                ):
                    animation = QtCore.QPropertyAnimation(self, prop, self)
                    animation.setDuration(220)
                    animation.setStartValue(start)
                    animation.setEndValue(end)
                    animation.setEasingCurve(QtCore.QEasingCurve.Type.OutBack)
                    group.addAnimation(animation)
                self._animation = group
                group.start()
            else:
                self._slider_x = end_x
                self._slider_width = end_width
                self.update()
            if emit and self._callback is not None:
                self._callback(self._options[index].lower())

        def mousePressEvent(self, event):
            if event.button() == QtCore.Qt.MouseButton.LeftButton:
                x = event.position().x()
                for index, start in enumerate(self._positions):
                    end = start + self._widths[index]
                    if start <= x <= end:
                        self.setActive(self._options[index].lower(), animate=True, emit=True)
                        break
            super().mousePressEvent(event)

        def paintEvent(self, event):
            painter = QtGui.QPainter(self)
            painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)
            painter.setPen(QtCore.Qt.PenStyle.NoPen)
            painter.setBrush(self._theme["segment_bg"])
            painter.drawRoundedRect(QtCore.QRectF(0, 0, self.width(), self.height()), 7, 7)
            slider_rect = QtCore.QRectF(
                self._slider_x,
                self._padding,
                self._slider_width,
                self.height() - self._padding * 2.0,
            )
            shadow = self._theme.get("segment_slider_shadow")
            if shadow is not None:
                painter.setBrush(QtGui.QColor(shadow.red(), shadow.green(), shadow.blue(), 10))
                painter.drawRoundedRect(slider_rect.translated(0, 2).adjusted(0, 0, 0, 1), 5, 5)
                painter.setBrush(shadow)
                painter.drawRoundedRect(slider_rect.translated(0, 1), 4, 4)
            painter.setBrush(QtGui.QColor(self._theme["segment_slider_bg"]))
            painter.drawRoundedRect(
                slider_rect,
                6,
                6,
            )
            font = QtGui.QFont(self.font())
            font.setPixelSize(12)
            font.setWeight(QtGui.QFont.Weight.Medium)
            painter.setFont(font)
            for index, label in enumerate(self._options):
                painter.setPen(
                    QtGui.QColor(self._theme["segment_active_text"])
                    if index == self._active
                    else QtGui.QColor(self._theme["muted"])
                )
                painter.drawText(
                    QtCore.QRectF(
                        self._positions[index],
                        self._padding,
                        self._widths[index],
                        self.height() - self._padding * 2.0,
                    ),
                    QtCore.Qt.AlignmentFlag.AlignCenter,
                    label,
                )
            painter.end()

    class ToggleSwitch(_QtWidgets.QFrame):
        def __init__(self, on=False):
            super().__init__()
            self._on = bool(on)
            self._theme = themes["dark"]
            self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)
            self.setAutoFillBackground(False)
            self.setStyleSheet("background: transparent; border: 0;")
            self.setFixedSize(36, 20)
            self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
            self.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
            self._knob_margin = 3.0
            self._knob_size = 14.0
            self._offset = self._knob_travel() if self._on else 0.0
            self._animation = None
            self._callback = None

        def _knob_travel(self):
            return float(self.width()) - self._knob_size - self._knob_margin * 2

        def setChangedCallback(self, callback):
            self._callback = callback

        def setTheme(self, theme):
            self._theme = theme
            self.update()

        def getOffset(self):
            return self._offset

        def setOffset(self, value):
            self._offset = float(value)
            self.update()

        offset = QtCore.Property(float, getOffset, setOffset)

        def isOn(self):
            return self._on

        def setOn(self, enabled):
            enabled = bool(enabled)
            if self._on == enabled:
                return
            self._on = enabled
            if self._animation is not None:
                self._animation.stop()
            animation = QtCore.QPropertyAnimation(self, b"offset", self)
            animation.setDuration(300)
            animation.setStartValue(self._offset)
            animation.setEndValue(self._knob_travel() if self._on else 0.0)
            animation.setEasingCurve(QtCore.QEasingCurve.Type.OutBack)
            self._animation = animation
            animation.start()
            if self._callback is not None:
                self._callback(self._on)

        def mousePressEvent(self, event):
            if event.button() == QtCore.Qt.MouseButton.LeftButton:
                self.toggle()
                event.accept()
                return
            super().mousePressEvent(event)

        def toggle(self):
            self.setOn(not self._on)

        def paintEvent(self, event):
            painter = QtGui.QPainter(self)
            painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)
            rect = QtCore.QRectF(0.5, 0.5, self.width() - 1.0, self.height() - 1.0)
            radius = rect.height() / 2.0
            painter.setPen(QtCore.Qt.PenStyle.NoPen)
            painter.setBrush(QtGui.QColor(self._theme["primary_bg"]) if self._on else self._theme["toggle_off"])
            painter.drawRoundedRect(rect, radius, radius)
            knob_x = self._knob_margin + self._offset
            painter.setPen(QtCore.Qt.PenStyle.NoPen)
            painter.setBrush(self._theme["toggle_knob_on"] if self._on else self._theme["toggle_knob_off"])
            painter.drawEllipse(
                QtCore.QRectF(
                    knob_x,
                    self._knob_margin,
                    self._knob_size,
                    self._knob_size,
                )
            )
            painter.end()

    def make_label(text, object_name, parent=None):
        label = _QtWidgets.QLabel(text, parent)
        label.setObjectName(object_name)
        return label

    def make_section(text, first=False):
        label = make_label(text.upper(), "RizumSettingsSection")
        label.setFixedHeight(28 if first else 40)
        return label

    def make_row(height=40):
        row = _QtWidgets.QFrame()
        row.setObjectName("RizumSettingsRow")
        row.setFixedHeight(height)
        layout = _QtWidgets.QHBoxLayout(row)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        return row, layout

    class RevealRow(_QtWidgets.QFrame):
        def __init__(self, content, expanded_height):
            super().__init__()
            self.setObjectName("RizumSettingsRevealRow")
            self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)
            self.setAutoFillBackground(False)
            self.setStyleSheet("background: transparent; border: 0;")
            self._expanded_height = expanded_height
            self._progress = 1.0
            self._gap_layout = None
            self._geometry_callback = None
            self._animation = None
            self._expanded = True
            layout = _QtWidgets.QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            layout.addWidget(content)
            self.setFixedHeight(expanded_height)

        def setGapLayout(self, layout):
            self._gap_layout = layout
            self._syncRevealGeometry()

        def setGeometryCallback(self, callback):
            self._geometry_callback = callback

        def _syncRevealGeometry(self):
            progress = max(0.0, min(1.0, self._progress))
            self.setFixedHeight(round(self._expanded_height * progress))
            if self._gap_layout is not None:
                self._gap_layout.setSpacing(int(2.0 * progress + 0.5))
            if self._geometry_callback is not None:
                self._geometry_callback(progress)

        def _layoutProgress(self):
            return max(0.0, min(1.0, self._progress))

        def getRevealProgress(self):
            return self._progress

        def setRevealProgress(self, value):
            self._progress = float(value)
            self._syncRevealGeometry()

        revealProgress = QtCore.Property(float, getRevealProgress, setRevealProgress)

        def setExpanded(self, expanded, animate=True):
            expanded = bool(expanded)
            self._expanded = expanded
            target_progress = 1.0 if expanded else 0.0
            if animate and abs(self._progress - target_progress) < 0.001:
                self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents, not expanded)
                return
            if self._animation is not None:
                self._animation.stop()
            if not animate:
                self.setRevealProgress(target_progress)
                self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents, not expanded)
                return
            self.setVisible(True)
            self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents, not expanded)
            if expanded and self._progress < 0.25:
                self.setRevealProgress(0.25)
            elif not expanded and self._progress > 0.75:
                self.setRevealProgress(0.75)
            animation = QtCore.QPropertyAnimation(self, b"revealProgress", self)
            animation.setDuration(max(120, round(400 * abs(target_progress - self._progress))))
            animation.setStartValue(self._progress)
            animation.setEndValue(target_progress)
            animation.setEasingCurve(QtCore.QEasingCurve.Type.OutQuart)
            self._animation = animation
            animation.start()

    def make_text_block(name, meta=""):
        widget = _QtWidgets.QWidget()
        widget.setObjectName("RizumSettingsTexts")
        layout = _QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        layout.addWidget(make_label(name, "RizumSettingsItemName"))
        if meta:
            layout.addWidget(make_label(meta, "RizumSettingsItemMeta"))
        return widget

    window = _QtWidgets.QFrame()
    window.setObjectName("RizumSettingsWindow")
    window.setFixedWidth(342)
    window.setSizePolicy(
        _QtWidgets.QSizePolicy.Policy.Fixed,
        _QtWidgets.QSizePolicy.Policy.Fixed,
    )

    layout = _QtWidgets.QVBoxLayout(window)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)

    header = _QtWidgets.QWidget()
    header.setObjectName("RizumSettingsHeader")
    header.setFixedHeight(40)
    header_outer = _QtWidgets.QVBoxLayout(header)
    header_outer.setContentsMargins(0, 0, 0, 0)
    header_outer.setSpacing(0)
    header_row = _QtWidgets.QWidget()
    header_row.setObjectName("RizumSettingsHeaderRow")
    header_layout = _QtWidgets.QHBoxLayout(header_row)
    header_layout.setContentsMargins(16, 0, 16, 0)
    header_layout.setSpacing(0)
    header_layout.addWidget(make_label("Settings", "RizumSettingsTitle"))
    header_layout.addStretch(1)
    header_layout.addWidget(make_svg_label("x.svg", 14))
    header_outer.addWidget(header_row, 1)
    header_outer.addWidget(make_inset_separator(12, 1))
    layout.addWidget(header)

    body = _QtWidgets.QWidget()
    body.setObjectName("RizumSettingsBody")
    body_layout = _QtWidgets.QVBoxLayout(body)
    body_layout.setContentsMargins(12, 8, 12, 16)
    body_layout.setSpacing(2)

    body_layout.addWidget(make_section("Appearance", first=True))
    theme_row, theme_layout = make_row(40)
    theme_layout.setContentsMargins(8, 5, 8, 5)
    theme_layout.addWidget(make_label("Theme", "RizumSettingsItemName"))
    theme_layout.addStretch(1)
    theme_control = ThemeSegmentControl()
    theme_layout.addWidget(theme_control)
    body_layout.addWidget(theme_row)

    body_layout.addWidget(make_section("Export"))
    padding_stack = _QtWidgets.QWidget()
    padding_stack.setObjectName("RizumSettingsPaddingStack")
    padding_stack_layout = _QtWidgets.QVBoxLayout(padding_stack)
    padding_stack_layout.setContentsMargins(0, 0, 0, 0)
    padding_stack_layout.setSpacing(0)
    padding_row, padding_layout = make_row(51)
    padding_texts = make_text_block("Padding", "Infinite")
    padding_meta = padding_texts.findChild(_QtWidgets.QLabel, "RizumSettingsItemMeta")
    padding_layout.addWidget(padding_texts)
    padding_layout.addStretch(1)
    padding_toggle = ToggleSwitch(True)
    padding_layout.addWidget(padding_toggle)
    padding_stack_layout.addWidget(padding_row)

    dilation_row, dilation_layout = make_row(51)
    dilation_layout.addWidget(make_text_block("Dilation", "px"))
    dilation_layout.addStretch(1)
    stepper = make_compact_stepper(8, minimum=0, maximum=999, step=1)
    dilation_layout.addWidget(stepper)
    dilation_reveal = RevealRow(dilation_row, 51)
    padding_stack_layout.addWidget(dilation_reveal)
    dilation_reveal.setGapLayout(padding_stack_layout)
    body_layout.addWidget(padding_stack)

    auto_row, auto_layout = make_row(36)
    auto_layout.addWidget(make_label("Auto-open Photoshop", "RizumSettingsItemName"))
    auto_layout.addStretch(1)
    auto_toggle = ToggleSwitch(False)
    auto_layout.addWidget(auto_toggle)
    body_layout.addWidget(auto_row)

    body_layout.addWidget(make_section("Photoshop"))
    path_row, path_layout = make_row(45)
    path_layout.setContentsMargins(8, 5, 8, 5)
    path_select = _QtWidgets.QFrame()
    path_select.setObjectName("RizumSettingsMockSelect")
    path_select.setFixedHeight(34)
    path_select_layout = _QtWidgets.QHBoxLayout(path_select)
    path_select_layout.setContentsMargins(8, 0, 8, 0)
    path_select_layout.setSpacing(6)
    path_input = _QtWidgets.QLineEdit(r"C:\Program Files\Adobe\Photoshop.exe")
    path_input.setObjectName("RizumSettingsPathInput")
    path_input.setFrame(False)
    path_input.setClearButtonEnabled(False)
    path_input.setCursorPosition(0)
    path_input.setFixedHeight(20)
    path_input.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter)
    path_input.setSizePolicy(
        _QtWidgets.QSizePolicy.Policy.Expanding,
        _QtWidgets.QSizePolicy.Policy.Fixed,
    )
    path_select_layout.addWidget(path_input, 1, QtCore.Qt.AlignmentFlag.AlignVCenter)
    path_layout.addWidget(path_select, 1)
    browse_btn = make_icon_button("folder.svg", "Browse executable", size=14, compact=False)
    browse_btn.setFixedSize(26, 26)
    path_layout.addWidget(browse_btn)
    body_layout.addWidget(path_row)

    body_layout.addWidget(make_section("About"))
    version_row, version_layout = make_row(34)
    version_layout.addWidget(make_label("Version", "RizumSettingsItemName"))
    version_layout.addStretch(1)
    version_layout.addWidget(make_label("2.0.0", "RizumSettingsItemMeta"))
    body_layout.addWidget(version_row)

    layout.addWidget(body)

    footer = _QtWidgets.QWidget()
    footer.setObjectName("RizumSettingsFooter")
    footer.setFixedHeight(48)
    footer_outer = _QtWidgets.QVBoxLayout(footer)
    footer_outer.setContentsMargins(0, 0, 0, 0)
    footer_outer.setSpacing(0)
    footer_outer.addWidget(make_inset_separator(12, 1))
    footer_row = _QtWidgets.QWidget()
    footer_row.setObjectName("RizumSettingsFooterRow")
    footer_layout = _QtWidgets.QHBoxLayout(footer_row)
    footer_layout.setContentsMargins(16, 0, 16, 0)
    footer_layout.setSpacing(0)
    footer_layout.addWidget(make_label("Changes save automatically", "RizumSettingsFooterHint"))
    footer_layout.addStretch(1)
    done_button = ActionButton.create("Done", "dialog-primary")
    done_button.refreshLayout(minimum=72, maximum=112)
    footer_layout.addWidget(done_button)
    footer_outer.addWidget(footer_row, 1)
    layout.addWidget(footer)

    toggles = [padding_toggle, auto_toggle]

    def apply_theme(name, update_control=True):
        theme_name = "dark" if name == "system" else name
        theme = themes.get(theme_name, themes["dark"])
        window.setProperty("theme", theme_name)
        window.setStyleSheet(
            f"""
QFrame#RizumSettingsWindow {{
    background: {theme["window_bg"]};
    border: {theme["window_border_css"]};
    border-radius: 10px;
}}
QFrame#RizumSettingsWindow QFrame#RizumInsetSeparator {{
    background: {theme["border"]};
    border: 0;
}}
QWidget#RizumSettingsHeader,
QWidget#RizumSettingsHeaderRow,
QWidget#RizumSettingsBody,
QWidget#RizumSettingsFooter,
QWidget#RizumSettingsFooterRow,
QWidget#RizumSettingsPaddingStack,
QWidget#RizumSettingsTexts,
QWidget#RizumSettingsStepper,
QFrame#RizumSettingsRevealRow {{
    background: transparent;
    border: 0;
}}
QLabel#RizumSettingsTitle {{
    color: {theme["text"]};
    font-size: 13px;
    font-weight: 600;
    background: transparent;
    border: 0;
}}
QLabel#RizumSettingsSection {{
    color: {theme["faint"]};
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.5px;
    background: transparent;
    border: 0;
}}
QLabel#RizumSettingsItemName {{
    color: {theme["text"]};
    font-size: 13px;
    font-weight: 500;
    background: transparent;
    border: 0;
}}
QLabel#RizumSettingsItemMeta,
QLabel#RizumSettingsFooterHint {{
    color: {theme["faint"]};
    font-size: 11px;
    font-weight: 500;
    background: transparent;
    border: 0;
}}
QFrame#RizumSettingsRow {{
    background: transparent;
    border: 0;
    border-radius: 6px;
}}
QFrame#RizumSettingsRow:hover {{
    background: {theme["hover"]};
    border: 0;
}}
QPushButton#RizumSettingsSegment {{
    min-height: 0;
    padding: 4px 10px;
    color: {theme["muted"]};
    background: transparent;
    border: 0;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 500;
}}
QPushButton#RizumSettingsSegment:hover {{
    color: {theme["text"]};
    background: {theme["hover"]};
}}
QPushButton#RizumSettingsSegment[active="true"] {{
    color: {theme["primary_text"]};
    background: {theme["primary_bg"]};
    font-weight: 600;
}}
QFrame#RizumSettingsMockSelect {{
    background: transparent;
    border: 1px solid transparent;
    border-radius: 6px;
}}
QFrame#RizumSettingsMockSelect:hover {{
    background: transparent;
    border: 1px solid transparent;
}}
QLineEdit#RizumSettingsPathInput {{
    color: {theme["faint"]};
    background: transparent;
    border: 0;
    padding: 0;
    font-size: 11px;
    font-weight: 500;
    selection-background-color: {theme["control_hover"]};
    selection-color: {theme["text"]};
}}
QLineEdit#RizumSettingsPathInput:hover,
QLineEdit#RizumSettingsPathInput:focus {{
    color: {theme["text"]};
    background: transparent;
    border: 0;
}}
QFrame#RizumSettingsWindow QPushButton[variant="icon"] {{
    background: transparent;
    border: 1px solid transparent;
    border-radius: 4px;
}}
QFrame#RizumSettingsWindow QPushButton[variant="icon"]:hover {{
    background: {theme["icon_hover_bg"]};
    border: 1px solid transparent;
}}
QFrame#RizumSettingsWindow QPushButton[variant="icon"]:pressed {{
    background: {theme["control_hover"]};
    border: 1px solid transparent;
}}
QFrame#RizumSettingsWindow QPushButton[variant="dialog-primary"] {{
    color: {theme["primary_text"]};
    background: {theme["primary_bg"]};
    border: 1px solid transparent;
    border-radius: 13px;
    font-size: 12px;
    font-weight: 600;
}}
QFrame#RizumSettingsWindow QPushButton[variant="dialog-primary"]:hover {{
    background: {theme["primary_hover_bg"]};
}}
QFrame#RizumSettingsWindow QPushButton[variant="dialog-primary"]:pressed {{
    background: {theme["primary_pressed_bg"]};
}}
"""
        )
        theme_control.setTheme(theme)
        if update_control:
            theme_control.setActive(name, animate=False)
        stepper.setTheme(theme)
        for toggle in toggles:
            toggle.setTheme(theme)
        browse_btn.setProperty("iconColor", theme["muted"])
        browse_btn.setProperty("iconHoverColor", theme["text"])
        browse_btn.update()

    theme_control.setChangedCallback(lambda name: apply_theme(name, update_control=False))
    base_window_height = None

    def sync_window_height(reveal_progress=0.0):
        nonlocal base_window_height
        if base_window_height is None:
            base_window_height = window.sizeHint().height()
        window.setFixedHeight(base_window_height + round(53 * reveal_progress))
        window.updateGeometry()

    dilation_reveal.setGeometryCallback(sync_window_height)

    def bind_toggle_row(row, toggle):
        def press(event):
            if event.button() == QtCore.Qt.MouseButton.LeftButton:
                toggle.toggle()
                event.accept()
                return
            _QtWidgets.QFrame.mousePressEvent(row, event)

        row.mousePressEvent = press

    bind_toggle_row(padding_row, padding_toggle)
    bind_toggle_row(auto_row, auto_toggle)
    def sync_padding_dilation(enabled):
        if padding_meta is not None:
            padding_meta.setText("Infinite" if enabled else "Custom")
        dilation_reveal.setExpanded(not enabled)

    padding_toggle.setChangedCallback(sync_padding_dilation)
    dilation_reveal.setExpanded(not padding_toggle.isOn(), animate=False)
    apply_theme("dark")
    sync_window_height(0.0)
    window.setTheme = apply_theme
    return window


def build_drag_drop_preview(QtWidgets):
    from PySide6 import QtCore, QtGui, QtWidgets as _QtWidgets

    class RoundedColumn(_QtWidgets.QFrame):
        def __init__(self):
            super().__init__()
            self.setObjectName("RizumDragColumn")
            self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)
            self.setAutoFillBackground(False)

        def paintEvent(self, event):
            painter = QtGui.QPainter(self)
            painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)
            rect = QtCore.QRectF(8.5, 4.5, self.width() - 17, self.height() - 13)
            painter.setPen(QtCore.Qt.PenStyle.NoPen)
            for offset_y, spread, alpha in ((4, 1, 44), (8, 4, 22), (12, 8, 10)):
                shadow_rect = rect.adjusted(-spread, -spread, spread, spread).translated(0, offset_y)
                painter.setBrush(QtGui.QColor(0, 0, 0, alpha))
                painter.drawRoundedRect(shadow_rect, 8 + spread, 8 + spread)
            painter.setPen(QtCore.Qt.PenStyle.NoPen)
            painter.setBrush(QtGui.QColor("#222222"))
            painter.drawRoundedRect(rect, 8, 8)

    class RoundedDragWindow(_QtWidgets.QFrame):
        def __init__(self):
            super().__init__()
            self.setObjectName("RizumDragWindow")
            self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)
            self.setAutoFillBackground(False)

        def paintEvent(self, event):
            painter = QtGui.QPainter(self)
            painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)
            rect = QtCore.QRectF(0.5, 0.5, self.width() - 1, self.height() - 1)
            painter.setPen(QtCore.Qt.PenStyle.NoPen)
            painter.setBrush(QtGui.QColor("#1b1b1b"))
            painter.drawRoundedRect(rect, 10, 10)
            painter.end()

    class DropColumn(RoundedColumn):
        def __init__(self, source_group):
            super().__init__()
            self.source_group = source_group
            self.setAcceptDrops(True)
            layout = _QtWidgets.QVBoxLayout(self)
            layout.setContentsMargins(9, 5, 9, 9)
            layout.setSpacing(0)
            self.header = _QtWidgets.QWidget()
            self.header.setObjectName("RizumDragColumnHeader")
            header_layout = _QtWidgets.QVBoxLayout(self.header)
            header_layout.setContentsMargins(16, 12, 16, 10)
            header_layout.setSpacing(2)
            title = _QtWidgets.QLabel("TARGET: PAINTER")
            title.setObjectName("RizumDragColumnTitle")
            subtitle = _QtWidgets.QLabel("M_Body - BaseColor")
            subtitle.setObjectName("RizumDragColumnSub")
            header_layout.addWidget(title)
            header_layout.addWidget(subtitle)
            layout.addWidget(self.header)
            layout.addWidget(make_inset_separator(12, 1))
            self.tree = _QtWidgets.QWidget()
            self.tree.setObjectName("RizumDragTree")
            self.tree_layout = _QtWidgets.QVBoxLayout(self.tree)
            self.tree_layout.setContentsMargins(8, 8, 8, 8)
            self.tree_layout.setSpacing(4)
            first_item = make_drag_tree_item(
                "Dirt_Overlay",
                draggable=True,
                removable=True,
                on_remove=self._return_to_source,
                masked=True,
            )
            self.target_group = make_drag_collapsible_group(
                "Target Group",
                "",
                children=[first_item],
                draggable=False,
                expanded=True,
            )
            self.drop_line = _QtWidgets.QFrame()
            self.drop_line.setObjectName("RizumDragDropLine")
            self.drop_line.setFixedHeight(2)
            self.drop_line.setVisible(False)
            self.tree_layout.addWidget(self.target_group)
            self.tree_layout.addStretch(1)
            layout.addWidget(self.tree, 1)

        def dragEnterEvent(self, event):
            if event.mimeData().hasText():
                self.setProperty("dragOver", True)
                self.style().unpolish(self)
                self.style().polish(self)
                self.update()
                event.acceptProposedAction()

        def dragMoveEvent(self, event):
            self._show_drop_line(self._drop_index(event.position().toPoint()))
            event.acceptProposedAction()

        def dragLeaveEvent(self, event):
            self._hide_drop_line()
            self.setProperty("dragOver", False)
            self.style().unpolish(self)
            self.style().polish(self)
            self.update()

        def dropEvent(self, event):
            name = event.mimeData().text()
            kind = bytes(event.mimeData().data("application/x-rizum-layer-kind")).decode("utf-8")
            masked = bytes(event.mimeData().data("application/x-rizum-layer-masked")).decode("utf-8") == "1"
            index = self._drop_line_index()
            self._hide_drop_line()
            if not self.target_group.isExpanded():
                self.target_group.setExpanded(True)
            source = event.source()
            source_host = getattr(source, "_rizum_host", None)
            if source_host in self._drop_widgets():
                widgets = self._drop_widgets()
                old_index = widgets.index(source_host)
                if old_index < index:
                    index -= 1
                self.target_group._rizum_content_layout.removeWidget(source_host)
                self.target_group._rizum_content_layout.insertWidget(index, source_host)
                self.target_group.refreshLayout()
                self.setProperty("dragOver", False)
                self.style().unpolish(self)
                self.style().polish(self)
                self.update()
                event.acceptProposedAction()
                return
            item = make_drag_tree_item(
                name,
                "folder-filled.svg" if kind == "folder" else "layers.svg",
                folder=(kind == "folder"),
                draggable=True,
                removable=True,
                on_remove=self._return_to_source,
                masked=masked,
            )
            item._rizum_parent_group = self.target_group
            self.target_group._rizum_content_layout.insertWidget(index, item)
            animate_drag_tree_item_added(item, self.target_group)
            if source_host is not None:
                self._remove_source_widget(source_host)
            self.setProperty("dragOver", False)
            self.style().unpolish(self)
            self.style().polish(self)
            self.update()
            event.acceptProposedAction()

        def _remove_source_widget(self, source_host):
            if source_host is self.target_group or source_host in self._drop_widgets():
                return
            parent_widget = source_host.parentWidget()
            parent_layout = parent_widget.layout() if parent_widget is not None else None
            if parent_layout is not None:
                parent_layout.removeWidget(source_host)
            source_group = getattr(source_host, "_rizum_parent_group", None)
            source_host.deleteLater()
            if source_group is not None:
                source_group.refreshLayout()
            elif parent_widget is not None:
                try:
                    parent_widget.updateGeometry()
                except Exception:
                    pass

        def _return_to_source(self, target_host):
            name = getattr(target_host, "_rizum_name", "")
            folder = bool(getattr(target_host, "_rizum_folder", False))
            masked = bool(getattr(target_host, "_rizum_masked", False))
            source_item = make_drag_tree_item(
                name,
                "folder-filled.svg" if folder else "layers.svg",
                folder=folder,
                draggable=True,
                masked=masked,
            )
            source_item._rizum_parent_group = self.source_group
            source_row = getattr(source_item, "_rizum_row", source_item)
            source_item._rizum_added_final_host_height = max(
                1, source_item.sizeHint().height() or 36
            )
            source_row._rizum_added_final_row_height = max(
                1, source_row.sizeHint().height() or 34
            )
            source_item.setFixedHeight(0)
            source_row.setFixedHeight(0)
            self.source_group._rizum_content_layout.addWidget(source_item)
            self.source_group.refreshLayout()

            self.target_group._rizum_content_layout.removeWidget(target_host)
            self.target_group.refreshLayout()
            target_host.deleteLater()

            animate_drag_tree_item_added(source_item, self.source_group)

        def _drop_widgets(self):
            layout = self.target_group._rizum_content_layout
            widgets = []
            for index in range(layout.count()):
                widget = layout.itemAt(index).widget()
                if widget is not None and widget is not self.drop_line:
                    widgets.append(widget)
            return widgets

        def _drop_index(self, point):
            inner = self.target_group._rizum_content_inner
            local = inner.mapFrom(self, point)
            for index, widget in enumerate(self._drop_widgets()):
                if local.y() < widget.y() + widget.height() / 2:
                    return index
            return len(self._drop_widgets())

        def _drop_line_index(self):
            if not self.drop_line.isVisible():
                return len(self._drop_widgets())
            layout = self.target_group._rizum_content_layout
            index = layout.indexOf(self.drop_line)
            if index < 0:
                return len(self._drop_widgets())
            return index

        def _show_drop_line(self, index):
            layout = self.target_group._rizum_content_layout
            layout.removeWidget(self.drop_line)
            layout.insertWidget(index, self.drop_line)
            self.drop_line.setVisible(True)
            self.target_group.refreshLayout()

        def _hide_drop_line(self):
            self.drop_line.setVisible(False)
            self.target_group.refreshLayout()

    def make_column(title_text, subtitle_text, items):
        column = RoundedColumn()
        layout = _QtWidgets.QVBoxLayout(column)
        layout.setContentsMargins(9, 5, 9, 9)
        layout.setSpacing(0)
        header = _QtWidgets.QWidget()
        header.setObjectName("RizumDragColumnHeader")
        header_layout = _QtWidgets.QVBoxLayout(header)
        header_layout.setContentsMargins(16, 12, 16, 10)
        header_layout.setSpacing(2)
        title = _QtWidgets.QLabel(title_text.upper())
        title.setObjectName("RizumDragColumnTitle")
        subtitle = _QtWidgets.QLabel(subtitle_text)
        subtitle.setObjectName("RizumDragColumnSub")
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        layout.addWidget(header)
        layout.addWidget(make_inset_separator(12, 1))
        tree = _QtWidgets.QWidget()
        tree.setObjectName("RizumDragTree")
        tree_layout = _QtWidgets.QVBoxLayout(tree)
        tree_layout.setContentsMargins(8, 8, 8, 8)
        tree_layout.setSpacing(4)
        group_rows = [
            make_drag_tree_item(
                item[0],
                "folder-filled.svg" if item[1] else "layers.svg",
                folder=item[1],
                draggable=True,
                masked=item[2] if len(item) > 2 else False,
            )
            for item in items
        ]
        group = make_drag_collapsible_group(
            "Body Textures",
            "",
            children=group_rows,
            draggable=True,
            expanded=True,
        )
        column._rizum_group = group
        tree_layout.addWidget(group)
        tree_layout.addStretch(1)
        layout.addWidget(tree, 1)
        return column

    window = RoundedDragWindow()
    window.setFixedSize(580, 430)
    window.setStyleSheet(
        """
QFrame#RizumDragWindow {
    background: transparent;
    border: 0;
}
QWidget#RizumDragHeader, QWidget#RizumDragActionBar {
    background: transparent;
    border: 0;
}
QWidget#RizumDragContent {
    background: transparent;
    border: 0;
}
QWidget#RizumDragColumnHeader,
QWidget#RizumDragTree {
    background: transparent;
    border: 0;
}
QLabel#RizumDragTitle {
    color: #e0e0e0;
    font-size: 13px;
    font-weight: 400;
    background: transparent;
}
QLabel#RizumDragColumnTitle {
    color: #e0e0e0;
    font-size: 12px;
    font-weight: 400;
    background: transparent;
}
QLabel#RizumDragColumnSub {
    color: #666666;
    font-size: 11px;
    font-weight: 400;
    background: transparent;
}
QFrame#RizumDragDropLine {
    background: #ffffff;
    border: 0;
    border-radius: 1px;
}
QPushButton#RizumRemoveButton {
    min-width: 24px;
    max-width: 24px;
    min-height: 24px;
    max-height: 24px;
    color: transparent;
    background: transparent;
    border: 0;
    border-radius: 5px;
    padding: 0;
    font-size: 13px;
    font-weight: 400;
    text-align: center;
}
QFrame#RizumDragTreeItem:hover QPushButton#RizumRemoveButton {
    color: transparent;
}
QFrame#RizumDragTreeItem[hovered="true"] QPushButton#RizumRemoveButton {
    color: transparent;
}
QPushButton#RizumRemoveButton:hover {
    color: #ff453a;
    background: rgba(255, 69, 58, 44);
    border: 0;
}
"""
    )
    layout = _QtWidgets.QVBoxLayout(window)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)

    header = _QtWidgets.QWidget()
    header.setObjectName("RizumDragHeader")
    header.setFixedHeight(40)
    header_layout = _QtWidgets.QHBoxLayout(header)
    header_layout.setContentsMargins(16, 0, 16, 0)
    title = _QtWidgets.QLabel("Pt Bridge")
    title.setObjectName("RizumDragTitle")
    header_layout.addWidget(title)
    header_layout.addStretch(1)
    header_layout.addWidget(make_svg_label("x.svg", 14))
    layout.addWidget(header)
    layout.addWidget(make_inset_separator(12, 1))

    texture_combo = make_combo_input([("M_Body", "M_Body")])
    channel_combo = make_combo_input([("BaseColor", "BaseColor")])
    texture_combo.setDisplayParts("Texture Set:", "M_Body")
    channel_combo.setDisplayParts("Channel:", "BaseColor")
    texture_combo.setCompactHeight(26)
    channel_combo.setCompactHeight(26)
    texture_combo.setPopupAlignment("right")
    channel_combo.setPopupAlignment("right")
    reset_btn = make_icon_button("reset.svg", "Reset transfer", compact=False)
    settings_btn = make_icon_button("settings.svg", "Transfer settings", compact=False)
    undo_btn = make_icon_button("undo.svg", "Undo", compact=False)
    redo_btn = make_icon_button("redo.svg", "Redo", compact=False)
    apply_btn = make_icon_button("checkmark.svg", "Apply transfer", compact=False)
    reset_btn.setProperty("accent", True)
    settings_btn.setProperty("accent", True)
    undo_btn.setProperty("accent", True)
    redo_btn.setProperty("accent", True)
    apply_btn.setProperty("accent", True)
    drag_icon_bar = make_compact_icon_toolbar(
        reset_btn,
        settings_btn,
        None,
        undo_btn,
        redo_btn,
        None,
        apply_btn,
    )
    action_bar = make_compact_action_bar(
        [texture_combo, channel_combo],
        drag_icon_bar,
        object_name="RizumDragActionBar",
        spacing=8,
    )
    layout.addWidget(action_bar)
    layout.addWidget(make_inset_separator(12, 1))

    content = _QtWidgets.QWidget()
    content.setObjectName("RizumDragContent")
    content_layout = _QtWidgets.QHBoxLayout(content)
    content_layout.setContentsMargins(16, 16, 16, 16)
    content_layout.setSpacing(16)
    source = make_column(
        "Source: Photoshop",
        "BaseColor.psd",
        [("Main_Layer", False, True), ("Details_Pass", False, False), ("Effects_Group", True, True)],
    )
    target = DropColumn(source._rizum_group)
    content_layout.addWidget(source)
    content_layout.addWidget(target)
    layout.addWidget(content, 1)

    def refresh_layout():
        action_bar.refreshLayout()
        source._rizum_group.refreshLayout()
        target.target_group.refreshLayout()

    window.refreshLayout = refresh_layout
    refresh_layout()
    return window


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
    layout.addLayout(title_row)

    tabs = QtWidgets.QTabWidget()
    tabs.setObjectName("RizumPreviewTabs")
    tabs.setDocumentMode(True)
    tabs.tabBar().setDrawBase(False)

    overview = QtWidgets.QWidget()
    overview_layout = QtWidgets.QVBoxLayout(overview)
    overview_layout.setContentsMargins(0, 0, 0, 0)
    overview_layout.setSpacing(0)
    grid = QtWidgets.QGridLayout()
    grid.setSpacing(12)
    overview_left = QtWidgets.QWidget()
    overview_left.setObjectName("RizumOverviewLeft")
    overview_left_layout = QtWidgets.QVBoxLayout(overview_left)
    overview_left_layout.setContentsMargins(0, 0, 0, 0)
    overview_left_layout.setSpacing(16)
    overview_left_layout.addWidget(
        build_bridge_preview(QtWidgets),
        0,
        QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignLeft,
    )
    overview_left_layout.addWidget(
        make_dock_actions_panel(),
        0,
        QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignHCenter,
    )
    overview_left_layout.addStretch(1)
    grid.addWidget(overview_left, 0, 0, 2, 1, QtCore.Qt.AlignmentFlag.AlignTop)
    grid.addWidget(build_font_preview(QtWidgets), 0, 1)
    grid.addWidget(build_lab(QtWidgets), 1, 1)
    grid.setColumnStretch(0, 0)
    grid.setColumnStretch(1, 1)
    overview_layout.addLayout(grid, 1)
    tabs.addTab(overview, "Overview")

    drag_page = QtWidgets.QWidget()
    drag_layout = QtWidgets.QVBoxLayout(drag_page)
    drag_layout.setContentsMargins(0, 12, 0, 0)
    drag_layout.setSpacing(0)
    drag_layout.addWidget(
        build_drag_drop_preview(QtWidgets),
        0,
        QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignHCenter,
    )
    drag_layout.addStretch(1)
    tabs.addTab(drag_page, "Drag Drop")

    settings_page = QtWidgets.QWidget()
    settings_layout = QtWidgets.QVBoxLayout(settings_page)
    settings_layout.setContentsMargins(0, 12, 0, 0)
    settings_layout.setSpacing(0)
    settings_layout.addWidget(
        build_settings_preview(QtWidgets),
        0,
        QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignHCenter,
    )
    settings_layout.addStretch(1)
    tabs.addTab(settings_page, "Settings")

    layout.addWidget(tabs, 1)

    return reload_button


def main():
    configure_preview_scaling()
    from PySide6 import QtCore, QtWidgets

    app = QtWidgets.QApplication(qt_argv())
    full_mode = "--full" in sys.argv
    watch_enabled = "--no-watch" not in sys.argv
    apply_painter_like_base(app)
    app.setStyleSheet(
        build_painter_host_preview_stylesheet()
        + build_stylesheet(mode="full" if full_mode else "overlay")
        + PREVIEW_CANVAS_STYLESHEET
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
        apply_painter_like_base(app)
        app.setStyleSheet(
            build_painter_host_preview_stylesheet()
            + build_stylesheet(mode="full" if full_mode else "overlay")
            + PREVIEW_CANVAS_STYLESHEET
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
