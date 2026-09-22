# Rizum Time Tracker

Painter dock plugin for local, activity-based work tracking. Requires PySide6
and the sibling `rizum-pt-ui-prettier` UI library.

Enable `rizum-pt-time-tracker` in Painter's Python plugins menu. Save the project
and assign it to a work and part once. Unknown files stay untracked until assigned.
Save As keeps the work and part; choose **New part** in the grouping dialog when
splitting another body part. Existing time is never copied. Opening an unrelated
file requires its own explicit assignment. Renamed/moved files can be assigned to
the same work and part; historical records retain the original path.

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
associations are machine-specific. Save As inherits only during an open project;
external copies are linked explicitly. Changing a file's grouping also moves that
file's historical records; it never moves records belonging to its source file.
