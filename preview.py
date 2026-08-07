"""Standalone preview for the Rizum PySide6 UI kit."""

from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path

from rizum_ui import (
    ActionButton,
    AnimatedSaveButton,
    Card,
    IconActionButton,
    SectionHeader,
    COMPACT_DOCK_DEFAULT_HEIGHT,
    COMPACT_DOCK_DEFAULT_WIDTH,
    COMPACT_DOCK_MIN_WIDTH,
    PAINTER_DIALOG_STYLE,
    PAINTER_SETTINGS_LAYOUT,
    PAINTER_WINDOW_CONTENT_RADIUS,
    PainterSettingsDialog,
    SecondaryActionButton,
    TextActionButton,
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
    install_compact_tooltip,
    make_compact_action_bar,
    make_compact_dock_card,
    make_compact_dock_layout,
    make_compact_icon_toolbar,
    make_compact_stepper,
    make_combo_input,
    make_collapsible_group,
    make_drag_collapsible_group,
    make_drag_tree_item,
    make_export_tree_item,
    make_field_row,
    make_icon_button,
    make_inset_separator,
    make_inline_checkbox_row,
    make_mock_checkbox,
    make_progress_panel,
    make_painter_window_content,
    make_segmented_control,
    make_spin_input,
    make_svg_label,
    set_compact_footer_button_width,
    update_compact_field_row,
    update_export_tree_item,
    update_inline_checkbox_row,
)
from rizum_ui.animation import fade_in
from rizum_ui.theme import default_theme

ROOT = Path(__file__).resolve().parent
PREVIEW_FILE = Path(__file__).resolve()
WATCHED_MODULES = [
    "rizum_ui.theme",
    "rizum_ui.host_style",
    "rizum_ui.stylesheet",
    "rizum_ui.settings_layout",
    "rizum_ui.components",
    "rizum_ui.animation",
    "rizum_ui",
    "view_roll_preview",
]

PREVIEW_LANGUAGES = (
    ("English", "en"),
    ("Deutsch", "de"),
    ("Español", "es"),
    ("Français", "fr"),
    ("Italiano", "it"),
    ("日本語", "ja_JP"),
    ("한국어", "ko"),
    ("Português", "pt"),
    ("简体中文", "zh_CN"),
)
_PREVIEW_SETTINGS_ORG = "Rizum"
_PREVIEW_SETTINGS_APP = "UiPrettierPreview"
_PREVIEW_TEXT = {
    "de": {
        "overview": "Übersicht",
        "drag_drop": "Drag & Drop",
        "settings": "Einstellungen",
        "view_roll": "Ansicht drehen",
        "reload": "Neu laden",
        "language": "Sprache",
        "export": "Exportieren",
        "current_stack": "Aktueller Stack",
        "all_stacks": "Alle Stacks",
        "selected_channels": "{selected} von {total} Kanälen ausgewählt",
        "cancel": "Abbrechen",
        "padding": "Randabstand",
        "bit_depth": "Bittiefe",
        "texture_set": "Texturset",
        "infinite": "Unendlich",
        "auto_open": "Photoshop automatisch öffnen",
        "auto_open_meta": "Nach erfolgreichem Export starten",
        "photoshop": "Photoshop",
        "about": "Über",
        "version": "Version",
        "auto_save": "Änderungen werden automatisch gespeichert",
        "done": "Fertig",
    },
    "es": {
        "overview": "Resumen",
        "drag_drop": "Arrastrar y soltar",
        "settings": "Configuración",
        "view_roll": "Rotación de vista",
        "reload": "Recargar",
        "language": "Idioma",
        "export": "Exportar",
        "current_stack": "Pila actual",
        "all_stacks": "Todas las pilas",
        "selected_channels": "{selected} de {total} canales seleccionados",
        "cancel": "Cancelar",
        "padding": "Margen",
        "bit_depth": "Profundidad de bits",
        "texture_set": "Conjunto de texturas",
        "infinite": "Infinito",
        "auto_open": "Abrir Photoshop automáticamente",
        "auto_open_meta": "Iniciar después de exportar correctamente",
        "photoshop": "Photoshop",
        "about": "Acerca de",
        "version": "Versión",
        "auto_save": "Los cambios se guardan automáticamente",
        "done": "Listo",
    },
    "fr": {
        "overview": "Vue d’ensemble",
        "drag_drop": "Glisser-déposer",
        "settings": "Paramètres",
        "view_roll": "Rotation de la vue",
        "reload": "Recharger",
        "language": "Langue",
        "export": "Exporter",
        "current_stack": "Pile actuelle",
        "all_stacks": "Toutes les piles",
        "selected_channels": "{selected} sur {total} canaux sélectionnés",
        "cancel": "Annuler",
        "padding": "Marge",
        "bit_depth": "Profondeur de bits",
        "texture_set": "Jeu de textures",
        "infinite": "Infini",
        "auto_open": "Ouvrir Photoshop automatiquement",
        "auto_open_meta": "Lancer après une exportation réussie",
        "photoshop": "Photoshop",
        "about": "À propos",
        "version": "Version",
        "auto_save": "Les modifications sont enregistrées automatiquement",
        "done": "Terminé",
    },
    "it": {
        "overview": "Panoramica",
        "drag_drop": "Trascina e rilascia",
        "settings": "Impostazioni",
        "view_roll": "Rotazione vista",
        "reload": "Ricarica",
        "language": "Lingua",
        "export": "Esporta",
        "current_stack": "Stack corrente",
        "all_stacks": "Tutti gli stack",
        "selected_channels": "{selected} canali su {total} selezionati",
        "cancel": "Annulla",
        "padding": "Margine",
        "bit_depth": "Profondità colore",
        "texture_set": "Set di texture",
        "infinite": "Infinito",
        "auto_open": "Apri Photoshop automaticamente",
        "auto_open_meta": "Avvia dopo un’esportazione riuscita",
        "photoshop": "Photoshop",
        "about": "Informazioni",
        "version": "Versione",
        "auto_save": "Le modifiche vengono salvate automaticamente",
        "done": "Fatto",
    },
    "ko": {
        "overview": "개요",
        "drag_drop": "드래그 앤 드롭",
        "settings": "설정",
        "view_roll": "뷰 회전",
        "reload": "다시 불러오기",
        "language": "언어",
        "export": "내보내기",
        "current_stack": "현재 스택",
        "all_stacks": "모든 스택",
        "selected_channels": "채널 {total}개 중 {selected}개 선택됨",
        "cancel": "취소",
        "padding": "패딩",
        "bit_depth": "비트 심도",
        "texture_set": "텍스처 세트",
        "infinite": "무한",
        "auto_open": "Photoshop 자동 열기",
        "auto_open_meta": "내보내기 성공 후 실행",
        "photoshop": "Photoshop",
        "about": "정보",
        "version": "버전",
        "auto_save": "변경 사항이 자동으로 저장됩니다",
        "done": "완료",
    },
    "pt": {
        "overview": "Visão geral",
        "drag_drop": "Arrastar e soltar",
        "settings": "Configurações",
        "view_roll": "Rotação da vista",
        "reload": "Recarregar",
        "language": "Idioma",
        "export": "Exportar",
        "current_stack": "Pilha atual",
        "all_stacks": "Todas as pilhas",
        "selected_channels": "{selected} de {total} canais selecionados",
        "cancel": "Cancelar",
        "padding": "Margem",
        "bit_depth": "Profundidade de bits",
        "texture_set": "Conjunto de texturas",
        "infinite": "Infinito",
        "auto_open": "Abrir o Photoshop automaticamente",
        "auto_open_meta": "Iniciar após uma exportação bem-sucedida",
        "photoshop": "Photoshop",
        "about": "Sobre",
        "version": "Versão",
        "auto_save": "As alterações são salvas automaticamente",
        "done": "Concluído",
    },
    "zh_CN": {
        "overview": "概览",
        "drag_drop": "拖放",
        "settings": "设置",
        "view_roll": "视图旋转",
        "reload": "重新载入",
        "language": "语言",
        "export": "导出",
        "current_stack": "当前堆栈",
        "all_stacks": "所有堆栈",
        "selected_channels": "已选择 {selected}/{total} 个通道",
        "cancel": "取消",
        "padding": "边缘扩展",
        "bit_depth": "位深度",
        "texture_set": "纹理集",
        "infinite": "无限",
        "auto_open": "自动打开 Photoshop",
        "auto_open_meta": "导出成功后启动",
        "photoshop": "Photoshop",
        "about": "关于",
        "version": "版本",
        "auto_save": "更改会自动保存",
        "done": "完成",
    },
    "ja_JP": {
        "overview": "概要",
        "drag_drop": "ドラッグ＆ドロップ",
        "settings": "設定",
        "view_roll": "ビュー回転",
        "reload": "再読み込み",
        "language": "言語",
        "export": "書き出し",
        "current_stack": "現在のスタック",
        "all_stacks": "すべてのスタック",
        "selected_channels": "{total} チャンネル中 {selected} 件を選択",
        "cancel": "キャンセル",
        "padding": "パディング",
        "bit_depth": "ビット深度",
        "texture_set": "テクスチャセット",
        "infinite": "無限",
        "auto_open": "Photoshopを自動起動",
        "auto_open_meta": "書き出し成功後に起動",
        "photoshop": "Photoshop",
        "about": "情報",
        "version": "バージョン",
        "auto_save": "変更は自動的に保存されます",
        "done": "完了",
    },
}


def preview_language():
    from PySide6 import QtWidgets

    app = QtWidgets.QApplication.instance()
    value = app.property("rizumPreviewLanguage") if app is not None else None
    return str(value or "en")


def preview_text(key, fallback):
    return _PREVIEW_TEXT.get(preview_language(), {}).get(key, fallback)
WATCHED_FILES = sorted(
    [PREVIEW_FILE, ROOT / "view_roll_preview.py"]
    + list((ROOT / "rizum_ui").glob("*.py"))
    + list((ROOT / "icons").glob("*.svg"))
)
PREVIEW_FLAGS = {"--full", "--no-watch", "--scale-1x"}
PREVIEW_CANVAS_STYLESHEET = """
QWidget#RizumSurface {
    background: #2b2b2b;
}

QWidget#RizumSurface QLabel#RizumPreviewToolLabel,
QWidget#RizumSurface QLabel#RizumPreviewToolLabel:hover,
QWidget#RizumSurface QLabel#RizumPreviewToolLabel:focus {
    background: transparent;
    border: 0;
    border-radius: 0;
    padding: 0;
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
    global AnimatedSaveButton
    global Card
    global IconActionButton
    global SectionHeader
    global COMPACT_DOCK_DEFAULT_HEIGHT
    global COMPACT_DOCK_DEFAULT_WIDTH
    global COMPACT_DOCK_MIN_WIDTH
    global PAINTER_DIALOG_STYLE
    global PAINTER_SETTINGS_LAYOUT
    global PAINTER_WINDOW_CONTENT_RADIUS
    global PainterSettingsDialog
    global SecondaryActionButton
    global TextActionButton
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
    global install_compact_tooltip
    global make_compact_action_bar
    global make_compact_dock_card
    global make_compact_dock_layout
    global make_compact_icon_toolbar
    global make_compact_stepper
    global make_combo_input
    global make_collapsible_group
    global make_drag_collapsible_group
    global make_drag_tree_item
    global make_export_tree_item
    global make_field_row
    global make_icon_button
    global make_inset_separator
    global make_inline_checkbox_row
    global make_mock_checkbox
    global make_progress_panel
    global make_painter_window_content
    global make_segmented_control
    global make_spin_input
    global make_svg_label
    global set_compact_footer_button_width
    global update_compact_field_row
    global update_export_tree_item
    global update_inline_checkbox_row
    global default_theme
    global fade_in

    for module_name in WATCHED_MODULES:
        module = importlib.import_module(module_name)
        importlib.reload(module)

    import rizum_ui
    import rizum_ui.animation

    ActionButton = rizum_ui.ActionButton
    AnimatedSaveButton = rizum_ui.AnimatedSaveButton
    Card = rizum_ui.Card
    IconActionButton = rizum_ui.IconActionButton
    SectionHeader = rizum_ui.SectionHeader
    COMPACT_DOCK_DEFAULT_HEIGHT = rizum_ui.COMPACT_DOCK_DEFAULT_HEIGHT
    COMPACT_DOCK_DEFAULT_WIDTH = rizum_ui.COMPACT_DOCK_DEFAULT_WIDTH
    COMPACT_DOCK_MIN_WIDTH = rizum_ui.COMPACT_DOCK_MIN_WIDTH
    PAINTER_DIALOG_STYLE = rizum_ui.PAINTER_DIALOG_STYLE
    PAINTER_SETTINGS_LAYOUT = rizum_ui.PAINTER_SETTINGS_LAYOUT
    PAINTER_WINDOW_CONTENT_RADIUS = rizum_ui.PAINTER_WINDOW_CONTENT_RADIUS
    PainterSettingsDialog = rizum_ui.PainterSettingsDialog
    SecondaryActionButton = rizum_ui.SecondaryActionButton
    TextActionButton = rizum_ui.TextActionButton
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
    install_compact_tooltip = rizum_ui.install_compact_tooltip
    make_compact_action_bar = rizum_ui.make_compact_action_bar
    make_compact_dock_card = rizum_ui.make_compact_dock_card
    make_compact_dock_layout = rizum_ui.make_compact_dock_layout
    make_compact_icon_toolbar = rizum_ui.make_compact_icon_toolbar
    make_compact_stepper = rizum_ui.make_compact_stepper
    make_combo_input = rizum_ui.make_combo_input
    make_collapsible_group = rizum_ui.make_collapsible_group
    make_drag_collapsible_group = rizum_ui.make_drag_collapsible_group
    make_drag_tree_item = rizum_ui.make_drag_tree_item
    make_export_tree_item = rizum_ui.make_export_tree_item
    make_field_row = rizum_ui.make_field_row
    make_icon_button = rizum_ui.make_icon_button
    make_inset_separator = rizum_ui.make_inset_separator
    make_inline_checkbox_row = rizum_ui.make_inline_checkbox_row
    make_mock_checkbox = rizum_ui.make_mock_checkbox
    make_progress_panel = rizum_ui.make_progress_panel
    make_painter_window_content = rizum_ui.make_painter_window_content
    make_segmented_control = rizum_ui.make_segmented_control
    make_spin_input = rizum_ui.make_spin_input
    make_svg_label = rizum_ui.make_svg_label
    set_compact_footer_button_width = rizum_ui.set_compact_footer_button_width
    update_compact_field_row = rizum_ui.update_compact_field_row
    update_export_tree_item = rizum_ui.update_export_tree_item
    update_inline_checkbox_row = rizum_ui.update_inline_checkbox_row
    default_theme = rizum_ui.default_theme
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
    from PySide6 import QtCore, QtWidgets as _QtWidgets

    layout_spec = PAINTER_SETTINGS_LAYOUT
    theme = {
        **dict(PAINTER_DIALOG_STYLE),
        "border": "#3a3b3e",
    }

    window = PainterSettingsDialog()
    window.setObjectName("RizumExportWindow")
    window.setWindowFlags(QtCore.Qt.WindowType.Widget)
    window.setSettingsFrameWidth(0)
    window.setSettingsFrameBottomWidth(0)
    window.setSettingsBottomEdgeExtensionEnabled(False)
    window.setSizePolicy(
        _QtWidgets.QSizePolicy.Policy.Fixed,
        _QtWidgets.QSizePolicy.Policy.Fixed,
    )
    surface_layout = window.settingsSurfaceLayout()
    content = make_painter_window_content(
        theme["surface"],
        rounded=False,
        bottom_radius=PAINTER_WINDOW_CONTENT_RADIUS,
    )
    content_layout = content.contentLayout()
    surface_layout.addWidget(content, 1)

    mode_combo = make_combo_input(
        [
            (preview_text("current_stack", "Current Stack"), "current"),
            (preview_text("all_stacks", "All Stacks"), "all"),
        ]
    )
    mode_combo.setObjectName("RizumExportScopeInput")
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
        height=layout_spec.row_height.design,
        margins=(
            layout_spec.body_margin_x.design,
            0,
            layout_spec.body_margin_x.design,
            0,
        ),
        spacing=layout_spec.row_spacing,
    )
    content_layout.addWidget(top_controls)
    top_separator = make_inset_separator(
        layout_spec.body_margin_x.design,
        thickness=1,
    )
    top_separator.setObjectName("RizumExportTopDivider")
    content_layout.addWidget(top_separator)

    tree_scroll = _QtWidgets.QScrollArea()
    tree_scroll.setObjectName("RizumExportTreeScroll")
    tree_scroll.setWidgetResizable(True)
    tree_scroll.setFrameShape(_QtWidgets.QFrame.Shape.NoFrame)
    tree_scroll.setHorizontalScrollBarPolicy(
        QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff
    )
    tree_scroll.setVerticalScrollBarPolicy(
        QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff
    )
    tree_scroll.viewport().setAutoFillBackground(False)
    internal_scrollbar = tree_scroll.verticalScrollBar()
    internal_scrollbar.setObjectName("RizumExportInternalScrollbar")
    internal_scrollbar.setStyleSheet(
        "QScrollBar#RizumExportInternalScrollbar {"
        " min-width: 0; max-width: 0; width: 0;"
        " background: transparent; border: 0; }"
    )
    internal_scrollbar.setFixedWidth(0)

    # Painter may reserve space for its native scrollbar. The preview mirrors
    # the live dialog's fixed-width proxy so horizontal alignment stays stable.
    tree_scrollbar = _QtWidgets.QScrollBar(QtCore.Qt.Orientation.Vertical)
    tree_scrollbar.setObjectName("RizumExportTreeScrollbar")
    tree_scrollbar.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
    tree_scrollbar.valueChanged.connect(internal_scrollbar.setValue)
    internal_scrollbar.valueChanged.connect(tree_scrollbar.setValue)

    tree_container = _QtWidgets.QWidget()
    tree_container.setObjectName("RizumExportTreeContainer")
    tree_container_layout = _QtWidgets.QHBoxLayout(tree_container)
    tree_container_layout.setContentsMargins(0, 0, 0, 0)
    tree_container_layout.setSpacing(0)
    tree_container_layout.addWidget(tree_scroll, 1)
    tree_container_layout.addWidget(tree_scrollbar)

    tree = _QtWidgets.QFrame()
    tree.setObjectName("RizumExportTree")
    tree.setSizePolicy(
        _QtWidgets.QSizePolicy.Policy.Expanding,
        _QtWidgets.QSizePolicy.Policy.Fixed,
    )
    tree_layout = _QtWidgets.QVBoxLayout(tree)
    tree_layout.setContentsMargins(12, 8, 12, 8)
    tree_layout.setSpacing(layout_spec.body_spacing.design)
    tree_layout.addStretch(1)
    tree_scroll.setWidget(tree)
    content_layout.addWidget(tree_container, 1)

    groups = []
    target_specs = [
        ("M_body", ["basecolor", "User1"]),
        ("M_clothes", ["Base Color"]),
        ("M_coat", ["Base Color", "Normal"]),
        ("M_face", ["Base Color", "Opacity"]),
        ("M_hair_back1", ["Base Color"]),
        ("M_hair_back2", ["Base Color"]),
        ("M_hair_front", ["Base Color", "Opacity"]),
        ("M_shoes", ["Base Color"]),
        ("M_skirt", ["Base Color"]),
    ]

    def make_tree_item(name, checkbox, meta="", child=False):
        return make_export_tree_item(name, checkbox, meta=meta, child=child)

    def selection_counter(selected, total):
        return (
            f'<span style="color:{theme["text"]};">{selected}</span>'
            f'<span style="color:{theme["faint"]};"> / {total}</span>'
        )

    def selection_tooltip(selected, total):
        template = preview_text(
            "selected_channels",
            "{selected} of {total} channels selected",
        )
        return template.format(selected=selected, total=total)

    def update_selection_summary(group, selected):
        total = len(group["children"])
        tooltip = selection_tooltip(selected, total)
        group["widget"].refreshLayout(
            subtitle_text=selection_counter(selected, total)
        )
        group["subtitle"].setCompactTooltipText(tooltip)
        group["subtitle"].setAccessibleName(tooltip)

    def update_parent(group):
        checked_count = sum(1 for child in group["children"] if child.isChecked())
        if checked_count == 0:
            group["parent"].setChecked(False)
        elif checked_count == len(group["children"]):
            group["parent"].setChecked(True)
        else:
            group["parent"].setIndeterminate(True)
        update_selection_summary(group, checked_count)
        refresh_export_state()

    def add_group(name, children, checked):
        parent_cb = make_mock_checkbox(checked)
        child_cbs = [make_mock_checkbox(checked) for _ in children]
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
            update_parent(g)

        parent_cb.mousePressEvent = parent_mouse
        group_frame = make_collapsible_group(
            name,
            selection_counter(len(children) if checked else 0, len(children)),
            children=child_rows,
            trailing_widget=parent_cb,
            expanded=True,
        )
        group["widget"] = group_frame
        subtitle = group_frame.findChild(
            _QtWidgets.QLabel,
            "RizumCollapsibleSubtitle",
        )
        subtitle.setTextFormat(QtCore.Qt.TextFormat.RichText)
        install_compact_tooltip(
            subtitle,
            selection_tooltip(len(children) if checked else 0, len(children)),
        )
        group["subtitle"] = subtitle
        update_selection_summary(group, len(children) if checked else 0)
        tree_layout.insertWidget(tree_layout.count() - 1, group_frame)
        groups.append(group)
        content_frame = group_frame._rizum_content
        sync_group_height = content_frame._height_changed

        def sync_preview_tree_height(value, sync_group=sync_group_height):
            sync_group(value)
            sync_tree_content_height()

        content_frame._height_changed = sync_preview_tree_height

    footer_separator = make_inset_separator(
        layout_spec.footer_margin_x.design,
        thickness=1,
    )
    footer_separator.setObjectName("RizumExportFooterDivider")
    content_layout.addWidget(footer_separator)

    footer = _QtWidgets.QWidget()
    footer.setObjectName("RizumExportFooter")
    footer_outer = _QtWidgets.QVBoxLayout(footer)
    footer_outer.setContentsMargins(0, 0, 0, 0)
    footer_outer.setSpacing(0)
    footer_row = _QtWidgets.QWidget()
    footer_row.setObjectName("RizumExportFooterRow")
    footer_layout = _QtWidgets.QHBoxLayout(footer_row)
    footer_layout.setContentsMargins(
        layout_spec.footer_margin_x.design,
        0,
        layout_spec.footer_margin_x.design,
        0,
    )
    footer_layout.setSpacing(layout_spec.footer_button_spacing)
    cancel = SecondaryActionButton(
        preview_text("cancel", "Cancel"),
        theme["control"],
        theme["control_hover"],
        theme["control_pressed"],
        theme["text"],
        default_theme.radius_small,
    )
    cancel.setObjectName("RizumExportCancel")
    export = AnimatedSaveButton(preview_text("export", "Export"))
    export.setObjectName("RizumExportConfirm")
    footer_layout.addWidget(cancel)
    footer_layout.addStretch(1)
    footer_layout.addWidget(export)
    footer_outer.addWidget(footer_row)
    content_layout.addWidget(footer)

    expand_btn.clicked.connect(
        lambda: [group["widget"].setExpanded(True) for group in groups]
    )
    collapse_btn.clicked.connect(
        lambda: [group["widget"].setExpanded(False) for group in groups]
    )

    def refresh_export_state():
        selected = any(
            checkbox.isChecked()
            for group in groups
            for checkbox in group["children"]
        )
        export.setDirty(selected, animate=window.isVisible())

    def set_all_checked(checked):
        for group in groups:
            for checkbox in [group["parent"], *group["children"]]:
                checkbox.setChecked(checked)
            update_parent(group)
        refresh_export_state()

    select_all_btn.clicked.connect(lambda: set_all_checked(True))
    select_none_btn.clicked.connect(lambda: set_all_checked(False))

    def clear_groups():
        for group in groups:
            tree_layout.removeWidget(group["widget"])
            group["widget"].deleteLater()
        groups.clear()

    def refresh_scope(*_args):
        clear_groups()
        show_all = mode_combo.currentData() == "all"
        specs = target_specs if show_all else target_specs[:1]
        for name, channels in specs:
            add_group(name, channels, checked=not show_all)
        internal_scrollbar.setValue(0)
        refresh_export_state()
        apply_scale()

    mode_combo.currentIndexChanged.connect(refresh_scope)

    def metric(value, minimum=None):
        return window.settingsMetric(value, minimum)

    def apply_visual_style():
        window.setProperty("theme", "dark")
        content.setPainterContentColor(theme["surface"])
        window._update_surface_stylesheet()
        item_px = metric(13)
        meta_px = metric(11)
        surface = window.settingsSurface()
        surface.setStyleSheet(
            surface.styleSheet()
            + f"""
QFrame#RizumPainterSettingsSurface {{
    background: {theme["surface"]};
}}
QWidget#RizumExportTopControls,
QWidget#RizumExportTreeContainer,
QScrollArea#RizumExportTreeScroll,
QScrollArea#RizumExportTreeScroll > QWidget > QWidget,
QFrame#RizumExportTree,
QWidget#RizumExportFooter,
QWidget#RizumExportFooterRow,
QWidget#RizumExportTopDivider,
QWidget#RizumExportFooterDivider,
QFrame#RizumCollapsibleHeader,
QFrame#RizumCollapsibleContent,
QWidget#RizumCollapsibleContentInner,
QFrame#RizumExportTreeItemHost {{
    background: transparent;
    border: 0;
}}
QScrollBar#RizumExportTreeScrollbar {{
    background: transparent;
    border: 0;
    margin: 0;
    width: {metric(10, 8)}px;
}}
QScrollBar#RizumExportTreeScrollbar::handle:vertical {{
    background: #515151;
    border: 0;
    border-radius: {max(3, metric(4, 3))}px;
    min-height: {metric(28, 21)}px;
    margin: {metric(2, 1)}px;
}}
QScrollBar#RizumExportTreeScrollbar::handle:vertical:hover {{
    background: #686868;
}}
QScrollBar#RizumExportTreeScrollbar::handle:vertical:pressed {{
    background: #777777;
}}
QScrollBar#RizumExportTreeScrollbar[scrollable="false"]::handle:vertical {{
    background: transparent;
}}
QScrollBar#RizumExportTreeScrollbar::add-line:vertical,
QScrollBar#RizumExportTreeScrollbar::sub-line:vertical {{
    background: transparent;
    border: 0;
    height: 0;
}}
QScrollBar#RizumExportTreeScrollbar::add-page:vertical,
QScrollBar#RizumExportTreeScrollbar::sub-page:vertical {{
    background: transparent;
}}
QWidget#RizumExportTopDivider QFrame#RizumInsetSeparator,
QWidget#RizumExportFooterDivider QFrame#RizumInsetSeparator {{
    background: {theme["border"]};
}}
QFrame#RizumExportScopeInput {{
    background: transparent;
    border: 0;
    border-radius: {default_theme.radius_small}px;
}}
QFrame#RizumExportScopeInput:focus {{
    background: transparent;
}}
QFrame#RizumExportScopeInput:hover {{
    background: {default_theme.action_hover};
}}
QFrame#RizumCollapsibleGroup {{
    background: transparent;
    border: 0;
    border-radius: {default_theme.radius_small}px;
}}
QFrame#RizumCollapsibleGroup:hover {{
    background: {theme["control_pressed"]};
    border: 0;
}}
QFrame#RizumExportTreeItem {{
    background: transparent;
    border: 0;
    border-radius: {default_theme.radius_small}px;
}}
QFrame#RizumExportTreeItem[hovered="true"][child="true"] {{
    background: {default_theme.action_hover};
}}
QFrame#RizumExportTreeItem[pressed="true"][child="true"] {{
    background: {default_theme.action_pressed};
}}
QLabel#RizumExportItemName,
QLabel#RizumCollapsibleTitle {{
    color: {theme["text"]};
    font-size: {item_px}px;
    font-weight: 500;
    background: transparent;
    border: 0;
}}
QLabel#RizumExportMeta,
QLabel#RizumCollapsibleSubtitle {{
    color: {theme["muted"]};
    font-size: {meta_px}px;
    font-weight: 500;
    background: transparent;
    border: 0;
}}
QLabel#RizumSvgLabel,
QLabel#RizumSvgLabel:hover {{
    background: transparent;
    border: 0;
}}
"""
        )
        for button in (expand_btn, collapse_btn, select_all_btn, select_none_btn):
            button.setProperty("iconColor", theme["muted"])
            button.setProperty("iconAccentColor", theme["muted"])
            button.setProperty("iconHoverColor", theme["text"])
            button.update()

    def tree_content_height():
        margins = tree_layout.contentsMargins()
        height = margins.top() + margins.bottom()
        for index, group in enumerate(groups):
            if index:
                height += tree_layout.spacing()
            height += group["widget"].height()
        return height

    def first_group_prefix_height(group, maximum):
        widget = group["widget"]
        group_margins = widget.layout().contentsMargins()
        base = (
            group_margins.top()
            + widget._rizum_header.height()
            + group_margins.bottom()
        )
        if not widget.isExpanded() or base >= maximum:
            return min(base, maximum)

        height = base
        content_group_layout = widget._rizum_content_layout
        for index, row in enumerate(group["rows"]):
            addition = row.height()
            if index:
                addition += content_group_layout.spacing()
            if height + addition > maximum:
                break
            height += addition
        return height

    def quantized_tree_height(content_height, maximum):
        if content_height <= maximum or not groups:
            return content_height

        margins = tree_layout.contentsMargins()
        height = margins.top()
        complete_groups = 0
        truncated = False
        for group in groups:
            spacing = tree_layout.spacing() if complete_groups else 0
            candidate = (
                height
                + spacing
                + group["widget"].height()
                + margins.bottom()
            )
            if candidate > maximum:
                truncated = True
                if not complete_groups:
                    available = max(
                        0,
                        maximum - height - spacing - margins.bottom(),
                    )
                    height += spacing + first_group_prefix_height(
                        group,
                        available,
                    )
                break
            height += spacing + group["widget"].height()
            complete_groups += 1
        if truncated:
            return max(1, height + tree_layout.spacing())
        return max(1, height + margins.bottom())

    def set_tree_scrollable(scrolling):
        scrolling = bool(scrolling)
        if tree_scrollbar.property("scrollable") == scrolling:
            return
        tree_scrollbar.setProperty("scrollable", scrolling)
        tree_scrollbar.style().unpolish(tree_scrollbar)
        tree_scrollbar.style().polish(tree_scrollbar)
        tree_scrollbar.update()

    def sync_scrollbar_range(_minimum, _maximum):
        maximum = max(0, tree.height() - tree_scroll.viewport().height())
        tree_scrollbar.setRange(0, maximum)
        tree_scrollbar.setPageStep(internal_scrollbar.pageStep())
        tree_scrollbar.setSingleStep(internal_scrollbar.singleStep())
        tree_scrollbar.setValue(internal_scrollbar.value())
        set_tree_scrollable(maximum > 0)

    def sync_tree_content_height():
        tree_layout.activate()
        content_height = tree_content_height()
        tree.setFixedHeight(content_height)
        viewport_height = max(1, tree_scroll.viewport().height())
        scroll_maximum = max(0, content_height - viewport_height)
        tree_scrollbar.setRange(0, scroll_maximum)
        tree_scrollbar.setPageStep(viewport_height)
        tree_scrollbar.setSingleStep(internal_scrollbar.singleStep())
        tree_scrollbar.setValue(min(internal_scrollbar.value(), scroll_maximum))
        scrolling = scroll_maximum > 0
        set_tree_scrollable(scrolling)
        if not scrolling:
            internal_scrollbar.setValue(0)

    internal_scrollbar.rangeChanged.connect(sync_scrollbar_range)

    old_tree_scroll_resize = tree_scroll.resizeEvent

    def tree_scroll_resize(event):
        old_tree_scroll_resize(event)
        QtCore.QTimer.singleShot(0, sync_tree_content_height)

    tree_scroll.resizeEvent = tree_scroll_resize

    def footer_button_width(button, minimum=56, maximum=112):
        scale = window.settingsUiScale()
        width = button.sizeHint().width() + metric(16, 12)
        return max(
            metric(minimum),
            min(int(round(maximum * scale)), width),
        )

    def required_width():
        margin = layout_spec.body_margin_x.resolve(window)
        toolbar_width = compact_action_bar_width(
            [mode_combo],
            icon_bar,
            minimum=layout_spec.dialog_width.resolve(window),
            horizontal_margins=margin * 2,
            spacing=layout_spec.row_spacing,
            spacing_budget=layout_spec.row_spacing,
        )
        footer_width = (
            margin * 2
            + cancel.width()
            + export.width()
            + layout_spec.footer_button_spacing
        )
        return max(
            layout_spec.dialog_width.resolve(window),
            toolbar_width,
            footer_width,
        )

    def apply_scale():
        margin = layout_spec.body_margin_x.resolve(window)
        top_controls.setFixedHeight(layout_spec.row_height.resolve(window))
        top_controls.layout().setContentsMargins(margin, 0, margin, 0)
        top_controls.layout().setSpacing(layout_spec.row_spacing)
        mode_combo.setCompactHeight(layout_spec.control_height.resolve(window))
        mode_combo.fitToContents()

        icon_frame = metric(22, 17)
        icon_size = metric(16, 12)
        for button in (expand_btn, collapse_btn, select_all_btn, select_none_btn):
            button.setFixedSize(icon_frame, icon_frame)
            button.setPaintedIconSize(icon_size)
            if hasattr(button, "setCompactTooltipScale"):
                button.setCompactTooltipScale(window.settingsUiScale())
        for separator in icon_bar.findChildren(_QtWidgets.QFrame):
            if separator.width() == 1:
                separator.setFixedHeight(metric(14, 11))

        tree_margin_x = metric(12, 9)
        tree_margin_y = metric(8, 6)
        tree_layout.setContentsMargins(
            tree_margin_x,
            tree_margin_y,
            tree_margin_x,
            tree_margin_y,
        )
        tree_layout.setSpacing(layout_spec.body_spacing.resolve(window))
        checkbox_size = metric(14, 11)
        group_height = metric(36, 27)
        child_height = metric(32, 24)
        for group in groups:
            for checkbox in (group["parent"], *group["children"]):
                checkbox.setSize(checkbox_size)
            group["subtitle"].setFixedWidth(metric(42, 32))
            group["subtitle"].setCompactTooltipScale(window.settingsUiScale())
            group["widget"].setCompactHeight(group_height)
            for row in group["rows"]:
                row.setRightInset(metric(4, 3), metric(4, 3))
                update_export_tree_item(row, minimum_height=child_height)
            group["widget"].refreshLayout()

        tree_layout.activate()
        content_height = tree_content_height()
        viewport_height = quantized_tree_height(
            content_height,
            metric(500, 375),
        )
        tree.setFixedHeight(content_height)
        tree_container.setFixedHeight(viewport_height)
        tree_scroll.setFixedHeight(viewport_height)
        internal_scrollbar.setFixedWidth(0)
        scrollbar_gutter = metric(10, 8)
        tree_scrollbar.setFixedWidth(scrollbar_gutter)
        top_controls.layout().setContentsMargins(
            margin,
            0,
            margin + scrollbar_gutter,
            0,
        )
        set_tree_scrollable(content_height > viewport_height)

        footer_margin = layout_spec.footer_margin_x.resolve(window)
        footer_top = layout_spec.footer_top.resolve(window)
        footer_gap = layout_spec.footer_gap.resolve(window)
        footer_bottom = layout_spec.footer_bottom.resolve(window)
        footer_row_height = layout_spec.footer_row_height.resolve(window)
        footer_outer.setContentsMargins(
            0,
            footer_top + footer_gap,
            0,
            footer_bottom,
        )
        footer_row.setFixedHeight(footer_row_height)
        footer.setFixedHeight(
            footer_top + footer_gap + footer_row_height + footer_bottom
        )
        footer_layout.setContentsMargins(footer_margin, 0, footer_margin, 0)
        footer_separator.layout().setContentsMargins(
            footer_margin, 0, footer_margin, 0
        )
        top_separator.layout().setContentsMargins(margin, 0, margin, 0)
        footer_button_height = layout_spec.footer_button_height.resolve(window)
        for button in (cancel, export):
            button.setCompactHeight(footer_button_height)
            button.setFixedWidth(footer_button_width(button))

        apply_visual_style()
        window.setFixedWidth(required_width())
        window.setFixedHeight(
            top_controls.height()
            + top_separator.height()
            + viewport_height
            + footer_separator.height()
            + footer.height()
        )
        window.updateGeometry()

    def refresh_layout():
        top_controls.refreshLayout()
        for group in groups:
            for row in group["rows"]:
                row.refreshLayout()
            group["widget"].refreshLayout()
        apply_scale()

    window.refreshLayout = refresh_layout
    window.settingsUiScaleChanged.connect(lambda _scale: apply_scale())
    refresh_scope()
    window._rizum_top_controls = top_controls
    window._rizum_tree = tree
    window._rizum_tree_scroll = tree_scroll
    window._rizum_tree_scrollbar = tree_scrollbar
    window._rizum_scope_combo = mode_combo
    window._rizum_groups = groups
    window._rizum_footer = footer
    window._rizum_footer_row = footer_row
    window._rizum_cancel_button = cancel
    window._rizum_export_button = export
    return window


def build_font_preview_original(QtWidgets):
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
        return compact_label_width(
            ["Size", "Font"], widget=panel, minimum=28, maximum=56, padding=6
        )

    current_label_width = label_width()
    size_control = make_spin_input(1.0)
    size_row = make_field_row(
        "Size",
        size_control,
        label_width=current_label_width,
        gap=8,
        width=120,
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
    hint_widget = make_inline_checkbox_row(
        "No hinting", no_hinting, minimum=88, maximum=150
    )
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

    def scale_control_width():
        return compact_text_width(
            "2.00", widget=size_control, minimum=120, maximum=150, padding=78
        )

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
        for button in (folder_btn, refresh_btn):
            if hasattr(button, "setCompactTooltipScale"):
                button.setCompactTooltipScale(scale)

        next_label_width = label_width()
        tool_row.setContentsMargins(next_label_width + 8, -6, 0, 2)
        update_compact_field_row(
            size_row,
            label_width=next_label_width,
            control_width=scale_control_width(),
        )
        update_compact_field_row(font_row, label_width=next_label_width)
        update_inline_checkbox_row(
            hint_widget, "No hinting", minimum=88, maximum=150
        )
        reset_button.refreshLayout(minimum=68, maximum=118)
        apply_button.refreshLayout(minimum=72, maximum=112)
        panel.setMinimumWidth(0)
        panel.setMinimumWidth(
            max(COMPACT_DOCK_MIN_WIDTH, panel.minimumSizeHint().width())
        )
        panel.setFixedWidth(panel.minimumWidth())

    refresh_metrics()
    size_control.valueChanged.connect(refresh_metrics)
    panel._rizum_size_control_variant = "original"
    panel._rizum_size_control = size_control
    panel._rizum_reset_button = reset_button
    panel._rizum_save_button = apply_button
    return panel


def build_font_preview(QtWidgets, *, size_control_variant="spin"):
    from PySide6 import QtCore, QtGui
    from PySide6 import QtWidgets as _QtWidgets

    if size_control_variant not in {"spin", "compact"}:
        raise ValueError(f"Unsupported UI Font size control: {size_control_variant}")

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

    current_label_width = label_width()
    if size_control_variant == "compact":
        size_control = make_compact_stepper(
            1.0,
            minimum=0.75,
            maximum=2.0,
            step=0.05,
            decimals=2,
        )
    else:
        size_control = make_spin_input(1.0)
    size_row = make_field_row(
        "Size",
        size_control,
        label_width=current_label_width,
        gap=8,
        width=120,
    )
    scale_suffix = QtWidgets.QLabel("×")
    scale_suffix.setObjectName("RizumHintLabel")
    scale_suffix.setAttribute(
        QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents,
        True,
    )
    size_row.layout().insertWidget(size_row.layout().count() - 1, scale_suffix)
    main_layout.addWidget(size_row)

    font_combo = make_combo_input()
    for family in ["System Default", "MiSans", "MiSans Demibold", "Inter", "Segoe UI"]:
        font_combo.addItem(family, family)
    font_combo.setFitToContents(False)
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
    undo_button = make_icon_button("undo.svg", "Undo unsaved changes")
    undo_button.setProperty("accent", True)
    reset_button = TextActionButton("Reset")
    save_button = AnimatedSaveButton("Save")
    footer_layout.addWidget(undo_button)
    footer_layout.addWidget(reset_button)
    footer_layout.addStretch(1)
    footer_layout.addWidget(save_button)
    footer_outer.addWidget(footer_row, 1)
    card_layout.addWidget(footer_widget)

    saved_state = {
        "size": 1.0,
        "font": font_combo.currentData(),
        "hinting": no_hinting.isChecked(),
    }
    updating_state = False

    def current_state():
        return {
            "size": round(float(size_control.value()), 2),
            "font": font_combo.currentData(),
            "hinting": no_hinting.isChecked(),
        }

    def refresh_action_state(*_args):
        if updating_state:
            return
        dirty = current_state() != saved_state
        save_button.setDirty(dirty, animate=panel.isVisible())
        undo_button.setEnabled(dirty)

    def set_state(state):
        nonlocal updating_state
        updating_state = True
        try:
            size_control.setValue(state["size"])
            font_index = font_combo.findData(state["font"])
            font_combo.setCurrentIndex(max(0, font_index))
            no_hinting.setChecked(state["hinting"])
        finally:
            updating_state = False
        refresh_metrics(state["size"])
        refresh_action_state()

    def reset_to_defaults():
        set_state({"size": 1.0, "font": "System Default", "hinting": True})

    def save_state():
        saved_state.update(current_state())
        undo_button.setEnabled(False)
        save_button.showSavedFeedback()

    original_hinting_press = no_hinting.mousePressEvent

    def hinting_press(event):
        original_hinting_press(event)
        refresh_action_state()

    no_hinting.mousePressEvent = hinting_press
    undo_button.clicked.connect(lambda: set_state(saved_state))
    reset_button.clicked.connect(reset_to_defaults)
    save_button.clicked.connect(save_state)
    font_combo.currentIndexChanged.connect(refresh_action_state)

    def refresh_metrics(scale=None):
        scale = float(scale if scale is not None else size_control.value())

        def metric(value, minimum=None):
            result = int(round(value * scale))
            if minimum is not None:
                result = max(minimum, result)
            return result

        point_size = base_size * scale
        panel.setStyleSheet(
            base_panel_stylesheet
            + f"""
QWidget#RizumUiFontPreview,
QWidget#RizumUiFontPreview QLabel#RizumFieldLabel,
QWidget#RizumUiFontPreview QLabel#RizumHintLabel,
QWidget#RizumUiFontPreview QLabel#RizumMockText,
QWidget#RizumUiFontPreview QMenu#RizumPopupMenu {{
    font-size: {point_size:.2f}pt;
}}
"""
        )
        next_font = QtGui.QFont(base_font)
        next_font.setPointSizeF(point_size)
        for widget in [panel, *panel.findChildren(_QtWidgets.QWidget)]:
            widget.setFont(next_font)

        row_height = metric(32, 24)
        for row, control in ((size_row, size_control), (font_row, font_combo)):
            row.setFixedHeight(row_height)
            control.setCompactHeight(row_height)

        icon_frame = metric(22, 17)
        icon_size = metric(16, 12)
        for button in (folder_btn, refresh_btn, undo_button):
            button.setFixedSize(icon_frame, icon_frame)
            button.setPaintedIconSize(icon_size)
            if hasattr(button, "setCompactTooltipScale"):
                button.setCompactTooltipScale(scale)

        checkbox_size = metric(14, 11)
        no_hinting.setSize(checkbox_size)

        main_layout.setContentsMargins(
            metric(12, 9),
            metric(12, 9),
            metric(12, 9),
            metric(6, 5),
        )
        main_layout.setSpacing(metric(10, 8))

        next_label_width = label_width()
        field_gap = metric(8, 6)
        size_row.layout().setSpacing(field_gap)
        font_row.layout().setSpacing(field_gap)
        tool_row.setContentsMargins(
            next_label_width + field_gap,
            -metric(6, 5),
            0,
            metric(2, 2),
        )
        icon_group.setSpacing(metric(4, 3))
        update_compact_field_row(
            size_row,
            label_width=next_label_width,
            control_width=metric(120, 90),
        )
        update_compact_field_row(font_row, label_width=next_label_width)
        font_combo.setMinimumWidth(metric(54, 41))
        update_inline_checkbox_row(
            hint_widget,
            "No hinting",
            minimum=metric(88, 66),
            maximum=metric(150, 113),
        )

        footer_height = metric(48, 36)
        footer_widget.setFixedHeight(footer_height)
        footer_layout.setContentsMargins(metric(10, 8), 0, metric(10, 8), 0)
        footer_layout.setSpacing(metric(8, 6))
        footer_button_height = metric(26, 20)
        reset_button.setCompactHeight(footer_button_height)
        save_button.setCompactHeight(footer_button_height)
        save_button.setFixedWidth(
            compact_footer_button_width(
                save_button,
                minimum=metric(64, 48),
                maximum=metric(112, 84),
            )
        )

        panel.setMinimumWidth(0)
        panel.setMinimumWidth(
            max(metric(COMPACT_DOCK_MIN_WIDTH, 188), panel.minimumSizeHint().width())
        )
        panel.setFixedWidth(panel.minimumWidth())
        panel.setMinimumHeight(metric(COMPACT_DOCK_DEFAULT_HEIGHT, 138))
        panel.setFixedHeight(max(panel.minimumHeight(), panel.minimumSizeHint().height()))

    refresh_metrics()
    refresh_action_state()

    def size_changed(value):
        refresh_metrics(value)
        refresh_action_state()

    size_control.valueChanged.connect(size_changed)
    panel._rizum_size_control_variant = size_control_variant
    panel._rizum_size_control = size_control
    panel._rizum_font_combo = font_combo
    panel._rizum_hinting_checkbox = no_hinting
    panel._rizum_icon_buttons = (folder_btn, refresh_btn, undo_button)
    panel._rizum_footer = footer_widget
    panel._rizum_undo_button = undo_button
    panel._rizum_reset_button = reset_button
    panel._rizum_save_button = save_button
    return panel


def build_font_comparison(QtWidgets):
    from PySide6 import QtCore

    comparison = QtWidgets.QWidget()
    comparison.setObjectName("RizumUiFontCompare")
    comparison_layout = QtWidgets.QHBoxLayout(comparison)
    comparison_layout.setContentsMargins(0, 0, 0, 0)
    comparison_layout.setSpacing(12)
    candidates = []
    for title, builder in (
        ("ORIGINAL", lambda: build_font_preview_original(QtWidgets)),
        (
            "KIMI K3",
            lambda: build_font_preview(
                QtWidgets,
                size_control_variant="compact",
            ),
        ),
        (
            "KIMI K3 + CURRENT STEPPER",
            lambda: build_font_preview(
                QtWidgets,
                size_control_variant="spin",
            ),
        ),
    ):
        candidate = QtWidgets.QWidget()
        candidate.setObjectName("RizumUiFontCandidate")
        candidate_layout = QtWidgets.QVBoxLayout(candidate)
        candidate_layout.setContentsMargins(0, 0, 0, 0)
        candidate_layout.setSpacing(6)
        candidate_label = QtWidgets.QLabel(title)
        candidate_label.setObjectName("RizumPreviewToolLabel")
        candidate_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        candidate_layout.addWidget(candidate_label)
        panel = builder()
        candidate_layout.addWidget(
            panel,
            0,
            QtCore.Qt.AlignmentFlag.AlignTop,
        )
        candidate_layout.addStretch(1)
        comparison_layout.addWidget(candidate)
        candidates.append(panel)
    comparison._rizum_candidates = candidates
    return comparison


def build_dock_toolbar_preview(QtWidgets):
    """Build K3's single-flex-element dock toolbar proposal.

    Preview-only counterpart to the original three-tile
    ``make_dock_actions_panel``: Export owns all surplus width so its two
    compact utilities remain attached with a constant gap at every width.
    """
    from PySide6 import QtCore, QtWidgets as _QtWidgets

    theme = dict(PAINTER_DIALOG_STYLE)
    app = _QtWidgets.QApplication.instance()
    scale = float(app.property("rizumUiFontScale") or 1.0) if app is not None else 1.0

    def metric(value, minimum=None):
        result = int(round(value * scale))
        if minimum is not None:
            result = max(minimum, result)
        return result

    toolbar = _QtWidgets.QWidget()
    toolbar.setObjectName("RizumDockToolbar")
    toolbar.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)
    toolbar.setStyleSheet(
        "QWidget#RizumDockToolbar { background: transparent; border: 0; }"
    )
    row = _QtWidgets.QHBoxLayout(toolbar)
    margin = metric(12, 9)
    row.setContentsMargins(margin, 0, margin, 0)
    row.setSpacing(metric(6, 5))

    export = IconActionButton(
        preview_text("export", "Export"),
        "action-export.svg",
        theme["accent"],
        theme["accent_hover"],
        theme["accent_pressed"],
        theme["accent_text"],
        default_theme.radius_small,
    )
    export.setObjectName("RizumDockToolbarExport")
    export.setCompactHeight(metric(28, 21))
    export.setMinimumWidth(metric(96, 72))
    export.setSizePolicy(
        _QtWidgets.QSizePolicy.Policy.Expanding,
        _QtWidgets.QSizePolicy.Policy.Fixed,
    )
    row.addWidget(export, 1)

    icon_frame = metric(22, 17)
    icon_size = metric(16, 12)

    bridge = make_icon_button("action-bridge.svg", "Open bridge app")
    bridge.setObjectName("RizumDockToolbarBridge")
    bridge.setFixedSize(icon_frame, icon_frame)
    bridge.setPaintedIconSize(icon_size)
    bridge.setEnabled(False)
    if hasattr(bridge, "setCompactTooltipScale"):
        bridge.setCompactTooltipScale(scale)
    # Disabled widgets never receive hover events, so the compact tooltip
    # cannot pop up; keep a native tooltip as the reachable fallback.
    bridge.setAttribute(QtCore.Qt.WidgetAttribute.WA_AlwaysShowToolTips, True)
    bridge.setToolTip("Open bridge app (unavailable)")
    row.addWidget(bridge)

    settings = make_icon_button("settings.svg", "Settings")
    settings.setObjectName("RizumDockToolbarSettings")
    settings.setFixedSize(icon_frame, icon_frame)
    settings.setPaintedIconSize(icon_size)
    if hasattr(settings, "setCompactTooltipScale"):
        settings.setCompactTooltipScale(scale)
    row.addWidget(settings)

    toolbar.setFixedHeight(metric(44, 33))
    toolbar.setMinimumWidth(
        margin * 2
        + export.minimumWidth()
        + icon_frame * 2
        + row.spacing() * 2
    )
    toolbar.setSizePolicy(
        _QtWidgets.QSizePolicy.Policy.Expanding,
        _QtWidgets.QSizePolicy.Policy.Fixed,
    )
    toolbar._rizum_export_button = export
    toolbar._rizum_bridge_button = bridge
    toolbar._rizum_settings_button = settings
    return toolbar


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


def build_settings_preview(QtWidgets):
    """Build the PT Bridge settings panel from the canonical settings rhythm."""
    from PySide6 import QtCore, QtGui, QtWidgets as _QtWidgets

    layout_spec = PAINTER_SETTINGS_LAYOUT
    dark = dict(PAINTER_DIALOG_STYLE)
    theme = {
        **dark,
        "border": "#3a3b3e",
        "toggle_off": QtGui.QColor(dark["control"]),
        "toggle_knob_off": QtGui.QColor(dark["muted"]),
        "toggle_knob_on": QtGui.QColor(dark["muted"]),
    }

    class ToggleSwitch(_QtWidgets.QFrame):
        BASE_WIDTH = 36
        BASE_HEIGHT = 20
        MIN_HEIGHT = 15

        def __init__(self, on=False):
            super().__init__()
            self._on = bool(on)
            self._compact_height = self.BASE_HEIGHT
            self._knob_margin = 3.0
            self._knob_size = 14.0
            self._offset = 0.0
            self._animation = None
            self._callback = None
            self.setObjectName("RizumSettingsToggle")
            self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)
            self.setAutoFillBackground(False)
            self.setStyleSheet("background: transparent; border: 0;")
            self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
            self.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
            self.setCompactHeight(self.BASE_HEIGHT)

        def _knob_travel(self):
            return max(
                0.0,
                float(self.width()) - self._knob_size - self._knob_margin * 2,
            )

        def setCompactHeight(self, height):
            if self._animation is not None:
                self._animation.stop()
                self._animation = None
            self._compact_height = max(self.MIN_HEIGHT, int(round(height)))
            scale = self._compact_height / float(self.BASE_HEIGHT)
            width = max(27, int(round(self.BASE_WIDTH * scale)))
            self._knob_margin = 3.0 * scale
            self._knob_size = 14.0 * scale
            self.setFixedSize(width, self._compact_height)
            self._offset = self._knob_travel() if self._on else 0.0
            self.updateGeometry()
            self.update()

        def setChangedCallback(self, callback):
            self._callback = callback

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
            animation.setDuration(180)
            animation.setStartValue(self._offset)
            animation.setEndValue(self._knob_travel() if enabled else 0.0)
            animation.setEasingCurve(QtCore.QEasingCurve.Type.OutCubic)
            self._animation = animation
            animation.start()
            if self._callback is not None:
                self._callback(enabled)

        def toggle(self):
            self.setOn(not self._on)

        def mousePressEvent(self, event):
            if event.button() == QtCore.Qt.MouseButton.LeftButton:
                self.toggle()
                event.accept()
                return
            super().mousePressEvent(event)

        def paintEvent(self, event):
            del event
            painter = QtGui.QPainter(self)
            painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)
            rect = QtCore.QRectF(0.5, 0.5, self.width() - 1.0, self.height() - 1.0)
            painter.setPen(QtCore.Qt.PenStyle.NoPen)
            painter.setBrush(
                QtGui.QColor(theme["accent"])
                if self._on
                else theme["toggle_off"]
            )
            painter.drawRoundedRect(rect, rect.height() / 2.0, rect.height() / 2.0)
            painter.setBrush(
                theme["toggle_knob_on"]
                if self._on
                else theme["toggle_knob_off"]
            )
            painter.drawEllipse(
                QtCore.QRectF(
                    self._knob_margin + self._offset,
                    self._knob_margin,
                    self._knob_size,
                    self._knob_size,
                )
            )
            painter.end()

    class RevealRow(_QtWidgets.QFrame):
        def __init__(self, content, expanded_height):
            super().__init__()
            self.setObjectName("RizumSettingsRevealRow")
            self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)
            self.setAutoFillBackground(False)
            self.setStyleSheet("background: transparent; border: 0;")
            self._expanded_height = int(expanded_height)
            self._gap = layout_spec.body_spacing.design
            self._progress = 1.0
            self._gap_layout = None
            self._geometry_callback = None
            self._animation = None
            self._expanded = True
            reveal_layout = _QtWidgets.QVBoxLayout(self)
            reveal_layout.setContentsMargins(0, 0, 0, 0)
            reveal_layout.setSpacing(0)
            reveal_layout.addWidget(content)
            self.setFixedHeight(self._expanded_height)

        def setExpandedHeight(self, height):
            self._expanded_height = max(0, int(round(height)))
            self._syncRevealGeometry()

        def expandedHeight(self):
            return self._expanded_height

        def setGapLayout(self, target_layout):
            self._gap_layout = target_layout
            self._syncRevealGeometry()

        def setGap(self, gap):
            self._gap = max(0, int(round(gap)))
            self._syncRevealGeometry()

        def setGeometryCallback(self, callback):
            self._geometry_callback = callback

        def _syncRevealGeometry(self):
            progress = max(0.0, min(1.0, self._progress))
            self.setFixedHeight(round(self._expanded_height * progress))
            if self._gap_layout is not None:
                self._gap_layout.setSpacing(round(self._gap * progress))
            if self._geometry_callback is not None:
                self._geometry_callback(progress)

        def getRevealProgress(self):
            return self._progress

        def setRevealProgress(self, value):
            self._progress = float(value)
            self._syncRevealGeometry()

        revealProgress = QtCore.Property(float, getRevealProgress, setRevealProgress)

        def setExpanded(self, expanded, animate=True):
            expanded = bool(expanded)
            self._expanded = expanded
            target = 1.0 if expanded else 0.0
            self.setAttribute(
                QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents,
                not expanded,
            )
            if self._animation is not None:
                self._animation.stop()
            if not animate:
                self.setRevealProgress(target)
                return
            animation = QtCore.QPropertyAnimation(self, b"revealProgress", self)
            animation.setDuration(max(100, round(180 * abs(target - self._progress))))
            animation.setStartValue(self._progress)
            animation.setEndValue(target)
            animation.setEasingCurve(QtCore.QEasingCurve.Type.OutCubic)
            self._animation = animation
            animation.start()

    def make_label(text, object_name, parent=None):
        label = _QtWidgets.QLabel(text, parent)
        label.setObjectName(object_name)
        return label

    sections = []
    rows = []
    text_blocks = []

    def make_section(text, first=False):
        label = make_label(text.upper(), "RizumSettingsSection")
        metric = (
            layout_spec.first_section_height
            if first
            else layout_spec.section_height
        )
        label._rizum_layout_metric = metric
        label.setFixedHeight(metric.design)
        sections.append(label)
        return label

    def make_row(tall=False):
        row = _QtWidgets.QFrame()
        row.setObjectName("RizumSettingsRow")
        metric = layout_spec.detail_row_height if tall else layout_spec.row_height
        row._rizum_layout_metric = metric
        row.setFixedHeight(metric.design)
        row_layout = _QtWidgets.QHBoxLayout(row)
        row_layout.setContentsMargins(
            0,
            layout_spec.row_padding_y.design,
            0,
            layout_spec.row_padding_y.design,
        )
        row_layout.setSpacing(layout_spec.row_spacing)
        rows.append(row)
        return row, row_layout

    def make_text_block(name, meta=""):
        widget = _QtWidgets.QWidget()
        widget.setObjectName("RizumSettingsTexts")
        block_layout = _QtWidgets.QVBoxLayout(widget)
        block_layout.setContentsMargins(0, 0, 0, 0)
        block_layout.setSpacing(layout_spec.text_spacing.design)
        name_label = make_label(name, "RizumSettingsItemName")
        block_layout.addWidget(name_label)
        meta_label = None
        if meta:
            meta_label = make_label(meta, "RizumSettingsItemMeta")
            block_layout.addWidget(meta_label)
        widget._rizum_name_label = name_label
        widget._rizum_meta_label = meta_label
        text_blocks.append(widget)
        return widget

    window = PainterSettingsDialog()
    window.setObjectName("RizumSettingsWindow")
    window.setWindowFlags(QtCore.Qt.WindowType.Widget)
    window.setSettingsFrameWidth(0)
    window.setSettingsFrameBottomWidth(0)
    window.setSettingsBottomEdgeExtensionEnabled(False)
    window.setSizePolicy(
        _QtWidgets.QSizePolicy.Policy.Fixed,
        _QtWidgets.QSizePolicy.Policy.Fixed,
    )
    surface_layout = window.settingsSurfaceLayout()

    content = make_painter_window_content(
        dark["surface"],
        rounded=False,
        bottom_radius=PAINTER_WINDOW_CONTENT_RADIUS,
    )
    content_layout = content.contentLayout()
    surface_layout.addWidget(content, 1)

    body = _QtWidgets.QWidget()
    body.setObjectName("RizumSettingsBody")
    body_layout = _QtWidgets.QVBoxLayout(body)
    body_layout.setContentsMargins(
        layout_spec.body_margin_x.design,
        layout_spec.body_margin_top.design,
        layout_spec.body_margin_x.design,
        layout_spec.body_margin_bottom.design,
    )
    body_layout.setSpacing(layout_spec.body_spacing.design)

    body_layout.addWidget(
        make_section(preview_text("export", "Export"), first=True)
    )
    padding_stack = _QtWidgets.QWidget()
    padding_stack.setObjectName("RizumSettingsPaddingStack")
    padding_stack_layout = _QtWidgets.QVBoxLayout(padding_stack)
    padding_stack_layout.setContentsMargins(0, 0, 0, 0)
    padding_stack_layout.setSpacing(0)

    padding_row, padding_layout = make_row(tall=True)
    padding_texts = make_text_block(
        preview_text("padding", "Padding"), preview_text("infinite", "Infinite")
    )
    padding_meta = padding_texts._rizum_meta_label
    padding_layout.addWidget(padding_texts)
    padding_layout.addStretch(1)
    padding_toggle = ToggleSwitch(True)
    padding_layout.addWidget(padding_toggle)
    padding_stack_layout.addWidget(padding_row)

    dilation_row, dilation_layout = make_row(tall=True)
    dilation_texts = make_text_block("Dilation", "px")
    dilation_layout.addWidget(dilation_texts)
    dilation_layout.addStretch(1)
    stepper = make_compact_stepper(8, minimum=0, maximum=999, step=1)
    dilation_layout.addWidget(stepper)
    dilation_reveal = RevealRow(
        dilation_row,
        layout_spec.detail_row_height.design,
    )
    padding_stack_layout.addWidget(dilation_reveal)
    dilation_reveal.setGapLayout(padding_stack_layout)
    body_layout.addWidget(padding_stack)

    bit_depth = make_combo_input(
        [
            (preview_text("texture_set", "Texture Set"), None),
            ("8-bit", 8),
            ("16-bit", 16),
        ]
    )
    bit_depth.setProperty("rizumSettingsRole", "bit-depth")
    bit_depth.setFitToContents(False)
    bit_depth.setFixedWidth(126)
    bit_depth_row, bit_depth_layout = make_row()
    bit_depth_layout.addWidget(
        make_label(
            preview_text("bit_depth", "Bit depth"),
            "RizumSettingsItemName",
        )
    )
    bit_depth_layout.addStretch(1)
    bit_depth_layout.addWidget(bit_depth)
    body_layout.addWidget(bit_depth_row)

    auto_row, auto_layout = make_row(tall=True)
    auto_texts = make_text_block(
        preview_text("auto_open", "Auto-open Photoshop"),
        preview_text("auto_open_meta", "Launch after a successful export"),
    )
    auto_layout.addWidget(auto_texts)
    auto_layout.addStretch(1)
    auto_toggle = ToggleSwitch(False)
    auto_layout.addWidget(auto_toggle)

    body_layout.addWidget(make_section(preview_text("photoshop", "Photoshop")))
    body_layout.addWidget(auto_row)
    path_row, path_layout = make_row()
    path_select = _QtWidgets.QFrame()
    path_select.setObjectName("RizumSettingsMockSelect")
    path_select_layout = _QtWidgets.QHBoxLayout(path_select)
    path_select_layout.setContentsMargins(8, 0, 8, 0)
    path_select_layout.setSpacing(6)
    path_input = _QtWidgets.QLineEdit(r"C:\Program Files\Adobe\Photoshop.exe")
    path_input.setObjectName("RizumSettingsPathInput")
    path_input.setPlaceholderText("Photoshop.exe")
    path_input.setFrame(False)
    path_input.setClearButtonEnabled(False)
    path_input.setCursorPosition(0)
    path_input.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter)
    path_input.setSizePolicy(
        _QtWidgets.QSizePolicy.Policy.Expanding,
        _QtWidgets.QSizePolicy.Policy.Fixed,
    )
    path_select_layout.addWidget(path_input, 1, QtCore.Qt.AlignmentFlag.AlignVCenter)
    path_layout.addWidget(path_select, 1)
    browse_btn = make_icon_button(
        "folder.svg", "Browse executable", size=14, compact=False
    )
    path_layout.addWidget(browse_btn)
    body_layout.addWidget(path_row)

    body_layout.addWidget(make_section(preview_text("about", "About")))
    version_row, version_layout = make_row()
    version_layout.addWidget(
        make_label(preview_text("version", "Version"), "RizumSettingsItemName")
    )
    version_layout.addStretch(1)
    version_layout.addWidget(make_label("2.0.0", "RizumSettingsItemMeta"))
    body_layout.addWidget(version_row)
    content_layout.addWidget(body)

    footer_separator = make_inset_separator(
        layout_spec.footer_margin_x.design,
        thickness=1,
    )
    footer_separator.setObjectName("RizumSettingsFooterDivider")
    content_layout.addWidget(footer_separator)

    footer = _QtWidgets.QWidget()
    footer.setObjectName("RizumSettingsFooter")
    footer_outer = _QtWidgets.QVBoxLayout(footer)
    footer_outer.setContentsMargins(0, 0, 0, 0)
    footer_outer.setSpacing(0)
    footer_row = _QtWidgets.QWidget()
    footer_row.setObjectName("RizumSettingsFooterRow")
    footer_layout = _QtWidgets.QHBoxLayout(footer_row)
    footer_layout.setContentsMargins(
        layout_spec.footer_margin_x.design,
        0,
        layout_spec.footer_margin_x.design,
        0,
    )
    footer_layout.setSpacing(layout_spec.footer_button_spacing)
    footer_hint = make_label(
        preview_text("auto_save", "Changes save automatically"),
        "RizumSettingsFooterHint",
    )
    footer_layout.addWidget(footer_hint)
    footer_layout.addStretch(1)
    done_button = SecondaryActionButton(
        preview_text("done", "Done"),
        theme["accent"],
        theme["accent_hover"],
        theme["accent_pressed"],
        theme["accent_text"],
        default_theme.radius_small,
    )
    done_button.setProperty("rizumSettingsRole", "done")
    footer_layout.addWidget(done_button)
    footer_outer.addWidget(footer_row)
    content_layout.addWidget(footer)

    toggles = [padding_toggle, auto_toggle]
    base_height = None
    design_height = None

    def metric(value, minimum=None):
        return window.settingsMetric(value, minimum)

    def text_font(pixel_size, weight):
        font = QtGui.QFont(window.font())
        font.setPixelSize(metric(pixel_size))
        font.setWeight(weight)
        return font

    def current_extra_height():
        progress = max(0.0, min(1.0, dilation_reveal.getRevealProgress()))
        return round(dilation_reveal.expandedHeight() * progress) + round(
            body_layout.spacing() * progress
        )

    def sync_window_height(_progress=0.0):
        if base_height is None:
            return
        window.setFixedHeight(base_height + current_extra_height())
        window.updateGeometry()

    dilation_reveal.setGeometryCallback(sync_window_height)

    def apply_visual_style():
        window.setProperty("theme", "dark")
        content.setPainterContentColor(theme["surface"])
        window._update_surface_stylesheet()
        surface = window.settingsSurface()
        surface.setStyleSheet(
            surface.styleSheet()
            + f"""
QFrame#RizumPainterSettingsSurface {{
    background: {theme["surface"]};
}}
QWidget#RizumSettingsBody,
QWidget#RizumSettingsFooter,
QWidget#RizumSettingsFooterRow,
QWidget#RizumSettingsPaddingStack,
QWidget#RizumSettingsTexts,
QWidget#RizumSettingsFooterDivider,
QFrame#RizumSettingsRevealRow {{
    background: transparent;
    border: 0;
}}
QLabel#RizumSettingsSection {{ color: {theme["faint"]}; }}
QLabel#RizumSettingsItemName {{ color: {theme["text"]}; }}
QLabel#RizumSettingsItemMeta,
QLabel#RizumSettingsFooterHint {{ color: {theme["muted"]}; }}
QFrame#RizumSettingsRow {{
    background: transparent;
    border: 0;
}}
QWidget#RizumSettingsFooterDivider QFrame#RizumInsetSeparator {{
    background: {theme["border"]};
}}
QFrame#RizumSettingsMockSelect {{
    background: transparent;
    border: 0;
}}
QLineEdit#RizumSettingsPathInput {{
    color: {theme["muted"]};
    background: transparent;
    border: 0;
    padding: 0;
    selection-background-color: {theme["control_hover"]};
    selection-color: {theme["text"]};
}}
QLineEdit#RizumSettingsPathInput:hover,
QLineEdit#RizumSettingsPathInput:focus {{
    color: {theme["text"]};
    background: transparent;
    border: 0;
}}
QPushButton[variant="icon"] {{
    background: transparent;
    border: 0;
    border-radius: {default_theme.radius_small}px;
}}
QPushButton[variant="icon"]:hover {{
    background: {theme["control_hover"]};
}}
QPushButton[variant="icon"]:pressed {{
    background: {theme["control_pressed"]};
}}
"""
        )
        stepper.setTheme(
            {
                "window_bg": theme["surface"],
                "text": theme["text"],
                "muted": theme["muted"],
                "control_hover": theme["control_hover"],
            }
        )
        done_button._background = QtGui.QColor(theme["accent"])
        done_button._hover_background = QtGui.QColor(theme["accent_hover"])
        done_button._pressed_background = QtGui.QColor(theme["accent_pressed"])
        done_button._text_color = QtGui.QColor(theme["accent_text"])
        done_button.update()
        browse_btn.setProperty("iconColor", theme["muted"])
        browse_btn.setProperty("iconHoverColor", theme["text"])
        browse_btn.update()

    def required_width():
        body_margin = layout_spec.body_margin_x.resolve(window)
        footer_margin = layout_spec.footer_margin_x.resolve(window)
        base = metric(338, 254)
        footer_need = (
            footer_hint.sizeHint().width()
            + done_button.width()
            + layout_spec.footer_button_spacing
            + 2 * footer_margin
        )
        bit_depth_need = (
            bit_depth_layout.itemAt(0).widget().sizeHint().width()
            + layout_spec.row_spacing
            + bit_depth.width()
            + 2 * body_margin
        )
        auto_need = (
            auto_texts.sizeHint().width()
            + layout_spec.row_spacing
            + auto_toggle.width()
            + 2 * body_margin
        )
        return max(base, footer_need, bit_depth_need, auto_need)

    def apply_scale():
        body_margin = layout_spec.body_margin_x.resolve(window)
        body_layout.setContentsMargins(
            body_margin,
            layout_spec.body_margin_top.resolve(window),
            body_margin,
            layout_spec.body_margin_bottom.resolve(window),
        )
        body_layout.setSpacing(layout_spec.body_spacing.resolve(window))
        row_padding = layout_spec.row_padding_y.resolve(window)
        for section in sections:
            section.setFixedHeight(section._rizum_layout_metric.resolve(window))
        for row in rows:
            row.setFixedHeight(row._rizum_layout_metric.resolve(window))
            row.layout().setContentsMargins(0, row_padding, 0, row_padding)
            row.layout().setSpacing(layout_spec.row_spacing)

        name_metrics = QtGui.QFontMetrics(
            text_font(13, QtGui.QFont.Weight.Medium)
        )
        meta_metrics = QtGui.QFontMetrics(
            text_font(11, QtGui.QFont.Weight.Medium)
        )
        text_spacing = layout_spec.text_spacing.resolve(window)
        for block in text_blocks:
            block.layout().setSpacing(text_spacing)
            block._rizum_name_label.setFixedHeight(name_metrics.height())
            if block._rizum_meta_label is not None:
                block._rizum_meta_label.setFixedHeight(meta_metrics.height())
                block.setFixedHeight(
                    name_metrics.height() + text_spacing + meta_metrics.height()
                )

        stepper.setCompactHeight(layout_spec.stepper_height.resolve(window))
        control_height = layout_spec.control_height.resolve(window)
        bit_depth.setCompactHeight(control_height)
        bit_depth.setFitToContents(True)
        bit_depth.fitToContents()
        combo_margins = bit_depth.layout().contentsMargins()
        # The combo label uses rich text, whose size hint can exceed the
        # plain-font measurement used by fitToContents in long translations.
        localized_bit_depth_width = max(
            bit_depth.width(),
            bit_depth._label.sizeHint().width()
            + combo_margins.left()
            + combo_margins.right()
            + bit_depth.layout().spacing()
            + bit_depth._arrow_size
            + metric(6, 5),
        )
        bit_depth.setFitToContents(False)
        bit_depth.setFixedWidth(
            max(metric(126, 95), localized_bit_depth_width)
        )
        toggle_height = metric(ToggleSwitch.BASE_HEIGHT, ToggleSwitch.MIN_HEIGHT)
        for toggle in toggles:
            toggle.setCompactHeight(toggle_height)
        detail_height = layout_spec.detail_row_height.resolve(window)
        dilation_reveal.setExpandedHeight(detail_height)
        dilation_reveal.setGap(body_layout.spacing())

        path_select.setFixedHeight(control_height)
        path_input.setFixedHeight(max(15, control_height - metric(8, 6)))
        icon_frame = metric(26, 20)
        browse_btn.setFixedSize(icon_frame, icon_frame)
        if hasattr(browse_btn, "setPaintedIconSize"):
            browse_btn.setPaintedIconSize(metric(14, 11))
        if hasattr(browse_btn, "setCompactTooltipScale"):
            browse_btn.setCompactTooltipScale(window.settingsUiScale())

        footer_margin = layout_spec.footer_margin_x.resolve(window)
        footer_top = layout_spec.footer_top.resolve(window)
        footer_gap = layout_spec.footer_gap.resolve(window)
        footer_bottom = layout_spec.footer_bottom.resolve(window)
        footer_row_height = layout_spec.footer_row_height.resolve(window)
        footer_outer.setContentsMargins(
            0,
            footer_top + footer_gap,
            0,
            footer_bottom,
        )
        footer_row.setFixedHeight(footer_row_height)
        footer.setFixedHeight(
            footer_top + footer_gap + footer_row_height + footer_bottom
        )
        footer_layout.setContentsMargins(footer_margin, 0, footer_margin, 0)
        footer_separator.layout().setContentsMargins(
            footer_margin, 0, footer_margin, 0
        )
        button_height = layout_spec.footer_button_height.resolve(window)
        done_button.setCompactHeight(button_height)
        done_button.setFixedWidth(
            max(metric(72, 54), done_button.sizeHint().width() + metric(8, 6))
        )
        window.setFixedWidth(required_width())
        apply_visual_style()

    def remeasure_base_height():
        nonlocal base_height, design_height
        window.setMinimumHeight(0)
        window.setMaximumHeight(16777215)
        measured = max(1, window.sizeHint().height() - current_extra_height())
        scale = window.settingsUiScale()
        if design_height is None:
            normalizer = scale if scale >= 1.0 else 1.0
            design_height = int(round(measured / normalizer))
        base_height = max(measured, int(round(design_height * scale)))
        sync_window_height()

    def on_scale_changed(_scale):
        apply_scale()
        remeasure_base_height()

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
            padding_meta.setText(
                preview_text("infinite", "Infinite") if enabled else "Custom"
            )
        dilation_reveal.setExpanded(not enabled)

    padding_toggle.setChangedCallback(sync_padding_dilation)
    window.settingsUiScaleChanged.connect(on_scale_changed)
    dilation_reveal.setExpanded(not padding_toggle.isOn(), animate=False)
    apply_scale()
    remeasure_base_height()

    window._rizum_body_layout = body_layout
    window._rizum_rows = rows
    window._rizum_footer = footer
    window._rizum_footer_row = footer_row
    window._rizum_done_button = done_button
    window._rizum_padding_toggle = padding_toggle
    window._rizum_dilation_reveal = dilation_reveal
    window._rizum_bit_depth = bit_depth
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
                mapped=True,
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
            self.empty_hint = _QtWidgets.QLabel("Drop Photoshop layers here to map")
            self.empty_hint.setObjectName("RizumDragEmptyHint")
            self.empty_hint.setContentsMargins(34, 4, 0, 0)
            self.tree_layout.addWidget(self.empty_hint)
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
                mapped=True,
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
QLabel#RizumDragEmptyHint {
    color: #666666;
    font-size: 11px;
    font-weight: 400;
    background: transparent;
    border: 0;
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


def _build_preview_candidate(window, QtWidgets, watch_enabled, rebuild_callback=None):
    from PySide6 import QtCore

    old_tabs = window.findChild(QtWidgets.QTabWidget, "RizumPreviewTabs")
    if old_tabs is not None:
        window.setProperty("rizumPreviewTabIndex", old_tabs.currentIndex())

    # Build away from the live window so a transient import or constructor
    # error cannot destroy the last good preview during source reload.
    preview_root = QtWidgets.QWidget(window)
    preview_root.setObjectName("RizumPreviewStagingRoot")
    layout = QtWidgets.QVBoxLayout(preview_root)
    layout.setContentsMargins(16, 16, 16, 16)
    layout.setSpacing(12)

    title_row = QtWidgets.QHBoxLayout()
    title_row.addWidget(
        SectionHeader(
            "Rizum UI Prettier",
            "Shared PySide6 components for Substance 3D Painter plugins.",
        ),
        1,
    )

    scale_label = QtWidgets.QLabel("UI Scale")
    scale_label.setObjectName("RizumPreviewToolLabel")
    title_row.addWidget(scale_label)
    app = QtWidgets.QApplication.instance()
    scale = float(window.property("rizumPreviewUiScale") or 1.0)
    scale_input = make_spin_input(scale, minimum=0.75, maximum=2.0, step=0.05)
    scale_input.setObjectName("RizumPreviewScaleInput")
    scale_input.setCompactHeight(26)
    title_row.addWidget(scale_input)

    language_label = QtWidgets.QLabel(preview_text("language", "Language"))
    language_label.setObjectName("RizumPreviewToolLabel")
    title_row.addWidget(language_label)
    language_input = make_combo_input(PREVIEW_LANGUAGES)
    language_input.setObjectName("RizumPreviewLanguageInput")
    language_input.setCompactHeight(26)
    language_input.setCurrentIndex(
        max(0, language_input.findData(preview_language()))
    )
    title_row.addWidget(language_input)

    reload_button = ActionButton.create(preview_text("reload", "Reload"), "ghost")
    title_row.addWidget(reload_button)
    layout.addLayout(title_row)

    if rebuild_callback is not None:
        reload_button.clicked.connect(rebuild_callback)

        def request_scale(value):
            value = float(value)
            window.setProperty("rizumPreviewUiScale", value)
            if app is not None:
                app.setProperty("rizumUiFontScale", value)
            if window.property("rizumPreviewPersistSettings"):
                settings = QtCore.QSettings(
                    _PREVIEW_SETTINGS_ORG, _PREVIEW_SETTINGS_APP
                )
                settings.setValue("uiScale", value)
            QtCore.QTimer.singleShot(0, rebuild_callback)

        def request_language(_index):
            language = language_input.currentData() or "en"
            if app is not None:
                app.setProperty("rizumPreviewLanguage", language)
            if window.property("rizumPreviewPersistSettings"):
                settings = QtCore.QSettings(
                    _PREVIEW_SETTINGS_ORG, _PREVIEW_SETTINGS_APP
                )
                settings.setValue("language", language)
            QtCore.QTimer.singleShot(0, rebuild_callback)

        scale_input.valueChanged.connect(request_scale)
        language_input.currentIndexChanged.connect(request_language)

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
    bridge_preview = build_bridge_preview(QtWidgets)
    overview_left_layout.addWidget(
        bridge_preview,
        0,
        QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignLeft,
    )
    dock_compare = QtWidgets.QWidget()
    dock_compare.setObjectName("RizumDockCompare")
    dock_compare.setFixedWidth(bridge_preview.width())
    dock_compare_layout = QtWidgets.QVBoxLayout(dock_compare)
    dock_compare_layout.setContentsMargins(0, 0, 0, 0)
    dock_compare_layout.setSpacing(6)

    dock_label = QtWidgets.QLabel("PT BRIDGE DOCK")
    dock_label.setObjectName("RizumPreviewToolLabel")
    dock_compare_layout.addWidget(dock_label)
    dock_toolbar = build_dock_toolbar_preview(QtWidgets)
    dock_toolbar.setStyleSheet(
        dock_toolbar.styleSheet()
        + "QWidget#RizumDockToolbar { border: 1px solid #3a3a3a; border-radius: 6px; }"
    )
    dock_compare_layout.addWidget(dock_toolbar)
    overview_left_layout.addWidget(
        dock_compare,
        0,
        QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignLeft,
    )
    overview_left_layout.addStretch(1)
    grid.addWidget(overview_left, 0, 0, 2, 1, QtCore.Qt.AlignmentFlag.AlignTop)
    grid.addWidget(build_font_preview_original(QtWidgets), 0, 1)
    grid.addWidget(build_lab(QtWidgets), 1, 1)
    grid.setColumnStretch(0, 0)
    grid.setColumnStretch(1, 1)
    overview_layout.addLayout(grid, 1)
    tabs.addTab(overview, preview_text("overview", "Overview"))

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
    tabs.addTab(drag_page, preview_text("drag_drop", "Drag Drop"))

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
    tabs.addTab(settings_page, preview_text("settings", "Settings"))

    import view_roll_preview

    view_roll_page = QtWidgets.QWidget()
    view_roll_layout = QtWidgets.QVBoxLayout(view_roll_page)
    view_roll_layout.setContentsMargins(0, 12, 0, 0)
    view_roll_layout.setSpacing(0)
    view_roll_layout.addWidget(
        view_roll_preview.build_view_roll_preview(QtWidgets),
        1,
    )
    tabs.addTab(view_roll_page, preview_text("view_roll", "View Roll"))

    font_page = QtWidgets.QWidget()
    font_page_layout = QtWidgets.QVBoxLayout(font_page)
    font_page_layout.setContentsMargins(0, 12, 0, 0)
    font_page_layout.setSpacing(0)
    font_page_layout.addWidget(
        build_font_comparison(QtWidgets),
        0,
        QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignHCenter,
    )
    font_page_layout.addStretch(1)
    tabs.addTab(font_page, "UI Font")

    tab_index = int(window.property("rizumPreviewTabIndex") or 0)
    tabs.setCurrentIndex(max(0, min(tab_index, tabs.count() - 1)))
    tabs.currentChanged.connect(
        lambda index: window.setProperty("rizumPreviewTabIndex", index)
    )

    layout.addWidget(tabs, 1)

    window_layout = window.layout()
    if window_layout is None:
        window_layout = QtWidgets.QVBoxLayout(window)
    else:
        clear_layout(window_layout)
    window_layout.setContentsMargins(0, 0, 0, 0)
    window_layout.setSpacing(0)
    preview_root.setObjectName("RizumPreviewRoot")
    window_layout.addWidget(preview_root)
    if window.isVisible():
        preview_root.show()

    return tabs


def build_preview(window, QtWidgets, watch_enabled, rebuild_callback=None):
    from PySide6 import QtCore

    app = QtWidgets.QApplication.instance()
    existing_top_levels = set(app.topLevelWidgets()) if app is not None else set()
    try:
        return _build_preview_candidate(
            window,
            QtWidgets,
            watch_enabled,
            rebuild_callback,
        )
    except BaseException:
        if app is not None:
            for widget in app.topLevelWidgets():
                if widget not in existing_top_levels and widget is not window:
                    widget.deleteLater()
        pending_roots = window.findChildren(
            QtWidgets.QWidget,
            "RizumPreviewStagingRoot",
            QtCore.Qt.FindChildOption.FindDirectChildrenOnly,
        )
        for pending_root in pending_roots:
            pending_root.deleteLater()
        raise


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
        try:
            reload_ui_kit()
            apply_painter_like_base(app)
            app.setStyleSheet(
                build_painter_host_preview_stylesheet()
                + build_stylesheet(mode="full" if full_mode else "overlay")
                + PREVIEW_CANVAS_STYLESHEET
            )
            build_preview(window, QtWidgets, watch_enabled, refresh_preview)
        except Exception:
            import traceback

            traceback.print_exc()
        finally:
            # Consume this source snapshot even when a reload fails. Retrying
            # the same broken snapshot every 500 ms starves painting and leaks
            # the abandoned widget trees until the preview appears blank.
            mtimes = next_mtimes

    settings = QtCore.QSettings(_PREVIEW_SETTINGS_ORG, _PREVIEW_SETTINGS_APP)
    try:
        saved_scale = float(settings.value("uiScale", 1.0))
    except (TypeError, ValueError):
        saved_scale = 1.0
    saved_scale = max(0.75, min(2.0, saved_scale))
    saved_language = str(settings.value("language", "en"))
    valid_languages = {data for _label, data in PREVIEW_LANGUAGES}
    if saved_language not in valid_languages:
        saved_language = "en"
    app.setProperty("rizumPreviewLanguage", saved_language)
    app.setProperty("rizumUiFontScale", saved_scale)
    window.setProperty("rizumPreviewUiScale", saved_scale)
    window.setProperty("rizumPreviewPersistSettings", True)
    build_preview(window, QtWidgets, watch_enabled, refresh_preview)

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
