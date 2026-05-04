# Plan

## Working Agreement

- Rizum Guidelines are active for this project/thread until the user says otherwise.

## Direction 1: Shared UI Kit

Goal: Build a small reusable PySide6 UI library for Rizum Painter plugins.

- [x] Create project docs and working agreement.
- [x] Add theme tokens and stylesheet helpers.
- [x] Add reusable component helpers for buttons, panels, forms, and status surfaces.
- [x] Add animation helpers that are safe for normal Qt widgets.
- [x] Add a compact dock actions panel for shareable one-click plugin actions.
- [x] Add a measured PT Bridge settings preview with reserved light/dark theme switching.
- [x] Study the Gemini HTML mockups and align the PySide6 visual tokens.
- [x] Update the style rules for unified backgrounds, fewer outlines, larger text, breathable buttons, and filled checkbox tiles.
- [x] Capture the north-star style summary and align checkbox selection with the pure-white command language.

## Direction 2: Preview Workflow

Goal: Let UI changes be previewed without restarting Substance 3D Painter.

- [x] Add a standalone PySide6 preview app.
- [x] Include representative PT Bridge and UI Font surfaces in the preview.
- [x] Document how to run and iterate on the preview.
- [x] Add a Painter-like host baseline for no-Painter previewing.
- [x] Keep the default component stylesheet in overlay mode.
- [x] Add auto-refresh for UI-kit module changes while the preview stays open.
- [x] Add a standalone Painter preview dock for real host visual checks.
- [x] Use a fixed Painter-like host stylesheet for external preview controls instead of live Painter palette sync.
- [x] Add screenshot tooling to compare the real UI Font HTML mockup with the PySide6 preview.
- [x] Align the UI Font preview panel to the HTML reference geometry, icons, checkbox, and button sizing.
- [x] Promote the tuned UI Font controls into reusable shared components.
- [x] Update the UI Font preview to mirror the live compact dock/card implementation.
- [x] Align the PT Bridge preview controls with the export dialog HTML reference.
- [x] Add a reusable animated collapsible group for folder/layer-style rows.
- [ ] Re-check dropdown arrow behavior, combo popup toggle behavior, export dropdown width, and live-clipped collapsible group animation in a fresh session against live Painter recordings.

## Direction 3: Painter Integration

Goal: Make existing plugins able to opt into the shared UI kit.

- [x] Document sibling import strategy for Painter plugin folders.
- [x] Provide a minimal integration snippet for `rizum-pt-to-ps-bridge`.
- [x] Provide a minimal integration snippet for `rizum-pt-ui-font`.
- [x] Add runtime relayout helpers so compact components can respond to plugin-owned font scaling.

## Direction 4: Distribution Strategy

Goal: Keep preview-driven component development centralized while making shared plugins self-contained.

- [ ] Implement final components in the real Painter plugins using this project as the development source.
- [ ] After live Painter testing is approved, vendor a snapshot of the needed `rizum_ui` files and icons directly into each plugin that will be shared publicly.
- [x] Add a repeatable sync script or documented command that copies the approved component snapshot from this project into each plugin.
- [ ] Keep the vendored plugin copy self-contained so recipients do not need to install `rizum-pt-ui-prettier`.
- [ ] Keep this repository as the upstream preview/component lab for future updates, then re-sync plugin-local copies after new preview changes are approved.
- [ ] Restructure public GitHub documentation so generic PySide6 users see the reusable component library first, while Substance Painter plugin examples live in a clearly marked `examples/substance-painter` or adapter section.
- [ ] Separate SP-specific plugin files from the generic UI kit surface so non-Painter users are not confused by Painter entry points.
