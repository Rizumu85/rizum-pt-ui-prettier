# Agent Notes
- DO NOT send optional commentary
- Spend time on thinking; you do not need to use the commentary channel to report progress to me.
- Bilingual Guideline Effective.
- Keep changes small and directly tied to the shared Painter UI component library.
- This project is a sibling helper library for Painter plugins such as `rizum-pt-to-ps-bridge` and `rizum-pt-ui-font`.

## Development discipline

- Before ending any conversation that changes project files, create focused commits grouped by concern and push each completed group to the configured remote for backup. Never mix unrelated existing work into those commits.
- Add comments only to preserve non-obvious decisions, especially user requirements or tradeoffs that a future refactor might otherwise undo. Do not narrate what the code does, repeat rationale across files, or let comments proliferate without purpose.
- Diagnose bugs through the overall implementation flow, ownership, coupling, and architecture before patching symptoms. Prefer instrumentation and captured runtime data over guesses, and avoid one-off fixes that move the problem elsewhere.
- Before adding a feature, inspect the existing architecture and research the relevant stack. Evaluate integration boundaries, performance, maintainability, and the feature's appropriate product and UI hierarchy from a human designer's perspective before implementing.
- When project direction changes, remove obsolete fallback paths and experimental remnants instead of carrying both designs forward. Keep a fallback only when a concrete runtime requirement justifies it.
- Keep Markdown documentation intentional and sparse. Record material only when the user explicitly asks, or when a durable architectural or product constraint would otherwise be lost; do not turn documentation into a development diary.

## Required reading

- **`docs/font-scale-adaptation.md`** — Before adding or modifying any shared compact component (painted icon button, stepper, chevron, field control, footer button), read this standard. Every component with painted internals or a fixed pixel size must expose a runtime size setter (`setPaintedIconSize` / `setButtonSize` / `setSize` / `setCompactHeight`) so `rizum-pt-ui-font` can scale it at runtime. The doc contains the API contract, the caller pattern, and a checklist. Skipping it produces controls that clip or refuse to scale when the UI font grows.
