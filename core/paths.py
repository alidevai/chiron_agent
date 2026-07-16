"""Platform dizin yerlesimi. Tum modüller Paths uzerinden konum alir;
testler gecici bir kok dizinle ayni kodu calistirabilir."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Paths:
    root: Path = field(default_factory=lambda: DEFAULT_ROOT)

    @property
    def policies(self) -> Path:
        return self.root / "policies"

    @property
    def immutable_core(self) -> Path:
        return self.policies / "immutable-core.yaml"

    @property
    def immutable_seal(self) -> Path:
        return self.policies / "immutable-core.sha256"

    @property
    def registry_db(self) -> Path:
        return self.root / "registry" / "registry.db"

    @property
    def revoked_dir(self) -> Path:
        return self.root / "registry" / "revoked"

    @property
    def lessons_db(self) -> Path:
        return self.root / "registry" / "lessons.db"

    @property
    def audit_log(self) -> Path:
        return self.root / "audit" / "audit.jsonl"

    @property
    def staging_skills(self) -> Path:
        return self.root / "staging" / "skills"

    @property
    def active_skills(self) -> Path:
        return self.root / ".claude" / "skills"

    @property
    def sandbox_runs(self) -> Path:
        return self.root / "sandbox" / "runs"

    @property
    def evals_dir(self) -> Path:
        return self.root / "evals"

    @property
    def approvals_pending(self) -> Path:
        return self.root / "approvals" / "pending"

    @property
    def approvals_decided(self) -> Path:
        return self.root / "approvals" / "decided"

    def ensure(self) -> None:
        for p in [
            self.policies,
            self.registry_db.parent,
            self.revoked_dir,
            self.audit_log.parent,
            self.staging_skills,
            self.active_skills,
            self.sandbox_runs,
            self.evals_dir,
            self.approvals_pending,
            self.approvals_decided,
        ]:
            p.mkdir(parents=True, exist_ok=True)
