# Painter Plugin Integration

## Safe Boundary

Do not patch Substance 3D Painter installation files. Use the UI kit in one of two scopes:

1. Plugin scope: call `apply_theme(self.widget, mode="overlay")` on a plugin panel or dialog.
2. App scope: call `apply_theme(QApplication.instance(), mode="overlay")` from an explicit appearance/font helper plugin.

Plugin scope is the default. App scope is useful for experiments, but it can affect Painter-owned widgets and other plugins.

## `rizum-pt-to-ps-bridge`

Add this near the top of the UI module before constructing widgets:

```python
from pathlib import Path
import sys

ui_kit_root = Path(__file__).resolve().parents[3] / "rizum-pt-ui-prettier"
if str(ui_kit_root) not in sys.path:
    sys.path.insert(0, str(ui_kit_root))

from rizum_ui import ActionButton, SectionHeader, apply_theme
```

Then apply the theme once after creating the dock root widget:

```python
self.widget = QtWidgets.QWidget()
self.widget.setObjectName("RizumPtToPsSmokeTestPanel")
apply_theme(self.widget, mode="overlay")
```

Use components gradually. For example:

```python
self.dock_export_button = ActionButton.create("Export", "primary")
```

## `rizum-pt-ui-font`

Use app scope only for an explicit appearance experiment:

```python
from pathlib import Path
import sys

ui_kit_root = Path(__file__).resolve().parents[1] / "rizum-pt-ui-prettier"
if str(ui_kit_root) not in sys.path:
    sys.path.insert(0, str(ui_kit_root))

from rizum_ui import apply_theme

app = QtWidgets.QApplication.instance()
if app is not None:
    apply_theme(app, mode="overlay")
```

Keep the existing reset path so font and style experiments can be backed out during the Painter session.
