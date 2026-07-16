"""Capability Registry: SQLite tabanli surumlu yetenek katalogu.

Durum yasam dongusu:
  experimental -> sandbox-validated -> project-approved -> production-approved
  her durumdan -> deprecated / revoked
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import time
from pathlib import Path

STATUSES = [
    "experimental",
    "sandbox-validated",
    "project-approved",
    "production-approved",
    "deprecated",
    "revoked",
]
ACTIVE_STATUSES = {"project-approved", "production-approved"}

_SCHEMA = """
CREATE TABLE IF NOT EXISTS capabilities (
    id TEXT NOT NULL,
    version TEXT NOT NULL,
    type TEXT NOT NULL DEFAULT 'skill',
    domains TEXT NOT NULL DEFAULT '[]',
    status TEXT NOT NULL DEFAULT 'experimental',
    risk_level TEXT NOT NULL DEFAULT 'medium',
    source TEXT DEFAULT '',
    path TEXT DEFAULT '',
    content_hash TEXT DEFAULT '',
    validation_score REAL DEFAULT 0.0,
    scan_score INTEGER DEFAULT 0,
    permissions TEXT DEFAULT '[]',
    notes TEXT DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    last_validated_at TEXT DEFAULT '',
    PRIMARY KEY (id, version)
);
"""


def dir_content_hash(path: Path) -> str:
    """Dizindeki tum dosyalarin deterministik icerik ozeti."""
    h = hashlib.sha256()
    path = Path(path)
    if path.is_file():
        h.update(path.read_bytes())
        return h.hexdigest()
    for f in sorted(path.rglob("*")):
        if f.is_file():
            h.update(str(f.relative_to(path)).encode("utf-8"))
            h.update(f.read_bytes())
    return h.hexdigest()


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S")


class Registry:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path))
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    # --- yazma ---------------------------------------------------------
    def add(self, id: str, version: str = "0.1.0", *, type: str = "skill",
            domains: list[str] | None = None, status: str = "experimental",
            risk_level: str = "medium", source: str = "", path: str = "",
            content_hash: str = "", validation_score: float = 0.0,
            scan_score: int = 0, permissions: list[str] | None = None,
            notes: str = "") -> None:
        if status not in STATUSES:
            raise ValueError(f"gecersiz durum: {status}")
        now = _now()
        self._conn.execute(
            """INSERT OR REPLACE INTO capabilities
               (id, version, type, domains, status, risk_level, source, path,
                content_hash, validation_score, scan_score, permissions, notes,
                created_at, updated_at, last_validated_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,
                       COALESCE((SELECT created_at FROM capabilities WHERE id=? AND version=?), ?),
                       ?, ?)""",
            (id, version, type, json.dumps(domains or []), status, risk_level,
             source, path, content_hash, validation_score, scan_score,
             json.dumps(permissions or []), notes, id, version, now, now, ""),
        )
        self._conn.commit()

    def set_status(self, id: str, status: str, version: str | None = None) -> None:
        if status not in STATUSES:
            raise ValueError(f"gecersiz durum: {status}")
        row = self.latest(id) if version is None else self.get(id, version)
        if row is None:
            raise KeyError(f"kayit yok: {id}")
        self._conn.execute(
            "UPDATE capabilities SET status=?, updated_at=? WHERE id=? AND version=?",
            (status, _now(), id, row["version"]),
        )
        self._conn.commit()

    def set_validation(self, id: str, score: float, version: str | None = None) -> None:
        row = self.latest(id) if version is None else self.get(id, version)
        if row is None:
            raise KeyError(f"kayit yok: {id}")
        self._conn.execute(
            "UPDATE capabilities SET validation_score=?, last_validated_at=?, updated_at=? "
            "WHERE id=? AND version=?",
            (score, _now(), _now(), id, row["version"]),
        )
        self._conn.commit()

    # --- okuma ---------------------------------------------------------
    def get(self, id: str, version: str) -> dict | None:
        row = self._conn.execute(
            "SELECT * FROM capabilities WHERE id=? AND version=?", (id, version)
        ).fetchone()
        return dict(row) if row else None

    def latest(self, id: str) -> dict | None:
        row = self._conn.execute(
            "SELECT * FROM capabilities WHERE id=? ORDER BY updated_at DESC, version DESC LIMIT 1",
            (id,),
        ).fetchone()
        return dict(row) if row else None

    def list(self, status: str | None = None) -> list[dict]:
        if status:
            rows = self._conn.execute(
                "SELECT * FROM capabilities WHERE status=? ORDER BY id", (status,)
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT * FROM capabilities ORDER BY id, version"
            ).fetchall()
        return [dict(r) for r in rows]

    def search(self, query: str = "", domain: str = "", active_only: bool = False) -> list[dict]:
        rows = self.list()
        out = []
        for r in rows:
            if active_only and r["status"] not in ACTIVE_STATUSES:
                continue
            domains = json.loads(r["domains"] or "[]")
            if domain and domain not in domains:
                continue
            hay = " ".join([r["id"], r["notes"] or "", " ".join(domains)]).lower()
            if query and query.lower() not in hay:
                continue
            out.append(r)
        return out

    def stale(self, days: int = 90) -> list[dict]:
        cutoff = time.time() - days * 86400
        out = []
        for r in self.list():
            if r["status"] not in ACTIVE_STATUSES:
                continue
            lv = r["last_validated_at"] or r["updated_at"]
            try:
                t = time.mktime(time.strptime(lv[:19], "%Y-%m-%dT%H:%M:%S"))
            except ValueError:
                t = 0
            if t < cutoff:
                out.append(r)
        return out
