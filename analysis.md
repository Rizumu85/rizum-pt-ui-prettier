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
