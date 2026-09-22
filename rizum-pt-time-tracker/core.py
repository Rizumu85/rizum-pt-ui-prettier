"""Local work ledger. File copies never copy recorded time."""
from __future__ import annotations

import os
import sqlite3
import time
from pathlib import Path
from uuid import uuid4


def key(path):
    return os.path.normcase(os.path.abspath(path))


class Ledger:
    def __init__(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(path), timeout=2)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS works(id TEXT PRIMARY KEY, name TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS parts(
                id TEXT PRIMARY KEY, work TEXT NOT NULL REFERENCES works(id), name TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS files(
                path TEXT PRIMARY KEY, part TEXT NOT NULL REFERENCES parts(id));
            CREATE TABLE IF NOT EXISTS sessions(
                id TEXT PRIMARY KEY, file TEXT NOT NULL REFERENCES files(path),
                start REAL NOT NULL, end REAL NOT NULL, seconds REAL NOT NULL DEFAULT 0,
                manual INTEGER NOT NULL DEFAULT 0);
            CREATE INDEX IF NOT EXISTS sessions_file ON sessions(file);
        """)

    def binding(self, path):
        return self.db.execute("""SELECT f.path, p.id AS part, p.name AS part_name,
            w.id AS work, w.name AS work_name FROM files f JOIN parts p ON f.part=p.id
            JOIN works w ON p.work=w.id WHERE f.path=?""", (key(path),)).fetchone()

    def works(self):
        return self.db.execute("SELECT * FROM works ORDER BY name COLLATE NOCASE").fetchall()

    def parts(self, work):
        return self.db.execute("SELECT * FROM parts WHERE work=? ORDER BY name", (work,)).fetchall()

    def bind(self, path, work_name, part_name, work_id=None, part_id=None):
        path = key(path)
        with self.db:
            if work_id is None:
                work_id = uuid4().hex
                self.db.execute("INSERT INTO works VALUES(?,?)", (work_id, work_name.strip()))
            if part_id is None:
                part_id = uuid4().hex
                self.db.execute("INSERT INTO parts VALUES(?,?,?)", (part_id, work_id, part_name.strip()))
            elif not self.db.execute("SELECT 1 FROM parts WHERE id=? AND work=?", (part_id, work_id)).fetchone():
                raise ValueError("Part does not belong to this work")
            self.db.execute("INSERT INTO files VALUES(?,?) ON CONFLICT(path) DO UPDATE SET part=excluded.part",
                            (path, part_id))
        return self.binding(path)

    def inherit(self, path, source):
        old = self.binding(source)
        if not self.binding(path) and old:
            self.bind(path, old['work_name'], old['part_name'], old['work'], old['part'])
        return self.binding(path)

    def save_session(self, ident, path, start, end, seconds, manual=False):
        with self.db:
            self.db.execute("""INSERT INTO sessions VALUES(?,?,?,?,?,?)
                ON CONFLICT(id) DO UPDATE SET end=excluded.end, seconds=excluded.seconds""",
                (ident, key(path), start, end, seconds, int(manual)))

    def summary(self, work, since=0):
        # Clip at local midnight instead of charging an entire overnight session to today.
        return self.db.execute("""SELECT p.name, p.id,
            COALESCE(SUM(s.seconds),0) AS total,
            COALESCE(SUM(CASE WHEN s.end<=? THEN 0 WHEN s.start>=? OR s.manual=1 THEN s.seconds
              ELSE s.seconds * (s.end-?) / MAX(s.end-s.start, 0.001) END),0) AS today
            FROM parts p LEFT JOIN files f ON f.part=p.id
            LEFT JOIN sessions s ON s.file=f.path WHERE p.work=? GROUP BY p.id ORDER BY p.name""",
            (since, since, since, work)).fetchall()

    def history(self, work):
        return self.db.execute("""SELECT s.*, p.name AS part_name FROM sessions s
            JOIN files f ON f.path=s.file JOIN parts p ON p.id=f.part
            WHERE p.work=? ORDER BY s.start DESC""", (work,)).fetchall()

    def close(self):
        self.db.close()


class ActivityClock:
    """Count intervals between real inputs, excluding an entire idle tail."""
    def __init__(self, ledger, idle=120):
        self.ledger, self.idle = ledger, idle
        self.path = None
        self.session = None
        self.last = None
        self.seconds = 0.0
        self.dirty = False

    def switch(self, path):
        self.stop()
        self.path = key(path) if path else None

    def input(self, mono=None, wall=None):
        if not self.path:
            return
        mono = time.monotonic() if mono is None else mono
        wall = time.time() if wall is None else wall
        gap = mono - self.last if self.last is not None else None
        if gap is None or gap < 0 or gap >= self.idle:
            self.stop()
            self.session, self.start, self.seconds = uuid4().hex, wall, 0.0
        else:
            self.seconds += gap
        self.last, self.end, self.dirty = mono, wall, True

    def flush(self):
        if self.dirty and self.session:
            self.ledger.save_session(self.session, self.path, self.start, self.end, self.seconds)
            self.dirty = False

    def stop(self):
        self.flush()
        self.last = self.session = None
        self.seconds = 0.0
