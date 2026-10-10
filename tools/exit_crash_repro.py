"""Reproduce the exit crash that ``rizum_ui/exit_guard.py`` prevents.

    python tools/exit_crash_repro.py none     no Python event filter: exits cleanly
    python tools/exit_crash_repro.py filter   Python application filter: crashes at exit
    python tools/exit_crash_repro.py guard    the same filter plus the guard: exits cleanly

Each run takes about 35 seconds, the time Qt's pixmap cache needs to fire its
timer once. The exit code tells the result (0 is clean).

Painter loads Qt long before Python's bindings and ends through the C
runtime with Python still initialized, so at exit the bindings are unloaded
before Qt's statics are destroyed. The script sets up the same order.
"""

from __future__ import annotations

import ctypes
import importlib.util
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

_qt_dir = os.path.dirname(importlib.util.find_spec("PySide6").origin)
os.add_dll_directory(_qt_dir)
for _name in ("Qt6Core.dll", "Qt6Gui.dll", "Qt6Widgets.dll"):
    ctypes.CDLL(os.path.join(_qt_dir, _name))

from PySide6 import QtCore, QtGui, QtWidgets  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


class _Filter(QtCore.QObject):
    def eventFilter(self, watched, event):
        return False


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "filter"
    app = QtWidgets.QApplication([])
    if mode != "none":
        watcher = _Filter(app)
        app.installEventFilter(watcher)
    if mode == "guard":
        from rizum_ui import exit_guard

        exit_guard.install()
    pixmap = QtGui.QPixmap(8, 8)
    QtGui.QPixmapCache.insert("exit-crash-repro", pixmap)
    QtCore.QTimer.singleShot(33000, app.quit)
    app.exec()
    print(f"{mode}: leaving through the C runtime", flush=True)
    ctypes.CDLL("ucrtbase").exit(0)


if __name__ == "__main__":
    main()
