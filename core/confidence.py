"""Kanita dayali guven skoru ve Capability Gap raporu.

Vizyon dokumanindaki "confidence < 0.75" esigini olculebilir kilar.
Skor tahmin degil; registry'deki dogrulanmis yeteneklerden turetilir:

  taban                          0.25
  + kapsanan skill orani         0.00 - 0.35  (istenen skill'lerin aktif karsiligi)
  + dogrulama skoru katkisi      0.00 - 0.20  (kapsanan skill'lerin ort. validation_score'u)
  + tazelik                      0.00 - 0.10  (son 90 gunde dogrulanmis olma orani)
  + risk duzeltmesi              -0.15 - +0.10 (low +0.10, medium 0, high -0.10, critical -0.15)

Eylem esikleri:
  >= 0.75              proceed
  0.60 - 0.75          proceed_with_verification (bagimsiz evaluator zorunlu)
  <  0.60              research_and_stage_capability
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

from .registry import ACTIVE_STATUSES, Registry

RISK_ADJUST = {"low": 0.10, "medium": 0.0, "high": -0.10, "critical": -0.15}
FRESH_DAYS = 90


@dataclass
class GapReport:
    task_domain: str
    required_skills: list[str]
    risk_level: str
    existing: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    stale: list[str] = field(default_factory=list)
    confidence: float = 0.0
    action: str = ""
    evidence: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return vars(self)


def _is_fresh(row: dict) -> bool:
    lv = row.get("last_validated_at") or ""
    if not lv:
        return False
    try:
        t = time.mktime(time.strptime(lv[:19], "%Y-%m-%dT%H:%M:%S"))
    except ValueError:
        return False
    return (time.time() - t) < FRESH_DAYS * 86400


def assess(registry: Registry, *, domain: str, required_skills: list[str],
           risk_level: str = "medium") -> GapReport:
    report = GapReport(task_domain=domain, required_skills=required_skills,
                       risk_level=risk_level)
    if not required_skills:
        required_skills = []

    covered_rows = []
    for skill in required_skills:
        row = registry.latest(skill)
        if row and row["status"] in ACTIVE_STATUSES:
            report.existing.append(skill)
            covered_rows.append(row)
            if not _is_fresh(row):
                report.stale.append(skill)
            report.evidence.append(
                f"{skill}: {row['status']} v{row['version']} "
                f"(validation={row['validation_score']:.2f})"
            )
        else:
            report.missing.append(skill)
            report.evidence.append(f"{skill}: aktif kayit yok")

    n = max(1, len(required_skills))
    coverage = len(report.existing) / n
    avg_validation = (
        sum(r["validation_score"] for r in covered_rows) / len(covered_rows)
        if covered_rows else 0.0
    )
    freshness = (
        sum(1 for r in covered_rows if _is_fresh(r)) / len(covered_rows)
        if covered_rows else 0.0
    )

    score = 0.25
    score += 0.35 * coverage
    score += 0.20 * coverage * avg_validation
    score += 0.10 * freshness
    score += RISK_ADJUST.get(risk_level, 0.0)
    report.confidence = round(max(0.0, min(1.0, score)), 3)

    if report.confidence >= 0.75 and not report.missing:
        report.action = "proceed"
    elif report.confidence >= 0.60 and not report.missing:
        report.action = "proceed_with_verification"
    else:
        report.action = "research_and_stage_capability"
    return report
