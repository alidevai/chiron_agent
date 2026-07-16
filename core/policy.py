"""Deny-by-default politika motoru.

Karar semantigi (deny-overrides):
  1) immutable-core.yaml butunlugu bozuksa -> her sey DENY (fail-closed)
  2) forbidden_actions icindeki eylem -> kosulsuz DENY
  3) human_approval_always icindeki eylem -> en az REQUIRE_APPROVAL
  4) Eslesen kurallardan biri deny ise -> DENY
  5) Degilse biri require_approval ise -> REQUIRE_APPROVAL
  6) Degilse allow kurali eslesir ve kosullari (context bayraklari) saglanirsa
     -> ALLOW; kosul eksikse fail-closed DENY
  7) Hicbir kural eslesmezse -> default_action (deny)
"""
from __future__ import annotations

import fnmatch
import hashlib
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .paths import Paths

ALLOW = "allow"
DENY = "deny"
REQUIRE_APPROVAL = "require_approval"


@dataclass
class Decision:
    effect: str
    reason: str
    rule_id: str | None = None
    missing_conditions: list[str] = field(default_factory=list)

    @property
    def allowed(self) -> bool:
        return self.effect == ALLOW


def file_sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class PolicyEngine:
    def __init__(self, paths: Paths):
        self.paths = paths
        self._immutable = None
        self._rules = None
        self._integrity_ok = None

    # --- yukleme -------------------------------------------------------
    def _load(self) -> None:
        if self._rules is not None:
            return
        self._immutable = yaml.safe_load(self.paths.immutable_core.read_text(encoding="utf-8"))
        rules = []
        for f in sorted(self.paths.policies.glob("*.yaml")):
            if f.name == "immutable-core.yaml":
                continue
            doc = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
            for rule in doc.get("rules", []) or []:
                rules.append(rule)
        self._rules = rules

    # --- butunluk ------------------------------------------------------
    def seal(self) -> str:
        """Immutable core'un guncel ozetini imzalar (yalnizca insan calistirir)."""
        digest = file_sha256(self.paths.immutable_core)
        self.paths.immutable_seal.write_text(digest + "\n", encoding="utf-8")
        return digest

    def verify_integrity(self) -> tuple[bool, str]:
        if not self.paths.immutable_core.exists():
            return False, "immutable-core.yaml yok"
        if not self.paths.immutable_seal.exists():
            return False, "immutable-core.sha256 muhru yok (python -m core seal-policy)"
        expected = self.paths.immutable_seal.read_text(encoding="utf-8").strip()
        actual = file_sha256(self.paths.immutable_core)
        if expected != actual:
            return False, "immutable-core.yaml degistirilmis: muhur uyusmuyor"
        return True, "politika butunlugu saglam"

    # --- karar ---------------------------------------------------------
    def decide(self, action: str, risk_level: str = "medium", context: dict | None = None) -> Decision:
        context = context or {}
        ok, msg = self.verify_integrity()
        if not ok:
            return Decision(DENY, f"fail-closed: {msg}", rule_id="integrity")
        self._load()

        forbidden = set(self._immutable.get("forbidden_actions", []) or [])
        if action in forbidden:
            return Decision(DENY, "anayasal sinir: forbidden_actions", rule_id="immutable")

        matched = []
        for rule in self._rules:
            pattern = rule.get("action", "")
            if not fnmatch.fnmatch(action, pattern):
                continue
            when = rule.get("when") or {}
            levels = when.get("risk_level")
            if levels is not None:
                if isinstance(levels, str):
                    levels = [levels]
                if risk_level not in levels:
                    continue
            matched.append(rule)

        always_approval = action in set(self._immutable.get("human_approval_always", []) or [])

        denies = [r for r in matched if r.get("effect") == DENY]
        if denies:
            return Decision(DENY, "politika kurali", rule_id=denies[0].get("id"))

        approvals = [r for r in matched if r.get("effect") == REQUIRE_APPROVAL]
        allows = [r for r in matched if r.get("effect") == ALLOW]

        if approvals or (always_approval and (allows or not matched)):
            rule = approvals[0] if approvals else None
            missing = self._missing_conditions(rule, context) if rule else []
            reason = "insan onayi gerekli"
            if always_approval:
                reason += " (anayasal: human_approval_always)"
            return Decision(
                REQUIRE_APPROVAL, reason,
                rule_id=rule.get("id") if rule else "immutable",
                missing_conditions=missing,
            )

        if allows:
            rule = allows[0]
            missing = self._missing_conditions(rule, context)
            if missing:
                return Decision(
                    DENY,
                    f"fail-closed: kosullar eksik: {', '.join(missing)}",
                    rule_id=rule.get("id"),
                    missing_conditions=missing,
                )
            return Decision(ALLOW, "politika kurali", rule_id=rule.get("id"))

        return Decision(DENY, "default deny: eslesen kural yok", rule_id="default")

    @staticmethod
    def _missing_conditions(rule: dict | None, context: dict) -> list[str]:
        if not rule:
            return []
        return [c for c in (rule.get("conditions") or []) if not context.get(c)]

    # --- korunan yollar --------------------------------------------------
    def protected_paths(self) -> list[str]:
        self._load()
        return list(self._immutable.get("protected_paths", []) or [])
