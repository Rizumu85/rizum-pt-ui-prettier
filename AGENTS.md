# Agent Notes

- Rizum Guidelines are active for this project/thread until the user says otherwise.
- Keep project files, code comments, and documentation in English.
- Keep changes small and directly tied to the shared Painter UI component library.
- This project is a sibling helper library for Painter plugins such as `rizum-pt-to-ps-bridge` and `rizum-pt-ui-font`.

## Required reading

- **`docs/font-scale-adaptation.md`** — Before adding or modifying any shared compact component (painted icon button, stepper, chevron, field control, footer button), read this standard. Every component with painted internals or a fixed pixel size must expose a runtime size setter (`setPaintedIconSize` / `setButtonSize` / `setSize` / `setCompactHeight`) so `rizum-pt-ui-font` can scale it at runtime. The doc contains the API contract, the caller pattern, and a checklist. Skipping it produces controls that clip or refuse to scale when the UI font grows.
