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
