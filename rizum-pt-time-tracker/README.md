# Rizum Time Tracker

Painter menu plugin for local, activity-based work tracking. Requires PySide6.

Enable `rizum-pt-time-tracker` in Painter's Python plugins menu. Saved projects
are tracked automatically, without a dock or assignment prompt. The **Time Tracker**
menu shows the current work, total, today, current part, and tracking state.

Names before the first dot identify a work; the remaining filename identifies a
part. `Penglai_Wedding.Basecolors.spp` and `Penglai_Wedding.Hair.spp` share the
`Penglai_Wedding` work. `Penglai_Wedding.spp` uses its `Main` part. Explicit trailing
version suffixes such as `_v02` are ignored; other digits and underscores remain.
Matching names across folders share the same work. Save As uses the destination
name immediately, without copying time. Existing file assignments are preserved,
including manual corrections made through **Manage > Change work / part**.

Clicks, keys, wheel input, mouse drags and pen contact count as activity. Passive
pointer movement does not. Only intervals between inputs shorter than the idle
timeout count. Waiting after the final input is excluded. Other applications,
manual pause and inactive Painter windows stop the session. Unsaved projects are
not tracked. Time is an approximation of active editing, not a measure of effort.

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
