"""Hash-zincirli, salt-ekleme (append-only) audit log.

Her kayit bir oncekinin hash'ini tasir; tek bir satirin degistirilmesi
zincirin kalanini gecersiz kilar. `verify()` tum zinciri dogrular.
"""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

GENESIS = "0" * 64


def _record_hash(record: dict) -> str:
    payload = json.dumps(
        {k: v for k, v in record.items() if k != "hash"},
        sort_keys=True,
        ensure_ascii=False,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class AuditLog:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _last_hash(self) -> str:
        if not self.path.exists():
            return GENESIS
        last = None
        with self.path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    last = line
        if last is None:
            return GENESIS
        return json.loads(last).get("hash", GENESIS)

    def append(self, actor: str, action: str, details: dict | None = None) -> dict:
        record = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "actor": actor,
            "action": action,
            "details": details or {},
            "prev_hash": self._last_hash(),
        }
        record["hash"] = _record_hash(record)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        return record

    def verify(self) -> tuple[bool, str]:
        """Zinciri dogrular. (ok, mesaj) dondurur."""
        if not self.path.exists():
            return True, "audit log bos"
        prev = GENESIS
        with self.path.open("r", encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    return False, f"satir {i}: JSON bozuk"
                if record.get("prev_hash") != prev:
                    return False, f"satir {i}: zincir kirik (prev_hash uyusmuyor)"
                if record.get("hash") != _record_hash(record):
                    return False, f"satir {i}: kayit degistirilmis (hash uyusmuyor)"
                prev = record["hash"]
        return True, "audit zinciri saglam"

    def tail(self, n: int = 20) -> list[dict]:
        if not self.path.exists():
            return []
        lines = [l for l in self.path.read_text(encoding="utf-8").splitlines() if l.strip()]
        return [json.loads(l) for l in lines[-n:]]
