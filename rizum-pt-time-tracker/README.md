# Rizum Time Tracker

Painter menu plugin for local, activity-based work tracking. Requires PySide6 and
the sibling `rizum-pt-ui-prettier` library for its settings and history dialogs.

Enable `rizum-pt-time-tracker` in Painter's Python plugins menu. Saved projects
are tracked automatically, without a dock or assignment prompt. The **Time Tracker**
menu shows the current work, total, today, current part, and tracking state.

Names before the first dot identify a work; the remaining filename identifies a
part. `Penglai_Wedding.Basecolors.spp` and `Penglai_Wedding.Hair.spp` share the
`Penglai_Wedding` work. `Penglai_Wedding.spp` uses its `Main` part. Explicit trailing
version suffixes such as `_v02` are ignored; other digits and underscores remain.
Matching names across folders share the same work. Save As uses the destination
name immediately, without copying time. Existing file assignments are preserved,
including manual corrections made through **Settings**. Settings combines the
current file's work/part, idle timeout and optional time addition under one Save /
Cancel boundary. CSV export and the records folder are secondary actions there.

Counting uses positive evidence. Pointer/pen contact, dragging and wheel input in
Painter's `Viewer3D`/`Viewer2D` count directly. Other native UI inputs, including
keyboard shortcuts, need a layer-stack change within 750 ms. Each input can be
confirmed once; autonomous background changes cannot extend time. Native controls
that do not emit this signal may be undercounted. Viewer names are host-specific.

Menus, dialogs, identifiable Python plugin widgets, unknown unconfirmed inputs,
busy periods, switching applications and manual pause break the session. Returning
to work never fills these excluded gaps. Passive mouse movement is ignored. Only
intervals between confirmed inputs shorter than the idle timeout count; the final
idle tail is excluded. Unsaved projects are not tracked. Testing a brush directly
on the canvas is indistinguishable from production painting; pause tracking for
that case. These signals estimate active editing rather than infer user intent.

Records are stored in `%LOCALAPPDATA%/Rizum/TimeTracker/time.sqlite3` using SQLite
WAL transactions, independently of SPP saves. Sessions checkpoint every second;
a crash can lose the latest unflushed second. The menu provides history, CSV
export, manual additions and an adjustable idle timeout. Manual time belongs to
the day it is entered. Back up the database through SQLite's backup API while
Painter is running, or copy the records folder after all Painter instances close.

The plugin never modifies Painter installation files or SPP metadata. Local path
associations are machine-specific. Save As and external copies are grouped by
filename. Changing a file's grouping also moves that
file's historical records; it never moves records belonging to its source file.
