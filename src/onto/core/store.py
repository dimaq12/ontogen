# -*- coding: utf-8 -*-
"""EventStore — the log persistence fabric (RELEASE 0.1).

The log = the wire history (duplicates in the log are legal — dedup is organism
semantics, window D26; the store decides nothing, it only stores and survives
kill -9). Two fabrics:

  jsonl  — the default: append+fsync per event, a ragged line = torn;
  sqlite — a real DBMS (stdlib sqlite3): WAL, journal durability, a single
           events.db file; synchronous NORMAL (commit grouping — honestly
           documented: the loss window = the last WAL checkpoint, the file
           itself is not corrupted).

Interface: append(dict) | read_from(idx) -> (dict|None=torn) | count() |
rewrite(events, backup_tag) — for the migration functor (backup mandatory).
"""
from __future__ import annotations

import json
import os
import pathlib
import shutil
import sqlite3


class JsonlStore:
    name = "jsonl"

    def __init__(self, data_dir: str | pathlib.Path):
        self.path = pathlib.Path(data_dir) / "events.jsonl"

    def append(self, event: dict) -> None:
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
            f.flush()
            os.fsync(f.fileno())

    def read_from(self, idx: int):
        if not self.path.exists():
            return
        for i, line in enumerate(self.path.read_text(encoding="utf-8").splitlines()):
            if i < idx or not line.strip():
                continue
            try:
                yield json.loads(line)
            except ValueError:
                yield None                      # torn

    def count(self) -> int:
        if not self.path.exists():
            return 0
        return sum(1 for l in self.path.read_text(encoding="utf-8").splitlines()
                   if l.strip())

    def rewrite(self, events: list[dict], backup_tag: str) -> str:
        backup = self.path.with_name(f"events.{backup_tag}.bak.jsonl")
        if self.path.exists():
            backup.write_text(self.path.read_text(encoding="utf-8"),
                              encoding="utf-8")
        self.path.write_text(
            "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in events),
            encoding="utf-8")
        return str(backup)


class SqliteStore:
    name = "sqlite"

    def __init__(self, data_dir: str | pathlib.Path):
        self.path = pathlib.Path(data_dir) / "events.db"
        # check_same_thread=False: access to the organism (and the store) is
        # serialized by the serve/warden lock — multithreaded HTTP,
        # single-threaded writes
        self._db = sqlite3.connect(self.path, check_same_thread=False)
        self._db.execute("PRAGMA journal_mode=WAL")
        self._db.execute("PRAGMA synchronous=NORMAL")
        self._db.execute(
            "CREATE TABLE IF NOT EXISTS events ("
            "seq INTEGER PRIMARY KEY AUTOINCREMENT, raw TEXT NOT NULL)")
        self._db.commit()

    def append(self, event: dict) -> None:
        self._db.execute("INSERT INTO events (raw) VALUES (?)",
                         (json.dumps(event, ensure_ascii=False),))
        self._db.commit()

    def read_from(self, idx: int):
        cur = self._db.execute(
            "SELECT raw FROM events ORDER BY seq LIMIT -1 OFFSET ?", (idx,))
        for (raw,) in cur:
            try:
                yield json.loads(raw)
            except ValueError:
                yield None

    def count(self) -> int:
        return self._db.execute("SELECT COUNT(*) FROM events").fetchone()[0]

    def rewrite(self, events: list[dict], backup_tag: str) -> str:
        backup = self.path.with_name(f"events.{backup_tag}.bak.db")
        self._db.commit()
        self._db.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        shutil.copy(self.path, backup)
        self._db.execute("DELETE FROM events")
        self._db.executemany(
            "INSERT INTO events (raw) VALUES (?)",
            [(json.dumps(e, ensure_ascii=False),) for e in events])
        self._db.commit()
        return str(backup)

    def close(self) -> None:
        self._db.close()


def open_store(data_dir: str | pathlib.Path, kind: str | None = None):
    """kind=None: auto-detect from files (events.db > events.jsonl > jsonl)."""
    data = pathlib.Path(data_dir)
    if kind is None:
        kind = "sqlite" if (data / "events.db").exists() else "jsonl"
    if kind == "sqlite":
        return SqliteStore(data)
    if kind == "jsonl":
        return JsonlStore(data)
    raise ValueError(f"unknown store kind '{kind}' (jsonl|sqlite)")
