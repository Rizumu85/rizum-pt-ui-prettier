"""Substance 3D Painter preview plugin for the Rizum UI kit."""

from __future__ import annotations

from pathlib import Path
import sys

PLUGIN_ROOT = Path(__file__).resolve().parent
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

try:
    from rizum_ui import (
        ActionButton,
        Card,
        FieldLabel,
        SectionHeader,
        StatusPill,
        apply_theme,
        save_app_palette,
    )
except Exception as exc:
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None

_PANEL = None
_DOCK = None


class UiPrettierPreviewPanel:
    def __init__(self):
        from PySide6 import QtGui, QtWidgets

        self.QtGui = QtGui
        self.QtWidgets = QtWidgets
        self.widget = QtWidgets.QWidget()
        self.widget.setObjectName("RizumSurface")
        self.widget.setWindowTitle("UI Prettier")
        apply_theme(self.widget, mode="overlay")

        layout = QtWidgets.QVBoxLayout(self.widget)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)
        layout.addWidget(
            SectionHeader(
                "UI Prettier",
                "Live preview inside Painter using the real host palette.",
            )
        )

        layout.addWidget(self._build_palette_card())
        layout.addWidget(self._build_component_card(), 1)
        layout.addStretch(1)

    def _build_palette_card(self):
        from PySide6 import QtWidgets

        card = Card.create()
        layout = card.layout()
        layout.addWidget(SectionHeader("Host Palette", "Export this palette for external preview matching."))

        row = QtWidgets.QHBoxLayout()
        app = QtWidgets.QApplication.instance()
        palette = app.palette()
        for role_name in ["Window", "Base", "Button", "Text", "Highlight"]:
            role = getattr(self.QtGui.QPalette.ColorRole, role_name)
            color = palette.color(role)
            swatch = QtWidgets.QLabel(role_name)
            swatch.setMinimumHeight(28)
            swatch.setStyleSheet(
                f"background: {color.name()}; border: 1px solid #555; border-radius: 5px; padding: 4px 6px;"
            )
            row.addWidget(swatch)
        layout.addLayout(row)

        export_button = ActionButton.create("Export Palette", "primary")
        export_button.clicked.connect(self.export_palette)
        self.status = StatusPill("Not exported", "neutral")
        action_row = QtWidgets.QHBoxLayout()
        action_row.addWidget(self.status)
        action_row.addStretch(1)
        action_row.addWidget(export_button)
        layout.addLayout(action_row)
        return card

    def _build_component_card(self):
        from PySide6 import QtWidgets

        card = Card.create()
        layout = card.layout()
        layout.addWidget(SectionHeader("Components", "These controls render inside the real Painter dock."))

        form = QtWidgets.QFormLayout()
        combo = QtWidgets.QComboBox()
        combo.addItems(["Current Stack", "All Stacks", "Selected Channels"])
        form.addRow(FieldLabel.create("Scope"), combo)

        value = QtWidgets.QDoubleSpinBox()
        value.setRange(0.75, 2.0)
        value.setValue(1.05)
        value.setSingleStep(0.05)
        form.addRow(FieldLabel.create("Scale"), value)
        layout.addLayout(form)

        tree = QtWidgets.QTreeWidget()
        tree.setHeaderHidden(True)
        item = QtWidgets.QTreeWidgetItem(["Texture Set / Stack / 3 channels"])
        tree.addTopLevelItem(item)
        for name in ["Base Color", "Roughness", "Normal"]:
            item.addChild(QtWidgets.QTreeWidgetItem([name]))
        item.setExpanded(True)
        layout.addWidget(tree)

        row = QtWidgets.QHBoxLayout()
        row.addWidget(StatusPill("Ready", "good"))
        row.addWidget(StatusPill("Painter", "info"))
        row.addStretch(1)
        row.addWidget(ActionButton.create("Secondary"))
        row.addWidget(ActionButton.create("Primary", "primary"))
        layout.addLayout(row)
        return card

    def export_palette(self):
        app = self.QtWidgets.QApplication.instance()
        path = Path(__file__).resolve().parent / "preview-host-palette.json"
        save_app_palette(app, path)
        self.status.setText("Exported")
        self.status.setToolTip(str(path))

    def close(self):
        pass


def start_plugin():
    import substance_painter as sp

    if _IMPORT_ERROR is not None:
        sp.logging.error(f"Rizum UI Prettier import failed: {_IMPORT_ERROR!r}")
        raise _IMPORT_ERROR

    global _DOCK, _PANEL
    _PANEL = UiPrettierPreviewPanel()
    _DOCK = sp.ui.add_dock_widget(_PANEL.widget)
    _DOCK.setWindowTitle("UI Prettier")
    _DOCK.show()
    sp.logging.info("Rizum UI Prettier preview plugin loaded")


def close_plugin():
    import substance_painter as sp

    global _DOCK, _PANEL
    if _PANEL is not None:
        _PANEL.close()
        _PANEL = None
    if _DOCK is not None:
        sp.ui.delete_ui_element(_DOCK)
        _DOCK = None
    sp.logging.info("Rizum UI Prettier preview plugin unloaded")
