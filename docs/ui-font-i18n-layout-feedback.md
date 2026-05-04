# UI Font i18n Layout Feedback

## Working Agreement

- Rizum Guidelines are active for this project/thread until the user says otherwise.

## Context

`rizum-pt-ui-font` now externalizes UI strings in `i18n/*.json` and supports the Substance 3D Painter language set: English, German, Spanish, French, Italian, Japanese, Korean, Portuguese, and Simplified Chinese.

The plugin intentionally does not add a visible language selector. Language detection happens without UI by reading overrides first, then Painter's local `log.txt` locale line, then Qt locale fallbacks.

## Problem

The compact UI does not adapt when localized text is longer than the English source strings. Current symptoms and risks:

- `make_field_row(..., label_width=...)` expects the caller to pre-pick a label width.
- Footer buttons use fixed widths from the caller, so labels like `Zurucksetzen`, `Reinitialiser`, `Restablecer`, and `Ripristina` can clip or feel cramped.
- Inline checkbox text is constrained by fixed/minimum widths and can clip in German, French, Italian, Spanish, and Portuguese.
- Tooltips are fine, but visible labels need layout-aware sizing.

## Desired Direction

Please solve this in `rizum-pt-ui-prettier`, not inside `rizum-pt-ui-font`, so all compact Painter panels get consistent localized text-fit behavior.

Suggested API-level improvements:

- Allow `make_field_row` to auto-size label width from `QFontMetrics.horizontalAdvance(label_text)` with min/max clamps.
- Provide a helper for localized footer buttons that computes width from text plus padding, with compact min/max bounds.
- Provide a helper for inline checkbox rows that keeps the text and checkbox visible without fixed text widths.
- Keep compact English layout visually unchanged when text is short.
- Avoid changing the visual style; this is a layout sizing issue, not a theme redesign.

## Verification Cases

Use these visible strings as stress cases:

- German: `Zurucksetzen`, `Systemstandard`, `Schriftliste aktualisieren`
- Spanish: `Predeterminada del sistema`, `Restablecer`, `Actualizar lista de fuentes`
- French: `Reinitialiser`, `Police systeme`, `Actualiser la liste des polices`
- Italian: `Predefinito di sistema`, `Ripristina`, `Aggiorna elenco font`
- Portuguese: `Padrao do sistema`, `Redefinir`, `Atualizar lista de fontes`
- Japanese/Korean/Chinese: check font rendering and row height, not only string length

## Current Owner Boundary

`rizum-pt-ui-font` owns translation keys and runtime language detection. `rizum-pt-ui-prettier` should own responsive text sizing and compact layout behavior.
