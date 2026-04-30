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

## Visual Diff Workflow

`pt-ui-font-gemini.html` is the current pixel reference for the UI Font panel. The preview tooling renders both the real HTML reference and the PySide6 panel into `visual-diff/` so small geometry, font, icon, and button differences can be compared directly.

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

`export-dialogue-gemini.html` defines the compact export direction: a 260px dark window, 40px header/top-control bands, inset separators, transparent controls that reveal hover blocks, right-aligned white checkboxes, and 26px pill footer actions. The preview now renders a matching PySide export panel with the same control set: mode select, expand/collapse icons, select-all/select-none icons, checkable parent/child rows, and Cancel/Export actions.

## Folder Fold Animation

`animation.mp4` shows a folder-like group interaction with a stable header row, a rounded hover block around the active group, and content that folds by clipping vertical height while fading the child rows. There is no horizontal slide; the visual polish comes from a short out-cubic height reveal/collapse and a slightly faster opacity fade. Icons or thumbnails sit in the header row and do not need to animate independently.

The shared `make_collapsible_group()` helper follows that pattern. It exposes optional `leading_widget` and `trailing_widget` slots so PT Bridge can later reuse the same group for layer rows with thumbnails, checkboxes, or action buttons.

The final implementation avoids `QGraphicsOpacityEffect` inside collapsible groups because opacity effects can conflict with custom-painted child widgets and produce `QPainter::begin` warnings. `export_dialogue_animated-gemini.html` uses CSS Grid to animate `grid-template-rows` from `0fr` to `1fr` with a `0.3s cubic-bezier(0.25, 1, 0.5, 1)` transition; the PySide helper mirrors that with one internal animated height property that calls `setFixedHeight()` each frame, plus a matching chevron rotation. It intentionally avoids animating `minimumHeight` and `maximumHeight` as separate constraints because that can make Qt layouts recalculate unevenly and cause small collapsed-row jumps. Animation parameters were removed from the public helper API so plugin code gets one stable behavior instead of experimental variants.

`icon-animation-gemini.html` keeps icon micro-interactions intentionally small: no positional hover shift, a brighter hover state, and a short active compression. The shared `make_icon_button()` follows that model with a custom-painted icon inside the existing QPushButton surface: hover recolors the SVG stroke to white, press animates icon scale to `0.85` and opacity to `0.7`, and release eases back with `OutCubic`. Icons render through `QSvgRenderer` at the widget device pixel ratio so the glyph is not softened by a low-resolution `QIcon.pixmap()` pass.

`dropdown-arrow-animation.html` uses a restrained 180 degree chevron rotation with a spring-like 400ms curve. The compact combo input mirrors that by rotating its passive painted chevron when the popup menu is open and easing it back when the menu closes. The arrow animation stays glyph-only so it does not create a separate hover surface or shift the field layout.

Combo popups use non-blocking `QMenu.popup()` instead of `exec()` so clicking the same field while the menu is open can close it. A short close debounce prevents the same click from closing the menu and immediately reopening it. Collapsible content uses a single fixed-height clipping frame so child rows can appear during expansion without delayed pop-in while still avoiding competing min/max layout constraints.

## Handoff Notes For Next Session

Recent iteration notes:

- `make_combo_input()` now supports `setFitToContents(False)`. Keep export's `All Sets / Current Set` control fit-to-content, but keep UI Font's font-family combo expanded across the row. The regression where UI Font looked skewed came from applying fit-to-content to every combo.
- The export dropdown should contain only `All Sets` and `Current Set`; no `Selected Channels` and no `Current Stack`.
- The dropdown arrow animation still needs live Painter/preview validation. If a background block appears while rotating upward, inspect `CompactChevronDown` repaint/composition first. Avoid manual transparent `CompositionMode_Source` fills; that produced a black square in offscreen renders.
- SVG icon sharpness is considered fixed after switching icon buttons to `QSvgRenderer` rendering at device pixel ratio.
- The export preview window is 284px wide, the smallest measured width that keeps the full top-control toolbar at its natural size without clipping while staying close to the original 260px HTML reference. Its mode dropdown sizes to the longest option (`Current Set`) after final widget fonts/styles are applied. Its passive chevron intentionally does not rotate, matching the HTML material/export mockup behavior where only the whole select surface gets hover feedback.
- The collapsible group animation remains the most fragile area. Attempts tried so far:
  - dual `minimumHeight`/`maximumHeight` animation caused layout jitter;
  - `QScrollArea` clipping introduced clipped-row artifacts and stale scroll-offset behavior;
  - hiding children during the height animation removed artifacts but caused a visible delayed pop-in.
  The current version uses a single fixed-height clipping frame with live child widgets kept at a stable full content geometry. The clipping frame height and the outer group frame height are synchronized in the same animated-height setter, so the hover/background frame does not wait for the parent layout's next pass and jitter behind the content. Child rows are not resized per frame and no cached pixmap is swapped in, which avoids text raster/position jumps on `basecolor` and `User1`. Mid-animation toggles are allowed; each new toggle stops the previous animation and starts from the current frame height.
- User preference remains: no unnecessary outlines, unified dark surfaces, subtle hover blocks with breathing room, stable layout with no horizontal/vertical drift, and polished but restrained animation.
