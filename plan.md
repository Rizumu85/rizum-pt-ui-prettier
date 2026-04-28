# Plan

## Working Agreement

- Rizum Guidelines are active for this project/thread until the user says otherwise.

## Direction 1: Shared UI Kit

Goal: Build a small reusable PySide6 UI library for Rizum Painter plugins.

- [x] Create project docs and working agreement.
- [x] Add theme tokens and stylesheet helpers.
- [x] Add reusable component helpers for buttons, panels, forms, and status surfaces.
- [x] Add animation helpers that are safe for normal Qt widgets.

## Direction 2: Preview Workflow

Goal: Let UI changes be previewed without restarting Substance 3D Painter.

- [x] Add a standalone PySide6 preview app.
- [x] Include representative PT Bridge and UI Font surfaces in the preview.
- [x] Document how to run and iterate on the preview.

## Direction 3: Painter Integration

Goal: Make existing plugins able to opt into the shared UI kit.

- [x] Document sibling import strategy for Painter plugin folders.
- [x] Provide a minimal integration snippet for `rizum-pt-to-ps-bridge`.
- [x] Provide a minimal integration snippet for `rizum-pt-ui-font`.
