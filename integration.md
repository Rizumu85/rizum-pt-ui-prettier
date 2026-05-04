# Painter Plugin Integration

## Safe Boundary

Do not patch Substance 3D Painter installation files. Use the UI kit in one of two scopes:

1. Plugin scope: call `apply_theme(self.widget, mode="overlay")` on a plugin panel or dialog.
2. App scope: call `apply_theme(QApplication.instance(), mode="overlay")` from an explicit appearance/font helper plugin.

Plugin scope is the default. App scope is useful for experiments, but it can affect Painter-owned widgets and other plugins.

## `rizum-pt-to-ps-bridge`

Add this near the top of the UI module before constructing widgets:

```python
from pathlib import Path
import sys

ui_kit_root = Path(__file__).resolve().parents[3] / "rizum-pt-ui-prettier"
if str(ui_kit_root) not in sys.path:
    sys.path.insert(0, str(ui_kit_root))

from rizum_ui import ActionButton, SectionHeader, apply_theme
```

Then apply the theme once after creating the dock root widget:

```python
self.widget = QtWidgets.QWidget()
self.widget.setObjectName("RizumPtToPsSmokeTestPanel")
apply_theme(self.widget, mode="overlay")
```

Use components gradually. For example:

```python
self.dock_export_button = ActionButton.create("Export", "primary")
```

Keep plugin/window chrome owned by the plugin. For example, PT Bridge should keep its own panel title and close control; use shared components for the panel body, toolbar controls, export tree rows, and collapsible content.

### Icon Rendering Standard

Use `make_icon_button()` for interactive toolbar and action icons. This is the shared visual standard for Painter-style icon buttons: it renders SVGs with `QSvgRenderer` into a transparent pixmap at the widget device pixel ratio, then recolors through the glyph alpha mask with `CompositionMode_SourceIn`. This keeps the icon sharp, preserves transparent corners, and avoids source SVG colors making dark icons invisible on the dark host surface.

Do not use direct `QIcon.pixmap()` or one-off QLabel/SVG rendering for interactive toolbar icons. Set `button.setProperty("accent", True)` only for icons that should be white in their normal state; otherwise the standard muted-to-white hover behavior should be used.

Use `make_svg_label()` for passive one-off glyphs only. For tree/list rows, prefer `make_tree_icon_label()` so filled folders, 16px layer glyphs, and mask badges stay consistent across export and drag/drop surfaces. Pair custom row surfaces with `bind_hover_state(host, row, *watched_widgets)` instead of relying only on Qt `:hover`; it keeps the same `hovered` property stable while moving across child labels, checkboxes, or action buttons. Plugin/window chrome such as top title bars and close buttons stays plugin-owned.

All shared SVG source files must use the same intrinsic canvas:

- `width="24" height="24" viewBox="0 0 24 24"`
- `stroke-width="2"` for outline strokes
- `stroke-linecap="round"` and `stroke-linejoin="round"`
- `#9E9E9E` for default neutral icon strokes/fills

Exceptions should be intentional and component-specific, such as `checkmark.svg` using `#1B1B1B` inside a white confirm button. Do not change per-file SVG width/height to fix apparent icon weight; keep the canvas standard and adjust the path geometry inside the 24x24 viewBox. For mixed filled/outline icons, use the same neutral color for filled pieces and outlines unless a design state explicitly tints the rendered widget.

When localized strings or runtime UI font scale change, refresh shared compact controls after applying the new font:

```python
mode_combo.setItems([("All Sets", "all"), ("Current Set", "current")])
mode_combo.refreshMetrics()
action_bar.refreshLayout()
window.setFixedWidth(compact_action_bar_width([mode_combo], icon_toolbar))
tree_row.refreshLayout()
group.refreshLayout("M_body", "4 Channels")
export_button.refreshLayout(minimum=82, maximum=140)
```

Use `make_compact_action_bar()` for rows that have compact controls on the left and a right-aligned icon toolbar. This keeps Export and PT Bridge toolbar alignment identical without making their plugin-owned chrome a shared component:

```python
icon_toolbar = make_compact_icon_toolbar(expand_button, collapse_button, None, select_all_button)
action_bar = make_compact_action_bar(
    [mode_combo],
    icon_toolbar,
    object_name="MyPluginActionBar",
)
```

For progress surfaces, keep the plugin's title/chrome outside the shared component and place the shared progress body inside it:

```python
progress_panel = make_progress_panel(
    "Exporting Textures",
    45,
    "12 of 28 maps remaining",
)
progress_panel.setProgress(75, "Exporting...", "Processing assets...")
progress_panel.refreshLayout()
```

For PT Bridge drag/drop trees, keep the panel title and close control in the plugin, then compose the shared drag rows and drag collapsible group inside the panel body:

```python
source_group = make_drag_collapsible_group(
    "Body Textures",
    children=[
        make_drag_tree_item("Main_Layer", draggable=True),
        make_drag_tree_item("Effects_Group", "folder-filled.svg", folder=True, draggable=True),
    ],
)
```

The drag group uses the filled folder icon as its disclosure marker, and drag/drop tree folders use the same filled folder treatment for visual consistency. Click the header to collapse/expand; drag the same header to move the folder as a folder payload. After adding or removing rows, call `source_group.refreshLayout()` so localized text and UI font scale changes keep the clipped animation height accurate.

For compact one-click dock actions, use `make_dock_actions_panel()` and connect the returned buttons:

```python
panel = make_dock_actions_panel()
export_button, bridge_button, settings_button = panel.actionButtons()
export_button.clicked.connect(self.export_selected)
bridge_button.clicked.connect(self.open_bridge)
settings_button.clicked.connect(self.open_settings)
```

## Vendoring For Public Plugin Sharing

During development, import this project as the sibling upstream UI kit. For public plugin sharing, vendor an approved snapshot into each plugin folder so users only need to install that plugin.

Dry-run the default sibling targets:

```powershell
python tools/sync_vendor.py
```

Apply the approved snapshot:

```powershell
python tools/sync_vendor.py --apply
```

Apply one target explicitly:

```powershell
python tools/sync_vendor.py --target ..\rizum-pt-ui-font --apply
```

The sync script copies only the generic shared package and icon assets:

- `rizum_ui/*.py`
- `icons/*.svg`

It does not copy preview files, Painter mockups, palette exports, or plugin entry points. Each target receives a `rizum_ui_vendor_manifest.json` file so later syncs can identify stale vendored files safely. Use `--delete-stale` only with `--apply` when you intentionally want to remove old files listed by a previous manifest.

## `rizum-pt-ui-font`

Use app scope only for an explicit appearance experiment:

```python
from pathlib import Path
import sys

ui_kit_root = Path(__file__).resolve().parents[1] / "rizum-pt-ui-prettier"
if str(ui_kit_root) not in sys.path:
    sys.path.insert(0, str(ui_kit_root))

from rizum_ui import apply_theme

app = QtWidgets.QApplication.instance()
if app is not None:
    apply_theme(app, mode="overlay")
```

Keep the existing reset path so font and style experiments can be backed out during the Painter session.
