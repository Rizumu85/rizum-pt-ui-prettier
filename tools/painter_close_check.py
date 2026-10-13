"""Check that closed plugins hold nothing of Painter's.

    python tools/painter_close_check.py                  every plugin in python/plugins
    python tools/painter_close_check.py --only a,b       only these plugin folders
    python tools/painter_close_check.py --painter EXE    when Painter is not found

Run it from PowerShell or a normal terminal, before releasing a change that
touches Painter's widgets, signal connections or a plugin's close. It takes
about a minute and a half and exits with 0 (clean), 1 (something is held)
or 2 (the check could not run).

Why it exists. Painter destroys its widgets after it has closed the plugins.
A Python wrapper of one of those widgets that is still alive then crashes
Painter when it unloads the bindings (see docs/integration.md, "Painter's
Widgets And Painter's Exit"). The crash depends on the order of that
teardown: it showed on most exits but not on all, and never in a unit test,
so it shipped twice in October 2026 before a user's crash reports gave it
away. What causes it can be seen every time, though, without waiting for the
crash: after the plugins are closed, something of Painter's is still held.
This check looks for exactly that.

How it works. The script copies itself into Painter's python/startup folder
and starts a second, temporary Painter. In there it creates a project, lets
the plugins work on it for a few seconds, closes all plugins the way Painter
does when it exits, runs a collection and reports what is left:

- a wrapper of Painter's main window that is still alive;
- a module variable or an attribute of a plugin's object that still holds
  one of Painter's widgets or actions;
- the plugin objects that outlived the close (listed, not an error: the
  collector cannot see through Qt, so some always do; they only must not
  hold anything of Painter's).

The temporary Painter is then ended as a process, never closed: closing it
would write its window layout over the user's. The startup copy is removed.
The plugins' registry settings are compared before and after and put back if
the run changed them.
"""

from __future__ import annotations

import json
import os
import sys
import traceback

OUT_VARIABLE = "RIZUM_CLOSE_CHECK_OUT"
ONLY_VARIABLE = "RIZUM_CLOSE_CHECK_ONLY"
PLUGINS_VARIABLE = "RIZUM_CLOSE_CHECK_PLUGINS"
STARTUP_NAME = "_rizum_close_check.py"
RESULT_NAME = "result.json"
# Painter is not ready for a project the moment its plugins start (measured:
# a project created earlier than about 15 s after start never opens).
PROJECT_DELAY_MS = 16000
PROJECT_POLL_MS = 1000
PROJECT_POLLS = 120
# Long enough for the plugins' own timers to look the tool's widgets up.
USE_MS = 5000


# -- inside the temporary Painter --------------------------------------------
_KEEP = {}
_ERRORS = []


def _guarded(function):
    def run():
        try:
            function()
        except Exception:
            _ERRORS.append(traceback.format_exc())
            _write_result({})
    return run


def _later(milliseconds, function):
    from PySide6 import QtCore

    QtCore.QTimer.singleShot(milliseconds, _guarded(function))


def _user_plugins():
    """Names of the started plugins that live in the user's plugins folder."""
    import substance_painter_plugins

    folder = os.path.normcase(os.path.abspath(os.environ[PLUGINS_VARIABLE]))
    names = []
    for name, module in substance_painter_plugins.plugins.items():
        path = os.path.normcase(os.path.abspath(getattr(module, "__file__", "") or ""))
        if path.startswith(folder + os.sep):
            names.append(name)
    return sorted(names)


def _limit_plugins():
    only = os.environ.get(ONLY_VARIABLE)
    if only is None:
        return
    import substance_painter_plugins

    wanted = {name for name in only.split(",") if name}
    folder = os.path.normcase(os.path.abspath(os.environ[PLUGINS_VARIABLE]))
    start = substance_painter_plugins.start_plugin

    def start_wanted(module):
        path = os.path.normcase(os.path.abspath(getattr(module, "__file__", "") or ""))
        if path.startswith(folder + os.sep) and module.__name__ not in wanted:
            return None
        return start(module)

    substance_painter_plugins.start_plugin = start_wanted


if os.environ.get(OUT_VARIABLE) and __name__ != "__main__":
    # At import, which is before Painter starts the plugins.
    _limit_plugins()


def start_plugin():
    if os.environ.get(OUT_VARIABLE):
        _later(PROJECT_DELAY_MS, _open_project)


def close_plugin():
    pass


def _open_project():
    import substance_painter as sp
    from PySide6 import QtCore

    sp.project.create(mesh_file_path=os.path.join(os.environ[OUT_VARIABLE], "plane.obj"))
    polls = {"left": PROJECT_POLLS}
    timer = QtCore.QTimer()
    _KEEP["poll"] = timer

    def poll():
        polls["left"] -= 1
        if sp.project.is_in_edition_state():
            timer.stop()
            _later(1000, _use)
        elif polls["left"] <= 0:
            timer.stop()
            raise RuntimeError("the project did not open")

    timer.timeout.connect(_guarded(poll))
    timer.start(PROJECT_POLL_MS)


def _use():
    import substance_painter as sp

    # A paint layer gives the active tool a color for the plugins to find.
    stack = sp.textureset.get_active_stack()
    layer = sp.layerstack.insert_paint(sp.layerstack.InsertPosition.from_textureset_stack(stack))
    sp.layerstack.set_selected_nodes([layer])
    _later(USE_MS, _close_and_look)


def _close_and_look():
    import collections
    import gc

    import shiboken6
    import substance_painter_plugins
    from PySide6 import QtCore, QtWidgets

    plugins = _user_plugins()
    own = __name__.split(".")[0]
    plugins = [name for name in plugins if name != own]
    substance_painter_plugins.close_all_plugins()
    gc.collect()

    def painters(value):
        return (
            isinstance(value, QtCore.QObject)
            and shiboken6.isValid(value)
            and not shiboken6.createdByPython(value)
            and not isinstance(value, QtCore.QCoreApplication)
        )

    def describe(value):
        return f"{type(value).__name__} {value.metaObject().className()} '{value.objectName()}'"

    def inside(value):
        if isinstance(value, (list, tuple, set, frozenset)):
            return list(value)
        if isinstance(value, dict):
            return list(value.values())
        return [value]

    main_windows = [
        describe(wrapper)
        for wrapper in shiboken6.getAllValidWrappers()
        if isinstance(wrapper, QtWidgets.QMainWindow) and painters(wrapper)
    ]
    held = []
    for name, module in list(sys.modules.items()):
        if name.split(".")[0] not in plugins or module is None:
            continue
        for attribute, value in list(vars(module).items()):
            held.extend(f"{name}.{attribute}: {describe(item)}" for item in inside(value) if painters(item))
    alive = collections.defaultdict(collections.Counter)
    for thing in gc.get_objects():
        kind = type(thing)
        root = (getattr(kind, "__module__", "") or "").split(".")[0]
        if root not in plugins:
            continue
        alive[root][kind.__name__] += 1
        attributes = getattr(thing, "__dict__", None)
        if not isinstance(attributes, dict):
            continue
        for attribute, value in list(attributes.items()):
            held.extend(
                f"{kind.__module__}.{kind.__name__}.{attribute}: {describe(item)}"
                for item in inside(value) if painters(item)
            )
    _write_result({
        "plugins": plugins,
        "main_window": main_windows,
        "held": sorted(set(held)),
        "alive": {name: dict(kinds) for name, kinds in sorted(alive.items())},
    })


def _write_result(result):
    result["errors"] = list(_ERRORS)
    folder = os.environ[OUT_VARIABLE]
    partial = os.path.join(folder, RESULT_NAME + ".part")
    with open(partial, "w", encoding="utf-8") as file:
        json.dump(result, file, indent=2)
    os.replace(partial, os.path.join(folder, RESULT_NAME))


# -- on the user's side --------------------------------------------------------
PLANE = "v 0 0 0\nv 1 0 0\nv 1 1 0\nv 0 1 0\nvt 0 0\nvt 1 0\nvt 1 1\nvt 0 1\nf 1/1 2/2 3/3 4/4\n"
PAINTER_APP_PATH = r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\Adobe Substance 3D Painter.exe"
SETTINGS_PREFIX = "Rizum"


def _find_painter():
    import winreg

    for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        try:
            with winreg.OpenKey(hive, PAINTER_APP_PATH) as key:
                path = winreg.QueryValue(key, None).strip('"')
        except OSError:
            continue
        if os.path.isfile(path):
            return path
    return None


def _settings_keys():
    import winreg

    names = []
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software") as software:
        index = 0
        while True:
            try:
                name = winreg.EnumKey(software, index)
            except OSError:
                break
            if name.startswith(SETTINGS_PREFIX):
                names.append(name)
            index += 1
    return sorted(names)


def _export_settings(folder, tag):
    import subprocess

    exported = {}
    for name in _settings_keys():
        path = os.path.join(folder, f"{tag}_{name}.reg")
        subprocess.run(["reg", "export", rf"HKCU\Software\{name}", path, "/y"], capture_output=True, check=True)
        with open(path, "rb") as file:
            exported[name] = (path, file.read())
    return exported


def _restore_settings(before, after):
    import subprocess

    changed = [name for name in before if name not in after or after[name][1] != before[name][1]]
    for name in changed:
        subprocess.run(["reg", "import", before[name][0]], capture_output=True, check=True)
    return changed


def main(arguments=None):
    import argparse
    import shutil
    import subprocess
    import tempfile
    import time
    from pathlib import Path

    parser = argparse.ArgumentParser(description="Check that closed Painter plugins hold nothing of Painter's.")
    parser.add_argument("--painter", help="path of Adobe Substance 3D Painter.exe")
    parser.add_argument("--only", help="comma separated plugin folders to start; the others stay off")
    parser.add_argument("--timeout", type=int, default=300, help="seconds to wait for the temporary Painter")
    options = parser.parse_args(arguments)

    plugins = Path(__file__).resolve().parents[2]
    startup = plugins.parent / "startup" / STARTUP_NAME
    painter = options.painter or _find_painter()
    if not painter or not os.path.isfile(painter):
        print("Painter was not found; pass --painter with the path of its exe.")
        return 2
    if startup.exists():
        print(f"{startup} exists: another check is running, or one was interrupted. Remove it and run again.")
        return 2

    folder = Path(tempfile.mkdtemp(prefix="rizum-close-check-"))
    (folder / "plane.obj").write_text(PLANE, encoding="utf-8")
    log = Path(os.environ.get("LOCALAPPDATA", "")) / "Adobe" / "Adobe Substance 3D Painter" / "log.txt"
    if log.is_file():
        # Painter keeps one older log; a running Painter's would be lost to this run.
        shutil.copy2(log, folder / "painter_log_before.txt")
    before = _export_settings(str(folder), "before")
    environment = dict(os.environ)
    environment[OUT_VARIABLE] = str(folder)
    environment[PLUGINS_VARIABLE] = str(plugins)
    if options.only is not None:
        environment[ONLY_VARIABLE] = options.only
    shutil.copy2(__file__, startup)
    process = None
    try:
        process = subprocess.Popen([painter], env=environment)
        deadline = time.monotonic() + options.timeout
        result_path = folder / RESULT_NAME
        while time.monotonic() < deadline and not result_path.exists() and process.poll() is None:
            time.sleep(2)
        time.sleep(1)
    finally:
        if process is not None and process.poll() is None:
            process.terminate()
        startup.unlink(missing_ok=True)
    restored = _restore_settings(before, _export_settings(str(folder), "after"))
    if restored:
        print(f"The run changed the settings of {', '.join(restored)}; they were put back.")
    if not result_path.exists():
        print(f"The temporary Painter gave no result within {options.timeout} s (files kept in {folder}).")
        return 2
    result = json.loads(result_path.read_text(encoding="utf-8"))
    if result.get("errors"):
        print("The check failed inside Painter:")
        print("\n".join(result["errors"]))
        return 2

    print(f"Plugins closed: {', '.join(result['plugins']) or 'none'}")
    for name, kinds in result["alive"].items():
        listed = ", ".join(f"{kind} x{count}" if count > 1 else kind for kind, count in sorted(kinds.items()))
        print(f"  still alive of {name}: {listed}")
    problems = [f"Painter's main window is still wrapped: {item}" for item in result["main_window"]]
    problems += [f"still held: {item}" for item in result["held"]]
    if problems:
        print("FAILED: something of Painter's outlived the close. It will crash Painter on some exits.")
        for problem in problems:
            print(f"  {problem}")
        print("See docs/integration.md, \"Painter's Widgets And Painter's Exit\".")
        return 1
    print("OK: nothing of Painter's is held after the close.")
    shutil.rmtree(folder, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
