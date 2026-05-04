# Analysis

## Current Context

`rizum-pt-ui-prettier` starts as an empty sibling plugin folder next to:

- `rizum-pt-to-ps-bridge`, which currently builds Painter UI directly with PySide6 widgets and local stylesheets.
- `rizum-pt-ui-font`, which applies application-level Qt font settings inside Substance 3D Painter.

## Technical Direction

Substance 3D Painter exposes PySide6 through its Python plugin runtime. A shared component library can live in this folder as an importable Python package and be added to `sys.path` by sibling plugins.

The safe styling boundary is:

- Style owned plugin widgets and dialogs with Qt stylesheets.
- Provide an optional application-level theme helper for fonts and broad Qt widget polish.
- Avoid modifying Painter installation files or private UI resources.

## Conclusions

The practical architecture is a small PySide6 library with:

- Design tokens for color, spacing, radius, typography, and animation timing.
- A stylesheet generator for dark modern Painter-friendly widgets.
- Component factories/subclasses for common controls.
- A preview app that can be run outside Painter for fast visual iteration.

This keeps the design system reusable without coupling it to a single plugin.

For distribution, the development source and the plugin-shared artifact should be separate. During design and implementation, `rizum-pt-ui-prettier` remains the upstream component lab and preview surface. After the real Painter plugins are tested and approved, public plugin packages should vendor a snapshot of the needed `rizum_ui` files and icons directly inside each plugin folder. That keeps shared plugins self-contained for users while preserving this repository as the place to tune components and re-sync future snapshots.

For a public GitHub audience beyond Substance Painter, keep the generic PySide6 package prominent and keep Painter-specific plugin files, host-preview docks, and SP integration examples in clearly marked documentation or example folders. Non-Painter users should be able to understand and reuse the component library without first learning Painter plugin structure.

## Visual Diff Workflow

`references/html/pt-ui-font-gemini.html` is the current pixel reference for the UI Font panel. The preview tooling renders both the real HTML reference and the PySide6 panel into `visual-diff/` so small geometry, font, icon, and button differences can be compared directly.

Important findings:

- The HTML panel uses `--panel-width: 356px`, but the screenshot size is `358x232` because the CSS border is outside the content width.
- HTML divider lines are header/footer pseudo-elements and do not consume layout height.
- The Size mock input is `88px` wide in the screenshot: `70px` content width plus horizontal padding and border.
- Native Qt SpinBox, ComboBox, and CheckBox rendering does not match the HTML mockup closely enough for visual tuning, so the preview uses mock controls for this panel.
- Qt high-DPI screenshots must be normalized to 1x before comparing with Playwright screenshots, otherwise text looks softer than the HTML reference.

## Runtime Font Scaling

`pt-ui-font` owns the actual application font family and scale. The shared UI kit should not force a font family, but compact controls still need relayout hooks because Painter plugins may increase the current Qt font after the panel has already been built.

The compact helpers now keep references to their internal labels/controls and expose relayout functions for field rows and inline checkbox rows. Integrating plugins should call those helpers after applying a new font so fixed widths, footer buttons, and minimum dock width are recomputed from the active font metrics.

## Export Dialog Reference

`references/html/export_dialogue_animated-gemini.html` defines the compact export direction: a 260px dark window, 40px header/top-control bands, inset separators, transparent controls that reveal hover blocks, right-aligned white checkboxes, and 26px pill footer actions. The preview now renders a matching PySide export panel with the same control set: mode select, expand/collapse icons, select-all/select-none icons, checkable parent/child rows, and Cancel/Export actions.

## Dock Actions Reference

`references/html/pt-dock-gemini.html` defines a compact dock action panel with a rounded dark shell, three equal vertical action buttons, a white primary action, and transparent secondary buttons. Browser measurement of the HTML reference gives a `282x78` outer panel including the 1px border, `14px` CSS padding plus the border (`15px` Qt layout margins), `8px` button gaps, and three roughly `78.66x48` action buttons. The shared `make_dock_actions_panel()` and `make_dock_action_button()` helpers keep the measured `78px` height, `48px` button height, padding, gap, icon size, and type size, while using the user's tighter approved width so the default PySide panel is `260x78` with roughly `71/72/71px` action buttons. The icon and label are centered as one vertical group so the icon top distance and label bottom margin stay balanced. The panel remains a generic PySide6 component; plugin-specific behavior should be attached by connecting each returned button's normal Qt signals.

## PT Bridge Settings Reference

`references/html/settings-gemini.html` defines the first pass for the PT Bridge settings panel. Browser measurement gives a `342x537` outer settings window including the 1px border, a `340x40` header, a `340x447` body, a `340x48` footer, `316px` body rows, and row heights of `40`, `51`, `51`, `36`, `45`, and `34`. The preview now includes a dedicated `Settings` tab that matches those measured dimensions and keeps light/dark/system theme switching as an internal reserved API (`setTheme(...)`) while defaulting to the current dark Painter-like mode because Substance Painter does not currently expose a light host mode for this plugin.

`references/html/settings_better-animation-gemini.html` and `references/html/settings_pro_v10_final.html` are used as interaction addenda, not replacement layouts. The full settings preview keeps the settings panel structure and dimensions, while adopting the snappier theme segmented-control slider timing, the toggle switch proportion, the toggle movement, and the final padding/dilation reveal behavior.

The settings dilation stepper keeps the compact `24px` controls from the HTML reference, but the minus/plus controls use the same press/release micro-interaction as shared icon buttons. The center value is editable via a compact integer `QLineEdit` so plugin settings can accept typed values without changing the row geometry.

## Folder Fold Animation

`references/media/animation.mp4` shows a folder-like group interaction with a stable header row, a rounded hover block around the active group, and content that folds by clipping vertical height while fading the child rows. There is no horizontal slide; the visual polish comes from a short out-cubic height reveal/collapse and a slightly faster opacity fade. Icons or thumbnails sit in the header row and do not need to animate independently.

The shared `make_collapsible_group()` helper follows that pattern. It exposes optional `leading_widget` and `trailing_widget` slots so PT Bridge can later reuse the same group for layer rows with thumbnails, checkboxes, or action buttons.

The final implementation avoids `QGraphicsOpacityEffect` inside collapsible groups because opacity effects can conflict with custom-painted child widgets and produce `QPainter::begin` warnings. `references/html/export_dialogue_animated-gemini.html` uses CSS Grid to animate `grid-template-rows` from `0fr` to `1fr` with a `0.3s cubic-bezier(0.25, 1, 0.5, 1)` transition; the PySide helper mirrors that with one internal animated height property that calls `setFixedHeight()` each frame, plus a matching chevron rotation. It intentionally avoids animating `minimumHeight` and `maximumHeight` as separate constraints because that can make Qt layouts recalculate unevenly and cause small collapsed-row jumps. Animation parameters were removed from the public helper API so plugin code gets one stable behavior instead of experimental variants.

`references/html/icon-animation-gemini.html` keeps icon micro-interactions intentionally small: no positional hover shift, a brighter hover state, and a short active compression. The shared `make_icon_button()` is the canonical renderer for interactive toolbar/action icons. It custom-paints the icon inside the existing QPushButton surface, renders the SVG through `QSvgRenderer` into a transparent device-pixel-ratio-aware pixmap, then recolors through the icon alpha mask with `CompositionMode_SourceIn`. This keeps icons sharp and guarantees that source SVG stroke colors, including dark strokes such as `checkmark.svg`, cannot make an enabled icon disappear on the dark Painter surface. Hover recolors to white, press animates icon scale to `0.85` and opacity to `0.7`, and release eases back with `OutCubic`.

Passive icon labels are separate from the icon-button standard. Use `make_svg_label()` for non-interactive one-off glyphs, and use `make_tree_icon_label()` for tree/list row glyphs so filled folders, layer sizing, and mask badges stay centralized. Keep passive sizes explicit when a component has a fixed compact row geometry, and use the no-color path unless a forced tint is required. Do not replace interactive toolbar icons with ad hoc QLabel/SVG rendering or `QIcon.pixmap()`; the icon-button path is the stable visual standard.

Tree rows now share small primitives rather than one large cross-purpose component. `make_tree_icon_label()` owns filled folder selection, 16px layer glyphs, and mask badges. `bind_hover_state()` owns the stable `hovered` property across host/row/child widgets, so export selection rows and drag/drop rows can keep separate business behavior without reintroducing label/checkbox hover gaps.

Source SVG files must use the shared icon canvas standard even though the PySide render path passes an explicit target rectangle. Every shared icon should declare `width="24" height="24" viewBox="0 0 24 24"`, use a 2px stroke with round caps and joins for outline strokes, and default to `#9E9E9E` unless the icon has a deliberate component-specific color such as the dark checkmark used inside a white confirmation control. Do not compensate for visual weight by changing intrinsic SVG width/height or per-file canvas size; tune the path geometry inside the 24x24 viewBox instead. Filled accents, such as `folder-filled.svg` or the filled top plate in `layers.svg`, should use the same neutral color as the outline so file browser previews and Qt renders stay visually consistent.

`dropdown-arrow-animation.html` uses a restrained 180 degree chevron rotation with a spring-like 400ms curve. The compact combo input mirrors that by rotating its passive painted chevron when the popup menu is open and easing it back when the menu closes. The arrow animation stays glyph-only so it does not create a separate hover surface or shift the field layout.

Combo popups use non-blocking `QMenu.popup()` instead of `exec()` so clicking the same field while the menu is open can close it. A short close debounce prevents the same click from closing the menu and immediately reopening it. Collapsible content uses a single fixed-height clipping frame so child rows can appear during expansion without delayed pop-in while still avoiding competing min/max layout constraints.

## Handoff Notes For Next Session

Recent iteration notes:

- `make_combo_input()` now supports `setFitToContents(False)`. Keep export's `All Sets / Current Set` control fit-to-content, but keep UI Font's font-family combo expanded across the row. The regression where UI Font looked skewed came from applying fit-to-content to every combo.
- The export dropdown should contain only `All Sets` and `Current Set`; no `Selected Channels` and no `Current Stack`.
- The dropdown arrow animation still needs live Painter/preview validation. If a background block appears while rotating upward, inspect `CompactChevronDown` repaint/composition first. Avoid manual transparent `CompositionMode_Source` fills; that produced a black square in offscreen renders.
- SVG icon sharpness is considered fixed after switching icon buttons to `QSvgRenderer` rendering at device pixel ratio and alpha-mask recoloring with `CompositionMode_SourceIn`. Future interactive toolbar/action icons should use `make_icon_button()` instead of direct `QIcon.pixmap()` or custom label renderers.
- The export preview window is 260px wide, matching the compact HTML reference while keeping the full top-control toolbar and right-aligned checkboxes visually aligned without clipping. Its mode dropdown sizes to the longest option (`Current Set`) after final widget fonts/styles are applied. Its passive chevron intentionally does not rotate, matching the HTML material/export mockup behavior where only the whole select surface gets hover feedback.
- The shared component boundary intentionally excludes plugin/window chrome such as the top `Export` title and close `x`; PT Bridge and UI Font should keep their own panel header/chrome. Shared internals now include `make_compact_action_bar()`, `make_compact_icon_toolbar()`, `make_export_tree_item()`, `update_export_tree_item()`, `compact_action_bar_width()`, `compact_top_controls_width()`, `make_combo_input()`, and `make_collapsible_group()`.
- For i18n or runtime UI Font scale changes, refresh internal controls after applying the new strings/font: call `combo.setItems(...)` or `combo.refreshMetrics()`, call `action_bar.refreshLayout()`, recompute compact panel width with `compact_action_bar_width(...)` or the legacy `compact_top_controls_width(...)`, call `row.refreshLayout(...)` or `update_export_tree_item(...)` for export rows, call `group.refreshLayout(title, subtitle)` so the stable live-clipped animation recalculates its content height, and call `button.refreshLayout(minimum=..., maximum=...)` for compact footer action buttons.
- `references/html/pro_progress_bar-animated-gemini.html` is translated into the shared `make_progress_panel()` component. It owns the status/percent/meta body and 4px animated white progress fill, but plugin-owned title bars such as `Processing...` stay outside the shared component boundary. For i18n and UI font scale changes, call `progress_panel.setProgress(...)` or `progress_panel.refreshLayout(...)`; the default width stays near the 320px reference and clamps long localized text to 420px with wrapping.
- `references/html/pt-bridge_drag_drop-animated-gemini.html` now has a dedicated `Drag Drop` preview tab. The preview keeps plugin/window chrome local to PT Bridge, while reusing shared internals such as compact combo inputs, icon toolbar spacing, inset separators, SVG labels, `make_drag_tree_item()`, and `make_drag_collapsible_group()`. The drag group variant uses the filled folder icon as the only disclosure marker, and all folder rows in the drag/drop tree use the filled folder style for consistency. It keeps child row indentation/hover geometry consistent with the export collapsible group, supports dragging the folder header itself, renders the drag ghost into a transparent pixmap, shows a white insertion line while hovering the target group, keeps drag/remove hover actions hidden until row hover, and reveals dropped rows with the HTML mockup's 0.3s OutCubic slide/fade timing.
- Shared icon files now use one intrinsic SVG standard: `width="24" height="24" viewBox="0 0 24 24"`, 2px outline strokes, round caps/joins, and neutral `#9E9E9E` strokes/fills unless a component explicitly requires another color. This prevents file-browser previews and Qt fallback paths from making matching 24px viewBox icons appear different because one file declared an 8px, 10px, 14px, or 19px canvas. Keep `layers.svg` as a filled top plate plus one lower layer line, and keep filled folder content the same color as its outline.
- The collapsible group animation remains the most fragile area. Attempts tried so far:
  - dual `minimumHeight`/`maximumHeight` animation caused layout jitter;
  - `QScrollArea` clipping introduced clipped-row artifacts and stale scroll-offset behavior;
  - hiding children during the height animation removed artifacts but caused a visible delayed pop-in.
  The current version uses a single fixed-height clipping frame with live child widgets kept at a stable full content geometry. The clipping frame height and the outer group frame height are synchronized in the same animated-height setter, so the hover/background frame does not wait for the parent layout's next pass and jitter behind the content. Child rows are not resized per frame and no cached pixmap is swapped in, which avoids text raster/position jumps on `basecolor` and `User1`. Mid-animation toggles are allowed; each new toggle stops the previous animation and starts from the current frame height.
- User preference remains: no unnecessary outlines, unified dark surfaces, subtle hover blocks with breathing room, stable layout with no horizontal/vertical drift, and polished but restrained animation.
