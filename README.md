# Rizum PT UI Prettier

Shared PySide6 UI helpers for Rizum Substance 3D Painter plugins.

## What This Is

This folder is meant to become a small component library used by sibling Painter plugins:

- `rizum-pt-to-ps-bridge`
- `rizum-pt-ui-font`

It provides theme tokens, a generated Qt stylesheet, reusable widget factories, and a standalone preview app.

## Preview

Run this from the `rizum-pt-ui-prettier` folder:

```powershell
python preview.py
```

This starts a no-Painter preview with a Painter-like dark Qt baseline plus the Rizum overlay stylesheet. It watches `rizum_ui/*.py` and refreshes the preview automatically when you save changes.

The external preview is intentionally approximate. It is good for fast layout and component iteration, but Painter's real palette, font metrics, embedded dock behavior, and host styles can differ.

To keep the preview open but disable auto-refresh:

```powershell
python preview.py --no-watch
```

To preview the full override stylesheet:

```powershell
python preview.py --full
```

To compare the live preview against browser screenshots at 1x scale:

```powershell
python preview.py --scale-1x
```

Use `--scale-1x` only for external visual debugging. Painter should keep its normal Qt DPI behavior.

You can keep Substance 3D Painter open while this preview runs. The preview is a separate Python process, so iterating on `theme.py`, `stylesheet.py`, or `components.py` does not require Painter or a Painter plugin reload. Changes to `preview.py` itself still require restarting the preview process.

## Painter Preview Dock

This folder is also a standalone Painter plugin. Enable `rizum-pt-ui-prettier` in Painter to open a `UI Prettier` dock that renders the same component examples inside the real host UI.

Use it as the final visual check before wiring the component library into another plugin.

## Current Handoff

Before continuing animation or compact-control work, read `analysis.md`, especially `Handoff Notes For Next Session`. It records the live Painter findings for dropdown arrows, icon sharpness, combo sizing, and collapsible row animation so the next session does not repeat failed approaches.

Click `Export Palette` in the Painter dock to write:

```text
preview-host-palette.json
```

Painter may report a light Qt palette even while the UI is dark, because the real dark look can come from Painter's host stylesheet. The external preview ignores exported light palettes and uses a Painter-like host-control stylesheet instead.

If your normal Python does not have PySide6, run the preview from an environment that does:

```powershell
python -m pip install PySide6
python preview.py
```

Substance Painter includes PySide6 in its plugin runtime, so missing PySide6 in system Python does not mean the Painter plugin path is blocked.

## Sibling Plugin Import

Painter plugin folders use hyphenated names, so sibling plugins should add this folder to `sys.path` before importing the package:

```python
from pathlib import Path
import sys

ui_kit_root = Path(__file__).resolve().parents[1] / "rizum-pt-ui-prettier"
if str(ui_kit_root) not in sys.path:
    sys.path.insert(0, str(ui_kit_root))

from rizum_ui import ActionButton, apply_theme
```

For plugin-owned panels and dialogs, apply the theme to the root widget:

```python
apply_theme(self.widget, mode="overlay")
```

For broad Painter UI experiments, apply it to the QApplication instance from the `rizum-pt-ui-font` plugin. Keep this optional and reversible because it affects more than one plugin.
