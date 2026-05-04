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
    )
except Exception as exc:
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None

_PANEL = None
_DOCK = None


class UiPrettierPreviewPanel:
    def __init__(self):
        from PySide6 import QtWidgets

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
                "Live preview inside Painter using the real host UI.",
            )
        )

        layout.addWidget(self._build_component_card(), 1)
        layout.addStretch(1)

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
