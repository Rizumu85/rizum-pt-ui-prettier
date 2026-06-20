# Font-Scale Adaptation Standard

> **Required reading for any agent adding or modifying a shared component.**
> Referenced from `AGENTS.md`.

## Why this exists

`rizum-pt-ui-font` can scale the whole Painter UI font at runtime (0.75x–2.0x). When the font grows, every shared compact control must grow with it — button frames, painted icons, internal glyphs, layout spacing — or text clips and proportions break. When the font shrinks again, everything must shrink back, including the floating dock window.

The hard-won lesson: **`setFixedSize` on a widget only scales the outer frame. Painted internals (icons, chevrons, stepper symbols) are sized by closure-captured constants and will NOT follow unless the component exposes a runtime size setter.** Every new component with painted internals must therefore ship a scale API from day one.

## The contract

Every shared compact component that paints its own glyphs or has a fixed pixel size **must** expose a runtime size setter so callers can scale it after creation. The setter names are conventional, not enforced:

| Component kind | Required method | What it scales |
|---|---|---|
| Painted icon button (`_AnimatedIconButton`) | `setPaintedIconSize(px)` | Painted icon size + clear pixmap cache. Named `setPaintedIconSize` (not `setIconSize`) because `QAbstractButton.setIconSize(QSize)` is non-virtual and PySide6 cannot override it from a Python subclass — calling `setIconSize(int)` silently routes to the C++ method and fails. |
| Stepper / multi-button glyph (`_StepperButtons`) | `setButtonSize(px)` | Fixed widget size + internal symbol geometry |
| Single chevron / arrow glyph (`_ChevronDown`) | `setSize(px)` | Fixed widget size + painted point coords |
| Mock checkbox (`_Checkbox`) | `setSize(px)` | Fixed widget size + painted box/checkmark coords |
| Container control with fixed height (`_SpinInput`, `_ComboInput`) | `setCompactHeight(px)` | Own height + margins + label height + delegate to child glyph setters |
| Field row wrapper (`make_field_row`) | (no setter — caller sets `row.setFixedHeight(h)` and calls `control.setCompactHeight(h)`) | Outer row height; caller drives the inner control |
| Footer / dialog button | width via `set_compact_footer_button_width(..., height=h)` | Pass `height=` so width+height set together |

### Rules

1. **No closure-captured sizes for painted geometry.** Store the size on `self` (e.g. `self._icon_size`, `self._button_size`) and read it in `_rendered_pixmap` / `paintEvent` / `_rect_for` / `_draw_symbol`. The closure value only seeds the initial `self._*`.
2. **Invalidate caches on resize.** Pixmap/geometry caches keyed by the old size must be cleared in the setter (`self._pixmap_cache.clear()`).
3. **Scale internal glyph geometry proportionally.** Fixed point coordinates in `paintEvent` must multiply by a ratio derived from the new size vs. the default size (e.g. `s = self._size / 10.0` for a glyph authored at 10px).
4. **Keep a sane floor, unified across all components.** Setters clamp to a minimum so the control never collapses below legibility. **All floors must use `base × 0.75`** (the same ratio as the row-height floor 24/32), so proportions stay consistent even when floors trigger at small scales. Example: a glyph authored at 10px floors at `max(8, …)` (round(10×0.75)=8); a button at 28px floors at `max(21, …)` (round(28×0.75)=21). Mismatched floors (e.g. 22px button flooring at 18 while 32px row floors at 24) break proportions at small scales.
5. **Container controls delegate.** `setCompactHeight` on a container must call the child glyph's size setter (e.g. `_SpinInput.setCompactHeight` calls `self._stepper_buttons.setButtonSize(...)`, `_ComboInput.setCompactHeight` calls `self._arrow.setSize(...)`), scaled by `child_default * new_height / default_height`.

## Caller side — `rizum-pt-ui-font` pattern

The font plugin drives scaling from a single `_apply_compact_heights(scale)` method. New shared components just need their setter called there:

```python
def _apply_compact_heights(self, scale):
    row_h = max(24, int(round(32 * scale)))
    footer_h = max(36, int(round(48 * scale)))

    # Field rows + their inner controls
    for key in ("size", "font"):
        row = self._styled_rows.get(key)
        if row is None:
            continue
        row.setFixedHeight(row_h)
        control = getattr(row, "_rizum_control", None)
        if control is not None and hasattr(control, "setCompactHeight"):
            control.setCompactHeight(row_h)  # delegates to child glyphs

    # Icon buttons: scale frame AND painted icon
    icon_btn_size = max(18, int(round(22 * scale)))
    icon_px = max(10, int(round(16 * scale)))
    for attr in ("browse_btn", "undo_btn", "refresh_btn"):
        btn = getattr(self, attr, None)
        if btn is None:
            continue
        btn.setFixedSize(icon_btn_size, icon_btn_size)
        btn.setPaintedIconSize(icon_px)  # without this, only the frame scales

    # Footer buttons: pass height= so setFixedSize covers both dimensions
    footer_btn_h = max(22, int(round(26 * scale)))
    self.ui.set_compact_footer_button_width(
        self.save_btn, computed_width, height=footer_btn_h,
    )
```

### Widths scale too

Width `maximum` caps that were authored for the default font must also multiply by `scale`, or long localized strings clip at large sizes:

```python
self.ui.compact_text_width(text, widget=w, minimum=m, maximum=int(round(max_px * scale)))
```

### Dock window must resize both directions

When the font changes, clear the minimums, force a layout reflow, re-measure `minimumSizeHint`, then resize the floating dock to that hint — growing **and** shrinking:

```python
self.widget.setMinimumWidth(0)
self.widget.setMinimumHeight(0)
self.widget.updateGeometry()
min_width = max(_MIN_DOCK_WIDTH, self.widget.minimumSizeHint().width())
min_height = max(_DEFAULT_DOCK_HEIGHT, self.widget.minimumSizeHint().height())
self.widget.setMinimumWidth(min_width)
self.widget.setMinimumHeight(min_height)
if _DOCK is not None and _DOCK.isFloating():
    _DOCK.resize(min_width, min_height)   # unconditional — grows & shrinks
```

The previous bug: guarding resize with `if dock.width() < min_width` only ever grew the window; it never shrank back.

## Checklist for new components

- [ ] No painted-geometry size comes from a closure; all read from `self._*`.
- [ ] Exposes the conventional setter (`setPaintedIconSize` / `setButtonSize` / `setSize` / `setCompactHeight`).
- [ ] Setter clamps to a floor and invalidates caches.
- [ ] Internal glyph point coordinates multiply by `new_size / default_size`.
- [ ] Container controls delegate to child glyph setters in their `setCompactHeight`.
- [ ] Default-size behavior is unchanged when `scale == 1.0`.
