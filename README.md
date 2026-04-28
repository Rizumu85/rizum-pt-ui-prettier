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
apply_theme(self.widget)
```

For broad Painter UI experiments, apply it to the QApplication instance from the `rizum-pt-ui-font` plugin. Keep this optional and reversible because it affects more than one plugin.
