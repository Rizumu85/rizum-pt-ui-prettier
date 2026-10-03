# Painter Plugin Integration

## Safe Boundary

Do not patch Substance 3D Painter installation files. Use the UI kit in one of two scopes:

1. Plugin scope: call `apply_theme(self.widget, mode="overlay")` on a plugin panel or dialog.
2. App scope: call `apply_theme(QApplication.instance(), mode="overlay")` from an explicit appearance/font helper plugin.

Plugin scope is the default. App scope is useful for experiments, but it can affect Painter-owned widgets and other plugins.

## Painter Languages

Painter ships nine UI languages: `de`, `en`, `es`, `fr`, `it`, `ja`, `ko`,
`pt`, `zh`. A plugin must work in every one of them and show its own text in
that language. A plugin tested only in an English Painter is untested.

### Which Language To Show

- First candidate: Painter's Language preference, `General/UI_LANGUAGE` in
  `QSettings("Adobe", "Adobe Substance 3D Painter")`. It holds the code of
  the chosen language (`zh`, `ja`, ...).
- Second candidate: `QLocale.system().name()`. The preference starts as
  "Default (System Language)", which names none of the shipped languages and
  makes Painter follow the system locale. A fresh install is in that state.
- Resolve each candidate against the plugin's catalogs by its exact code,
  then by its root (`zh_CN` to `zh`, `pt_BR` to `pt`); a candidate that
  matches nothing is skipped. English is the last resort.
- Do not read Painter's `log.txt`. Its `Using locale:` line is written after
  the plugins have started, so every plugin stayed English on a freshly
  started Painter. Do not use `QLocale()`: Painter leaves Qt's default locale
  alone.
- No language selector, override file or plugin-owned language setting.

`rizum-pt-color-wheel/localization.py` is the reference implementation.

### Catalogs

- Every user-facing string goes through the plugin's `text(key)`. No literal
  user-facing text in code, in any language.
- Ship `i18n/<language>.json` for all nine languages with identical keys
  (`zh-CN.json` also registers `zh`), and keep a test that asserts the
  language set and key parity.
- For Painter's own concepts use Painter's wording in that language. Look it
  up with `tools/painter_translations.py --find "<English text>"` instead of
  translating it afresh.

### Finding Painter's Widgets

Painter passes some of its Qt object names through its translator, so the
same widget can have a different name per language. Known in Painter 12.1:

| Object name | Translated in |
| --- | --- |
| `ActionEditor` (Properties panel) | Chinese, Italian |
| `LayerPropertiesEditor` | Chinese |
| `GeometryMaskView` | Japanese |
| `Symmetry` (toolbar menu) | every language |

`ActionEditor` left Color Wheel and Reference without a tool color in a
Chinese or Italian Painter.

- Find Painter's widgets by class name (`metaObject().className()`) or by an
  object name checked as below. Never match on visible text, window titles
  or tooltips.
- Before relying on an object name, run
  `tools/painter_translations.py <name>`. A message whose source is the name
  and whose context is the widget's parent class means the name is
  translated in the languages listed.
- Then run the plugin once in a non-English Painter.

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

Use `make_segmented_control()` for compact, mutually exclusive modes instead
of a wide combo box or a row of unrelated buttons:

```python
mode_control = make_segmented_control(
    [
        ("Continuous", "continuous"),
        ("15°", "step_15"),
        ("Custom", "custom"),
    ],
    current="step_15",
)
mode_control.currentDataChanged.connect(set_rotation_mode)
mode_control.setCompactHeight(30)
```

The control sizes itself from its labels, supports mouse and arrow-key
selection, and exposes `setCompactHeight()` for runtime UI Font scaling.

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

### Compact Dock Surface

The dock surface around the card must meet Painter's dock header without a
seam, and that header changes with the dock state (measured in Painter 12.1):

| Dock state | Header Painter draws | Surface color |
|---|---|---|
| Floating, or docked alone | Title bar `#2b2b2b` | `COMPACT_DOCK_PANEL_BG` |
| Docked in a tab group | Selected tab `#333333` | `COMPACT_DOCK_TABBED_PANEL_BG` |

`apply_compact_dock_surface(widget)` tracks this automatically: it re-checks
the state when the dock floats, re-docks, is tabbed or resized, and updates the
palette and the `rizumDockTabbed` style property. A plugin that paints its own
surface (for example to cover Painter's `#333333` repaint of unused dock
space) must paint `compact_dock_surface_color(self)`, never a fixed constant:

```python
class _Surface(QtWidgets.QWidget):
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QtGui.QPainter(self)
        painter.fillRect(event.rect(), QtGui.QColor(compact_dock_surface_color(self)))
        painter.end()
```

### Popup Menus

Create every context or dropdown menu with `make_popup_menu(parent)`. It sets
the shared `RizumPopupMenu` identity, masks the rounded corners (translucent
popups are not composited on every Windows setup), shows disabled items as
muted text instead of Painter's grey boxes, and restates the font and spacing
at the current UI Font scale.

Build menus when they open so they read the current scale. A menu kept alive
across scale changes must call `menu.refreshMetrics()` from the plugin's
metrics refresh. Plugin-specific rules go in `extra_stylesheet` so they are
re-applied with the scaled shared rules:

```python
menu = make_popup_menu(self.widget)
menu.addAction("Fit to panel", self.fit)
menu.exec(global_pos)
```

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

The default target set includes the bridge, UI Font, and View Roll plugins.

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
