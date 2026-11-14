"""Measure what each plugin costs Painter's main thread.

    python tools/painter_perf_check.py                       a plane, every plugin
    python tools/painter_perf_check.py --project FILE.spp    a copy of a real project
    python tools/painter_perf_check.py --only a,b            only these plugin folders start
    python tools/painter_perf_check.py --only ""             no plugin: Painter alone, to compare
    python tools/painter_perf_check.py --seconds 10          per scenario (default 8)
    python tools/painter_perf_check.py --census              count Painter's events instead
    python tools/painter_perf_check.py --scenarios idle,idle some of the scenarios, in this order
    python tools/painter_perf_check.py --painter EXE         when Painter is not found

Run it from PowerShell or a normal terminal, before releasing a plugin or a
change to a timer, an event filter or a search of Painter's widgets. It
exits with 0 (within the budget), 1 (a plugin is over it) or 2 (the check
could not run). The budget and the rules behind it are in
docs/integration.md, "Performance On Painter's Main Thread".

Why it exists. Everything a plugin does runs on the thread that also paints
strokes and turns the camera. A timer that takes 10 ms four times a second,
or a filter that takes half a millisecond for each pen event, is invisible
in a test and in the plugin's own panel, and shows as hitching somewhere
else: the user noticed it as View Roll's rotation stuttering, and the cause
was another plugin's timer (2026-11-13).

How it works. Like painter_close_check.py, the script copies itself into
Painter's python/startup folder and starts a second, temporary Painter. In
there it opens the project, picks the Paint tool on a new paint layer and
plays the scenarios below with input posted to the 3D view's window as
Windows messages. A hook on Python's
monitoring events times every call that Painter's event loop makes into
Python and files it under the plugin whose code was entered; a 8 ms timer
records how late the event loop gets to it.

    idle      nothing moves
    pointer   the pointer crosses the 3D view
    keys      Shift goes down and up, eight times a second
    turn      the camera rolls through the API, as View Roll turns it
    paint     strokes on the model
    tools     Paint and Eraser take turns, one switch a second

What it does not show: time a plugin causes inside Qt without running Python,
such as a style sheet Painter's widgets are polished with. For that, compare
the "event loop" lines of a run with the plugin and a run with --only "".
The hook makes Python slower, so the times are upper bounds.

--census counts the events themselves, by type and by what receives them
(a window, a widget, another object), instead of timing the plugins. An
application event filter is called for every one of them, a filter on a
window or a widget only for its own: the counts say what a filter would
cost where.

What it protects. A project is opened from a copy, so the file, its
autosaves and Painter's list of recent files stay as they were. The
temporary Painter starts the user's plugins with their real settings and
data: the plugins' registry settings and their files under
%LOCALAPPDATA%/Rizum are put back afterwards, unless another Painter ran in
the meantime (then they are left alone and the run says so). The temporary
Painter is ended as a process, never closed, so its layout is not saved.
"""

from __future__ import annotations

import json
import os
import sys
import threading
import time
import traceback

OUT_VARIABLE = "RIZUM_PERF_CHECK_OUT"
ONLY_VARIABLE = "RIZUM_PERF_CHECK_ONLY"
PLUGINS_VARIABLE = "RIZUM_PERF_CHECK_PLUGINS"
PROJECT_VARIABLE = "RIZUM_PERF_CHECK_PROJECT"
SECONDS_VARIABLE = "RIZUM_PERF_CHECK_SECONDS"
CENSUS_VARIABLE = "RIZUM_PERF_CHECK_CENSUS"
SCENARIOS_VARIABLE = "RIZUM_PERF_CHECK_SCENARIOS"
STARTUP_NAME = "_rizum_perf_check.py"
RESULT_NAME = "result.json"
# Painter is not ready for a project the moment its plugins start (measured:
# a project created earlier than about 15 s after start never opens).
PROJECT_DELAY_MS = 16000
PROJECT_POLL_MS = 1000
# A large project computes for a while after it opens; measuring starts
# once Painter has been idle this long.
QUIET_POLLS = 6
SETTLE_POLLS = 180
TICK_MS = 8
SCENARIOS = ("idle", "pointer", "keys", "turn", "paint", "tools")
# What a plugin may take: milliseconds of the main thread per second in each
# scenario, and the longest single call. See docs/integration.md.
BUDGET_MS_PER_SECOND = {"idle": 1.0, "pointer": 2.5, "keys": 6.0, "turn": 2.5, "paint": 4.0, "tools": 10.0}
BUDGET_LONGEST_MS = 8.0
OWN = "(this check)"
PAINTER = "(Painter's own Python)"

# -- inside the temporary Painter --------------------------------------------
_KEEP = {}
_ERRORS = []


def _guarded(function):
    def run(*arguments):
        try:
            function(*arguments)
        except Exception:
            _ERRORS.append(traceback.format_exc())
            _write_result({})
    return run


def _later(milliseconds, function):
    from PySide6 import QtCore

    QtCore.QTimer.singleShot(milliseconds, _guarded(function))


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


class _Meter:
    """Times each call Painter's event loop makes into Python, by plugin."""

    def __init__(self, plugins_folder):
        self._folder = os.path.normcase(os.path.abspath(plugins_folder)) + os.sep
        self._own = os.path.normcase(os.path.abspath(__file__))
        self._owners = {}
        self._entered = None
        # Monitoring reports every thread. A worker thread's function has no
        # caller either and may run for the whole session; taken for a call
        # from the event loop, it would hide everything after it.
        self._thread = threading.get_ident()
        self.totals = {}
        self.entries = {}

    def install(self):
        monitoring = sys.monitoring
        self._tool = monitoring.PROFILER_ID
        monitoring.use_tool_id(self._tool, "rizum_perf_check")
        events = monitoring.events
        monitoring.register_callback(self._tool, events.PY_START, self._started)
        monitoring.register_callback(self._tool, events.PY_RETURN, self._left)
        monitoring.register_callback(self._tool, events.PY_UNWIND, self._left)
        monitoring.set_events(self._tool, events.PY_START | events.PY_RETURN | events.PY_UNWIND)

    def remove(self):
        sys.monitoring.set_events(self._tool, 0)
        sys.monitoring.free_tool_id(self._tool)

    def reset(self):
        self.totals = {}
        self.entries = {}

    def _owner(self, code):
        # By file, not by code object: two plugins' copies of the same kit
        # function are equal code objects, and the first plugin seen would
        # be charged for both.
        owner = self._owners.get(code.co_filename)
        if owner is None:
            path = os.path.normcase(code.co_filename)
            if path == self._own:
                owner = OWN
            elif path.startswith(self._folder):
                owner = path[len(self._folder):].split(os.sep)[0]
                owner = owner[:-3] if owner.endswith(".py") else owner
            else:
                owner = PAINTER
            self._owners[code.co_filename] = owner
        return owner

    def _started(self, code, _offset):
        # A frame without a caller was entered from the event loop.
        if self._entered is None and sys._getframe(1).f_back is None and threading.get_ident() == self._thread:
            self._entered = (code, time.perf_counter())

    def _left(self, code, _offset, _value):
        entered = self._entered
        if (
            entered is None or entered[0] is not code or sys._getframe(1).f_back is not None
            or threading.get_ident() != self._thread
        ):
            return
        self._entered = None
        elapsed = time.perf_counter() - entered[1]
        owner = self._owner(code)
        if owner == OWN:
            return
        total = self.totals.setdefault(owner, [0.0, 0, 0.0, 0])
        total[0] += elapsed
        total[1] += 1
        total[2] = max(total[2], elapsed)
        total[3] += elapsed > BUDGET_LONGEST_MS / 1000.0
        name = f"{os.path.basename(code.co_filename)}:{code.co_qualname}"
        entry = self.entries.setdefault((owner, name), [0.0, 0, 0.0])
        entry[0] += elapsed
        entry[1] += 1
        entry[2] = max(entry[2], elapsed)


def _make_census():
    from PySide6 import QtCore, QtGui

    class Census(QtCore.QObject):
        """Counts every event of the application by type and receiver."""

        def __init__(self):
            super().__init__()
            self.counts = {}

        def eventFilter(self, receiver, event):
            if isinstance(receiver, QtGui.QWindow):
                kind = "window"
            elif receiver.isWidgetType():
                kind = "widget"
            else:
                kind = "object"
            key = (event.type(), kind)
            self.counts[key] = self.counts.get(key, 0) + 1
            return False

        def snapshot(self):
            rows = [
                [getattr(kind, "name", str(kind)), receiver, count]
                for (kind, receiver), count in sorted(self.counts.items(), key=lambda item: -item[1])
            ]
            self.counts = {}
            return rows

    return Census()


def _open_project():
    import substance_painter as sp
    from PySide6 import QtCore

    project = os.environ.get(PROJECT_VARIABLE)
    if project:
        sp.project.open(project)
    else:
        sp.project.create(mesh_file_path=os.path.join(os.environ[OUT_VARIABLE], "plane.obj"))
    state = {"polls": 0, "quiet": 0, "settling": 0}
    timer = QtCore.QTimer()
    _KEEP["poll"] = timer
    limit = int(os.environ.get("RIZUM_PERF_CHECK_LOAD_SECONDS", "900"))

    def poll():
        state["polls"] += 1
        if not sp.project.is_in_edition_state():
            if state["polls"] > limit:
                timer.stop()
                raise RuntimeError("the project did not open; visible windows: " + ", ".join(_visible_windows()))
            return
        state["settling"] += 1
        state["quiet"] = 0 if sp.project.is_busy() else state["quiet"] + 1
        if state["quiet"] >= QUIET_POLLS or state["settling"] >= SETTLE_POLLS:
            timer.stop()
            _later(500, _prepare)

    timer.timeout.connect(_guarded(poll))
    timer.start(PROJECT_POLL_MS)


def _visible_windows():
    from PySide6 import QtWidgets

    return [
        f"{widget.metaObject().className()} '{widget.windowTitle()}'"
        for widget in QtWidgets.QApplication.topLevelWidgets()
        if widget.isVisible()
    ]


def _prepare():
    import substance_painter as sp
    from PySide6 import QtWidgets

    main = sp.ui.get_main_window()
    _KEEP["main"] = main
    # The user's layout is made for their screen; a small window leaves the
    # 3D view a few pixels high.
    main.showMaximized()
    stack = sp.textureset.get_active_stack()
    layer = sp.layerstack.insert_paint(sp.layerstack.InsertPosition.from_textureset_stack(stack))
    sp.layerstack.set_selected_nodes([layer])
    button = main.findChild(QtWidgets.QToolButton, "Paint")
    action = button.defaultAction() if button is not None else None
    if action is not None:
        # Not click(): the button opens its menu and waits in it.
        action.trigger()
    # Showing a tool's Properties for the first time sets off a burst of
    # widget events that lasts some ten seconds; the scenarios start after it.
    _later(15000, _measure)


def _measure():
    import ctypes
    import math

    import substance_painter as sp
    import substance_painter_plugins
    from PySide6 import QtCore, QtWidgets

    main = _KEEP["main"]
    viewer = main.findChild(QtWidgets.QWidget, "Viewer3D")
    if viewer is None:
        raise RuntimeError("Painter's 3D view (Viewer3D) was not found")
    seconds = float(os.environ.get(SECONDS_VARIABLE, "8"))
    scenarios = [name for name in os.environ.get(SCENARIOS_VARIABLE, "").split(",") if name in SCENARIOS] or list(SCENARIOS)
    meter = _Meter(os.environ[PLUGINS_VARIABLE])
    census = _make_census() if os.environ.get(CENSUS_VARIABLE) else None
    if census is None:
        meter.install()
    else:
        QtWidgets.QApplication.instance().installEventFilter(census)
    folder = os.path.normcase(os.path.abspath(os.environ[PLUGINS_VARIABLE])) + os.sep
    started = sorted(
        name for name, module in substance_painter_plugins.plugins.items()
        if os.path.normcase(os.path.abspath(getattr(module, "__file__", "") or "")).startswith(folder)
        and substance_painter_plugins.is_plugin_started(module) and name != __name__.split(".")[0]
    )
    camera = sp.display.Camera.get_default_camera()
    rotation = list(camera.rotation)
    result = {
        "plugins": started,
        "painter": sp.application.version(),
        "python": sys.version.split()[0],
        "project": os.path.basename(os.environ.get(PROJECT_VARIABLE) or "plane.obj"),
        "texture_sets": len(sp.textureset.all_texture_sets()),
        "view": [viewer.width(), viewer.height()],
        "scale": main.devicePixelRatioF(),
        "seconds": seconds,
        "scenarios": [],
    }
    # Input goes to the 3D view's own window as Windows messages, so it
    # arrives as real input does. Events made in Python and handed to Qt do
    # not reach Painter's viewport: a stroke of them paints nothing.
    tools = [
        button.defaultAction()
        for button in (main.findChild(QtWidgets.QToolButton, name) for name in ("Eraser", "Paint"))
        if button is not None and button.defaultAction() is not None
    ]
    user32 = ctypes.windll.user32
    window = int(viewer.winId())
    scale = viewer.devicePixelRatioF()
    width, height = viewer.width() * scale, viewer.height() * scale
    mouse_move, left_down, left_up, key_down, key_up = 0x0200, 0x0201, 0x0202, 0x0100, 0x0101
    left_held, shift_key = 0x0001, 0x10
    state = {"index": 0, "ticks": 0, "events": 0, "last": 0.0, "start": 0.0, "gaps": [], "down": False, "strokes": 0}

    def post(message, wparam, lparam):
        user32.PostMessageW(window, message, wparam, lparam)
        state["events"] += 1

    def place(tick):
        """A point that wanders around the middle of the view, as the lParam of a mouse message."""
        angle = tick * 0.05
        x = width / 2 + math.cos(angle) * width * 0.2
        y = height / 2 + math.sin(angle * 1.7) * height * 0.2
        return (int(y) << 16) | (int(x) & 0xFFFF)

    def history_rows():
        dock = main.findChild(QtWidgets.QDockWidget, "history")
        views = dock.findChildren(QtWidgets.QAbstractItemView) if dock is not None else []
        return sum(view.model().rowCount() for view in views if view.model() is not None)

    def lift():
        if state["down"]:
            post(left_up, 0, place(state["ticks"]))
            state["down"] = False

    def play(name, elapsed):
        tick = state["ticks"]
        if name == "pointer":
            post(mouse_move, 0, place(tick))
        elif name == "keys":
            # Eight presses a second, as fast typing is.
            if tick % 16 == 0:
                post(key_down, shift_key, 0x002A0001)
            elif tick % 16 == 8:
                post(key_up, shift_key, 0xC02A0001)
        elif name == "turn":
            # Through the API, as View Roll turns the view: Painter redraws
            # the model for every step.
            turned = list(camera.rotation)
            turned[2] = (turned[2] + 180.0 * elapsed + 180.0) % 360.0 - 180.0
            camera.rotation = turned
        elif name == "tools":
            if tick % 125 == 0 and tools:
                tools[(tick // 125) % len(tools)].trigger()
        elif name == "paint":
            # A stroke of about a second, then the pen lifts.
            if tick % 125 == 0:
                lift()
            if state["down"]:
                post(mouse_move, left_held, place(tick))
            else:
                post(mouse_move, 0, place(tick))
                post(left_down, left_held, place(tick))
                state["down"] = True

    def finish(name):
        lift()
        if name == "turn":
            camera.rotation = rotation
        if name == "tools" and tools:
            tools[-1].trigger()
        elapsed = time.perf_counter() - state["start"]
        gaps = sorted(state["gaps"])
        played = {
            "name": name,
            "seconds": elapsed,
            "ticks": state["ticks"],
            "events": state["events"],
            "interval_median_ms": gaps[len(gaps) // 2] * 1000 if gaps else 0.0,
            "interval_p95_ms": gaps[int(len(gaps) * 0.95)] * 1000 if gaps else 0.0,
            "interval_max_ms": gaps[-1] * 1000 if gaps else 0.0,
            "late_33ms": sum(gap > 0.033 for gap in gaps),
            "late_100ms": sum(gap > 0.100 for gap in gaps),
            "plugins": {
                owner: {"ms": total[0] * 1000, "calls": total[1], "longest_ms": total[2] * 1000, "over": total[3]}
                for owner, total in meter.totals.items()
            },
            "entries": [
                {"plugin": owner, "call": call, "ms": entry[0] * 1000, "calls": entry[1], "longest_ms": entry[2] * 1000}
                for (owner, call), entry in sorted(meter.entries.items(), key=lambda item: -item[1][0])[:12]
            ],
        }
        if census is not None:
            played["census"] = census.snapshot()
        result["scenarios"].append(played)

    def begin():
        meter.reset()
        if census is not None:
            census.snapshot()
        now = time.perf_counter()
        state.update(ticks=0, events=0, last=now, start=now, gaps=[], down=False)
        if scenarios[state["index"]] == "paint":
            state["strokes"] = history_rows()
            state["painted"] = True

    timer = QtCore.QTimer()
    timer.setInterval(TICK_MS)
    timer.setTimerType(QtCore.Qt.TimerType.PreciseTimer)
    _KEEP["ticker"] = timer

    def done():
        # Painter lists a stroke in its History once it is finished.
        result["strokes"] = history_rows() - state["strokes"] if state.get("painted") else None
        if census is None:
            meter.remove()
        else:
            QtWidgets.QApplication.instance().removeEventFilter(census)
        _write_result(result)

    def tick():
        now = time.perf_counter()
        name = scenarios[state["index"]]
        elapsed = now - state["last"]
        state["gaps"].append(elapsed)
        state["last"] = now
        play(name, elapsed)
        state["ticks"] += 1
        if now - state["start"] < seconds:
            return
        finish(name)
        state["index"] += 1
        if state["index"] < len(scenarios):
            begin()
            return
        timer.stop()
        _later(1500, done)

    timer.timeout.connect(_guarded(tick))
    begin()
    timer.start()


def _write_result(result):
    result["errors"] = list(_ERRORS)
    folder = os.environ[OUT_VARIABLE]
    partial = os.path.join(folder, RESULT_NAME + ".part")
    with open(partial, "w", encoding="utf-8") as file:
        json.dump(result, file, indent=2)
    os.replace(partial, os.path.join(folder, RESULT_NAME))


# -- on the user's side --------------------------------------------------------
PLANE = "v 0 0 0\nv 1 0 0\nv 1 1 0\nv 0 1 0\nvt 0 0\nvt 1 0\nvt 1 1\nvt 0 1\nf 1/1 2/2 3/3 4/4\n"
PAINTER_PROCESS = "Adobe Substance 3D Painter.exe"
RECENT_PROJECTS_KEY = r"HKCU\Software\Adobe\Adobe Substance 3D Painter\project_management"
# Where the plugins keep files of their own, under %LOCALAPPDATA%/Rizum. A
# plugin that starts keeping files there adds its folder; other programs
# share that root and must not be put back.
PLUGIN_DATA_FOLDERS = ("BrushMemory", "TimeTracker", "Updater")


def _painter_processes():
    import subprocess

    listed = subprocess.run(
        ["tasklist", "/FI", f"IMAGENAME eq {PAINTER_PROCESS}", "/FO", "CSV", "/NH"], capture_output=True, text=True
    ).stdout
    return {int(line.split('","')[1]) for line in listed.splitlines() if line.startswith('"') and '","' in line}


def _snapshot(folder):
    """Every file under ``folder``, read into memory (the plugins' data is small)."""
    from pathlib import Path

    return {
        path: path.read_bytes()
        for name in PLUGIN_DATA_FOLDERS
        for path in (Path(folder) / name).rglob("*")
        if path.is_file()
    }


def _put_back(before, folder):
    from pathlib import Path

    changed = []
    after = {
        path for name in PLUGIN_DATA_FOLDERS for path in (Path(folder) / name).rglob("*") if path.is_file()
    }
    for path in after - set(before):
        path.unlink()
        changed.append(path.name)
    for path, data in before.items():
        if not path.exists() or path.read_bytes() != data:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            changed.append(path.name)
    return sorted(changed)


def _report(result):
    over = []
    print(f"Painter {result['painter']}, Python {result['python']}, project {result['project']} "
          f"({result['texture_sets']} texture sets), 3D view {result['view'][0]}x{result['view'][1]} at scale {result['scale']}")
    print(f"Plugins started: {', '.join(result['plugins']) or 'none'}")
    if result.get("strokes") == 0:
        print("Note: Painter's History lists no stroke from the paint scenario; its strokes did not reach Painter.")
    for scenario in result["scenarios"]:
        name = scenario["name"]
        seconds = scenario["seconds"]
        print(f"\n{name}: {seconds:.1f} s, {scenario['events']} events")
        print(f"  event loop: every {scenario['interval_median_ms']:.1f} ms (median), p95 {scenario['interval_p95_ms']:.1f}, "
              f"longest {scenario['interval_max_ms']:.0f}; over 33 ms: {scenario['late_33ms']}, over 100 ms: {scenario['late_100ms']}")
        census = scenario.get("census")
        if census is not None:
            total = sum(row[2] for row in census)
            by_receiver = {}
            for _kind, receiver, count in census:
                by_receiver[receiver] = by_receiver.get(receiver, 0) + count
            shares = ", ".join(f"{count / seconds:.0f} to a {receiver}" for receiver, count in sorted(by_receiver.items(), key=lambda item: -item[1]))
            print(f"  events: {total / seconds:.0f} per s ({shares})")
            for kind, receiver, count in census[:10]:
                print(f"      {kind} to a {receiver}: {count / seconds:.0f} per s")
            continue
        rows = sorted(scenario["plugins"].items(), key=lambda item: -item[1]["ms"])
        if rows:
            print(f"  {'plugin':<28}{'ms per s':>10}{'calls per s':>13}{'longest ms':>12}{'over ' + str(BUDGET_LONGEST_MS) + ' ms':>12}")
        for plugin, row in rows:
            per_second = row["ms"] / seconds
            flag = ""
            if plugin != PAINTER and (per_second > BUDGET_MS_PER_SECOND[name] or row["longest_ms"] > BUDGET_LONGEST_MS):
                flag = "  <- over budget"
                over.append(f"{plugin} in {name}: {per_second:.2f} ms per s, longest {row['longest_ms']:.1f} ms")
            print(f"  {plugin:<28}{per_second:>10.2f}{row['calls'] / seconds:>13.1f}{row['longest_ms']:>12.2f}{row['over']:>12}{flag}")
        for entry in scenario["entries"][:5]:
            if entry["plugin"] != PAINTER:
                print(f"      {entry['plugin']} {entry['call']}: {entry['ms'] / seconds:.2f} ms per s, "
                      f"{entry['calls'] / seconds:.1f} calls per s, longest {entry['longest_ms']:.2f} ms")
    return over


def main(arguments=None):
    import argparse
    import shutil
    import subprocess
    import tempfile
    from pathlib import Path

    import painter_close_check as close_check

    parser = argparse.ArgumentParser(description="Measure what each Painter plugin costs the main thread.")
    parser.add_argument("--painter", help="path of Adobe Substance 3D Painter.exe")
    parser.add_argument("--project", help="a .spp to measure on; it is opened from a copy")
    parser.add_argument("--only", help="comma separated plugin folders to start; the others stay off")
    parser.add_argument("--seconds", type=float, default=8.0, help="how long each scenario plays")
    parser.add_argument("--timeout", type=int, default=1500, help="seconds to wait for the temporary Painter")
    parser.add_argument("--census", action="store_true", help="count Painter's events instead of timing the plugins")
    parser.add_argument("--scenarios", help=f"comma separated, from {', '.join(SCENARIOS)}; a name may repeat")
    parser.add_argument("--json", help="also write the raw result to this file")
    options = parser.parse_args(arguments)

    plugins = Path(__file__).resolve().parents[2]
    startup = plugins.parent / "startup" / STARTUP_NAME
    painter = options.painter or close_check._find_painter()
    if not painter or not os.path.isfile(painter):
        print("Painter was not found; pass --painter with the path of its exe.")
        return 2
    if startup.exists():
        print(f"{startup} exists: another check is running, or one was interrupted. Remove it and run again.")
        return 2
    if options.project and not os.path.isfile(options.project):
        print(f"{options.project} is not a file.")
        return 2

    folder = Path(tempfile.mkdtemp(prefix="rizum-perf-check-"))
    (folder / "plane.obj").write_text(PLANE, encoding="utf-8")
    environment = dict(os.environ)
    environment[OUT_VARIABLE] = str(folder)
    environment[PLUGINS_VARIABLE] = str(plugins)
    environment[SECONDS_VARIABLE] = str(options.seconds)
    if options.only is not None:
        environment[ONLY_VARIABLE] = options.only
    if options.census:
        environment[CENSUS_VARIABLE] = "1"
    if options.scenarios:
        environment[SCENARIOS_VARIABLE] = options.scenarios
    if options.project:
        copy = folder / Path(options.project).name
        shutil.copy2(options.project, copy)
        environment[PROJECT_VARIABLE] = str(copy)
    data = Path(os.environ.get("LOCALAPPDATA", "")) / "Rizum"
    files_before = _snapshot(data)
    settings_before = close_check._export_settings(str(folder), "before")
    recent = folder / "recent_projects.reg"
    subprocess.run(["reg", "export", RECENT_PROJECTS_KEY, str(recent), "/y"], capture_output=True)
    others_before = _painter_processes()
    other_painter = bool(others_before)
    shutil.copy2(__file__, startup)
    process = None
    result_path = folder / RESULT_NAME
    try:
        process = subprocess.Popen([painter], env=environment)
        deadline = time.monotonic() + options.timeout
        while time.monotonic() < deadline and not result_path.exists() and process.poll() is None:
            time.sleep(3)
            other_painter = other_painter or bool(_painter_processes() - {process.pid})
        time.sleep(1)
    finally:
        if process is not None and process.poll() is None:
            process.terminate()
            process.wait(30)
        startup.unlink(missing_ok=True)
    if recent.is_file():
        subprocess.run(["reg", "import", str(recent)], capture_output=True)
    if other_painter:
        print("Another Painter ran during the check: the plugins' settings and data were left as they are.")
    else:
        restored = close_check._restore_settings(settings_before, close_check._export_settings(str(folder), "after"))
        restored += _put_back(files_before, data)
        if restored:
            print(f"Put back after the run: {', '.join(restored)}")
    if not result_path.exists():
        print(f"The temporary Painter gave no result within {options.timeout} s (files kept in {folder}).")
        return 2
    result = json.loads(result_path.read_text(encoding="utf-8"))
    if options.json:
        Path(options.json).write_text(json.dumps(result, indent=1), encoding="utf-8")
    if result.get("errors"):
        print("The check failed inside Painter:")
        print("\n".join(result["errors"]))
        return 2
    over = _report(result)
    shutil.rmtree(folder, ignore_errors=True)
    if over:
        print("\nOVER BUDGET (docs/integration.md, \"Performance On Painter's Main Thread\"):")
        for line in over:
            print(f"  {line}")
        return 1
    print("\nOK: every plugin is within the budget.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
