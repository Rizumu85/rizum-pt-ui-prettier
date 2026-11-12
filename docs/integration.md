# Painter Plugin Integration

## New Plugin Checklist

A new plugin is not done until each of these holds. The sections below give
the reasons.

1. The UI kit is vendored with `tools/sync_vendor.py`, never copied or edited
   by hand ("Vendoring For Public Plugin Sharing").
2. The entry module starts the exit guard before it builds any UI and removes
   it as the first statement of `close_plugin`, before any early return
   ("Python Event Filters And Painter's Exit"):

   ```python
   from .rizum_ui import exit_guard

   _EXIT_GUARD = None


   def start_plugin():
       global _EXIT_GUARD
       _EXIT_GUARD = exit_guard.install()
       ...


   def close_plugin():
       global _EXIT_GUARD
       exit_guard.remove(_EXIT_GUARD)
       _EXIT_GUARD = None
       ...
   ```

3. Every user-facing text goes through the plugin's `localization.py`, bound
   to `rizum_ui.localization`, with catalogs for all nine Painter languages
   and a test for key parity ("Painter Languages").
4. Painter's own widgets are found by class name or by an object name checked
   with `tools/painter_translations.py`, never by visible text ("Finding
   Painter's Widgets").
5. A deferred call runs from a timer its object owns, never from
   `QTimer.singleShot`, and a menu or dialog is deleted after `exec()`
   ("Deferred Calls, Menus And Dialogs").
6. A key the user picks is checked with `rizum_ui.painter_shortcuts`
   ("Shortcut Conflicts").
7. The repository carries the root `conftest.py` and `pytest.ini`, so
   `python -m pytest` runs its tests, and a test for catalog key parity
   ("Plugin Tests").
8. The plugin has been started once in a non-English Painter.

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

`rizum_ui/localization.py` implements this mechanism. A plugin's
`localization.py` keeps only its own texts (`FALLBACK_TEXT` and `i18n/`) and
binds the shared functions to them, exposing `text(key, *, language=None,
**values)`, `CURRENT_LANGUAGE`, `resolve_language()`, `supported_languages()`
and `CATALOGS`. The module imports PySide6 only when it reads a candidate, so
checks without PySide6 can load it with a stub.

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

Keep the wrapper a widget was found through. `sp.ui.get_main_window()` only
wraps Painter's window, and with Painter's PySide (6.8) everything found
through a wrapper with `findChild` or `findChildren` turns invalid when that
wrapper is collected ("Internal C++ object already deleted"), although
Painter deleted nothing.

- `sp.ui.get_main_window().findChild(...)` in one expression returns a widget
  that is invalid on the next line, unless some other code happens to hold
  the main window wrapper. Reference and Color Wheel worked beside Time
  Tracker and View Roll, which hold it, and failed without them.
- A plugin that looks up Painter's widgets keeps the main window wrapper
  while it runs and finds everything through that one, and lets go of it
  when it closes (see "Painter's Widgets And Painter's Exit").
- The PySide on a development machine may not behave this way, so a unit
  test does not show it. Check in Painter with the other plugins disabled.

## Python Event Filters And Painter's Exit

A Python application event filter (`QApplication.installEventFilter`) makes
Painter crash when it exits: an access violation in `shiboken6` under
`~QPMCache`, seen as a crash report after closing Painter.

PySide tags every C++ QObject it passes to Python with a dynamic property
whose destructor calls back into the bindings. An application filter is
passed every object that receives an event, including Qt's global pixmap
cache, a static that Painter destroys after it has unloaded the bindings.

- Every plugin calls `rizum_ui.exit_guard.install()` when it starts and
  `exit_guard.remove(guard)` when it closes, whether or not it installs a
  filter itself: the UI kit's steppers and menus install short-lived ones.
- The guard replaces the property on the cache once and removes itself; one
  guard protects every Python filter in the process.
- `tools/exit_crash_repro.py` reproduces the crash and shows the guard
  preventing it. If a crash dump shows another Qt static under the same
  stack, add its class name to `STATIC_CLASSES`.

## Painter's Widgets And Painter's Exit

A wrapper of something Painter owns must not outlive the plugin's close.
Everything found through a wrapper hangs on it as a child wrapper. Painter
destroys its widgets after it has closed the plugins and run a collection,
and wrappers that are still alive then, with such children, crash it when it
unloads the bindings: access violation in shiboken's `~BindingManager`, the
crash report on most exits (found 2026-10-13 after the user met it on every
exit; reproduced and bisected with real exits of temporary Painters).

Three things kept such wrappers alive, each invisible to Python's collector:

- A module-level variable holding the main window wrapper. A plugin sets it
  to `None` as the last step of its close.
- A connection made from Python to a signal of Painter's main window. It
  keeps the window's wrapper alive for as long as Painter runs, with the
  whole tree found through it by any plugin (measured: 66 wrapper families
  left after close, 2 without the connection). Do not connect to signals of
  Painter's main window. The kit's dock state tracker did, for
  `tabifiedDockWidgetActivated`; it now follows the dock's own signals and
  events, which a tab change also raises.
- An object that holds a wrapper of the widget it filters events for, or a
  closure connected to a signal: the watched object or the sender keeps it,
  it keeps them, and the collector sees neither link. A closed panel stayed
  alive whole this way, still holding Painter's widgets it had looked up.
  Keep no wrapper in an event filter object (use `parent()`), connect
  methods of QObjects instead of closures, and at close set every attribute
  that holds one of Painter's widgets to `None` instead of counting on the
  object being collected.

How to check: `python tools/painter_close_check.py`, before releasing a
change that looks up, keeps or connects to something of Painter's, or that
changes how a plugin closes. It starts a temporary Painter, closes the
plugins the way Painter's exit does and fails if Painter's main window is
still wrapped or a plugin's module or object still holds one of Painter's
widgets or actions. The user asked for it as the standing guard: the cause
shows on every run, where the crash it leads to depends on the order
shiboken tears its wrappers down and stayed away on some exits. For the same
reason one clean real exit proves nothing; when real exits are needed, run
several.

For digging further inside Painter: `shiboken6.getAllValidWrappers()` lists
what is wrapped, `shiboken6.dump()` shows a wrapper's parent and children
(it crashes on a wrapper with a dead child, the state that also crashes the
exit), and `gc.get_referrers()` names who holds an object.

## Deferred Calls, Menus And Dialogs

- Run a deferred call from a single-shot `QTimer` that is a child of the
  object it calls, never from `QTimer.singleShot`. The owned timer dies with
  its object. A `singleShot` call still fires after the plugin has closed, on
  widgets that are gone, and PySide never releases the callable of a
  zero-delay call it drops, which keeps the object alive.
- Call `deleteLater()` on a menu built with `make_popup_menu` and on a dialog
  parented to Painter's window once `exec()` returns. Qt keeps both as
  children of their parent: every opening would add one, and a child of
  Painter's window outlives the plugin's close.

## Shortcut Conflicts

Qt fires neither of two enabled actions that share a shortcut, so a plugin
key that Painter already uses silently disables a Painter command. A plugin
that lets the user pick a key marks such a key with
`rizum_ui.painter_shortcuts`: `registered_shortcut_index(main_window,
ignore=own_actions)` once per dialog, then `shortcut_conflicts(key, index)`.
Do not scan Painter's actions privately: the shared scan compares keys in
their portable spelling and keeps none of the wrappers it reads.

## Plugin Tests

A plugin's repository root is the plugin package and its `__init__.py`
imports `substance_painter`, so pytest fails while collecting it. Every
plugin repository carries the root `conftest.py` (collects the root as a
plain directory) and `pytest.ini` (`testpaths = tests`), copied from an
existing plugin, so `python -m pytest` runs the suite. The suite includes the
test that asserts the nine catalogs and their identical keys.

## ACE Color Management And Painter's Exit

Painter 12.1.2 itself crashes on exit when the project open at that moment
uses Adobe ACE color management, with or without plugins: an access violation
in `ACE.dll` under `~ToolBarSourceColorPickerView`, followed by Painter's
crash report window. The swatch in the contextual toolbar releases its ACE
transform while the main window is destroyed, after Painter has freed it.
Users take the plugins for the cause, so the exit guard works around it.

- `exit_guard.remove()` deletes that toolbar view when the plugins are closed
  for the exit, which is after Qt's `aboutToQuit` and before Painter destroys
  its windows. A plugin that is only disabled or reloaded leaves it alone.
- The same two calls as above cover it. `remove()` must be called in
  `close_plugin` even when `install()` returned `None`, and before any early
  return: a close that returns early because the plugin built nothing skips
  the workaround, and Painter crashes on that exit.
- Measured in a temporary Painter with a project created under
  `PAINTER_ACE_CONFIG`: exit code `0xC0000005` without the guard, `0` with
  it, also with a single plugin. Legacy projects exit cleanly either way.
- Painter's own crash dumps are in
  `%APPDATA%\Adobe\Adobe Substance 3D Painter\Sentry-Crashpad\reports`, not in
  Windows' `CrashDumps` folder.

## Using The Kit In A Plugin

Import the kit from the plugin's vendored copy and apply the theme once to
the plugin's own root widget:

```python
from .rizum_ui import apply_theme, make_icon_button

self.widget = QtWidgets.QWidget()
self.widget.setObjectName("RizumMyPluginPanel")
apply_theme(self.widget, mode="overlay")
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

Build menus when they open so they read the current scale, and delete them
when they close ("Deferred Calls, Menus And Dialogs"). A menu kept alive
across scale changes must call `menu.refreshMetrics()` from the plugin's
metrics refresh. Plugin-specific rules go in `extra_stylesheet` so they are
re-applied with the scaled shared rules:

```python
menu = make_popup_menu(self.widget)
menu.addAction("Fit to panel", self.fit)
menu.exec(global_pos)
menu.deleteLater()
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

Every plugin holds its own copy of the kit, so users only need to install that plugin. The copy is written by `tools/sync_vendor.py` and never edited by hand: a fix goes into this project and is synced out.

Dry-run, then apply:

```powershell
python tools/sync_vendor.py
python tools/sync_vendor.py --apply
```

Without `--target` the tool syncs every sibling `rizum-pt-*` folder that already has a `rizum_ui_vendor_manifest.json`. A new plugin, or one plugin alone, is named:

```powershell
python tools/sync_vendor.py --target ..\rizum-pt-ui-font --apply
```

A plugin whose manifest carries `"pinned": "<reason>"` is left out of the default set and printed as skipped with its reason. Pin a plugin whose copy must not be overwritten yet: one that still holds edits made in the plugin, or a deliberate older snapshot. It is synced only when named with `--target`, and the sync keeps the pin.

The sync script copies only the generic shared package and icon assets:

- `rizum_ui/*.py`
- `icons/*.svg`

It does not copy preview files, Painter mockups, or plugin entry points. Files are compared without regard to line endings, so a copy that differs only in those is left alone. Each target receives a `rizum_ui_vendor_manifest.json` file so later syncs can identify stale vendored files safely. Use `--delete-stale` only with `--apply` when you intentionally want to remove old files listed by a previous manifest.
