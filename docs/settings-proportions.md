# Settings Proportions

## Preference

The approved references are the live PT-PS Bridge settings and Drag Distance
settings. Their shared principle is **content-fitted geometry with stable visual
density**, not a universal window aspect ratio. A one-setting dialog is short and
wide; a multi-section dialog is narrow and taller. Height follows actual rows and
sections. Do not manufacture blank space to reach a target silhouette.

## Measured References

All values are logical design pixels at UI Scale 1.0, excluding native title bars.
OS/DPI scaling is separate from the plugin UI Scale.

| Property | Drag Distance | PT-PS Bridge |
| --- | --- | --- |
| Width | 250 | At least 338; grows for measured content |
| Height | 96 (one value row and footer) | Measured content plus visible dependent rows |
| Horizontal inset | 16 | 20 |
| Value/control height | 32 | 30; stepper 32 |
| Setting row | 32 | 40; detail rows 46 |
| First/later section height | No sections | 26 / 36 |
| Body top inset | 12 | 12 |
| Footer button height | 28 | 28 |

These are two layout families, not competing standards. Do not force a compact
single-setting dialog to use the height, section headers or divider of a larger
settings form. Data/history windows may be wider and resizable; they are not the
settings-form width reference.

## Typography and Density

Use the host font family and shared Painter settings roles: section 10px/700,
item name 13px/500, metadata/unit 11px/500, button 12px. Keep letter spacing zero.
Use `RizumSettingsSection`, `RizumSettingsItemName`, and `RizumSettingsItemMeta`
instead of assigning one generic font size to every label. Shared controls own
their value-text metrics. A neutral background alone does not establish parity.

At the Bridge baseline, a 13px label sits in a 40px row; a 30px control leaves
roughly 5px above and below. Retain these relationships when scaling. Stronger
separation belongs between semantic groups, not between every field. Use the
26px first-section token instead of giving it the later-section 36px gap.

## Implementation Contract

- Use `PainterSettingsDialog`, `PAINTER_SETTINGS_LAYOUT`, and existing compact
  control APIs. Scale width, insets, rows, fonts, glyphs and buttons together.
- Start grouped settings around the Bridge 338px width. Grow only for measured
  label/control/footer requirements. Never shrink type to preserve a width.
- Use fixed scaled row/section heights for compact forms, with explicit growth
  for wrapping or localization. Minimum heights alone allow Qt to distribute
  spare height across rows and change the intended rhythm.
- Fit height to content; do not add vertical stretch inside the form. Hidden
  fields remove their space. Recompute after reveal, hide, localization and scale
  changes, shrinking as well as growing.
- Controls align to a common right edge; labels share a left edge. A numeric
  stepper keeps its intrinsic width. Avoid stretching it to fill a field column.
- Footer spacing follows the chosen layout family. Do not insert a divider or
  large empty footer zone merely because another, longer form has one.
- Compare at the same UI Scale, font family, DPI and content state. Check 0.75,
  1.0, 1.1 and 2.0, including a shrink back to 1.0 and expanded dependent fields.

The intended effect is compact but legible: content determines the window,
shared typography determines hierarchy, and consistent spacing determines density.
