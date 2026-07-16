"""Eval runner: bir yetenek ancak olculebilir testte basariliysa terfi eder.

Eval spec formati (evals/<capability-id>.yaml):

  capability: skill-adi
  minimum_score: 0.9
  checks:
    - name: frontmatter_var
      type: file_regex            # dosyada regex esles(sin/mesin)
      file: SKILL.md
      pattern: "^---"
      expect: present             # present | absent
    - name: guvenlik_taramasi
      type: scanner               # statik tarama esigi
      max_verdict: review         # pass | review (bu esikten kotusu fail)
    - name: script_calisiyor
      type: command               # sandbox icinde komut calistir
      command: [python, scripts/check.py]
      expect_exit: 0
      network: false
      critical: true              # critical check fail -> tum eval fail

Spec dosyasi yoksa varsayilan yapi kontrolleri uygulanir
(SKILL.md var mi, frontmatter var mi, tarama verdikti pass/review mi).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from . import sandbox as sbx
from .scanner import scan_path

VERDICT_ORDER = {"pass": 0, "review": 1, "reference_only": 2, "reject": 3}

DEFAULT_SPEC = {
    "minimum_score": 0.9,
    "checks": [
        {"name": "skill_md_exists", "type": "file_regex", "file": "SKILL.md",
         "pattern": r".", "expect": "present", "critical": True},
        {"name": "frontmatter", "type": "file_regex", "file": "SKILL.md",
         "pattern": r"^---", "expect": "present"},
        {"name": "security_scan", "type": "scanner", "max_verdict": "review",
         "critical": True},
    ],
}


@dataclass
class CheckResult:
    name: str
    passed: bool
    critical: bool
    detail: str = ""


@dataclass
class EvalResult:
    capability: str
    checks: list[CheckResult] = field(default_factory=list)
    minimum_score: float = 0.9

    @property
    def score(self) -> float:
        if not self.checks:
            return 0.0
        return sum(1 for c in self.checks if c.passed) / len(self.checks)

    @property
    def critical_failures(self) -> list[str]:
        return [c.name for c in self.checks if c.critical and not c.passed]

    @property
    def passed(self) -> bool:
        return self.score >= self.minimum_score and not self.critical_failures

    def to_dict(self) -> dict:
        return {
            "capability": self.capability,
            "score": round(self.score, 3),
            "minimum_score": self.minimum_score,
            "passed": self.passed,
            "critical_failures": self.critical_failures,
            "checks": [vars(c) for c in self.checks],
        }


def load_spec(evals_dir: Path, capability_id: str) -> dict:
    spec_path = Path(evals_dir) / f"{capability_id}.yaml"
    if spec_path.exists():
        return yaml.safe_load(spec_path.read_text(encoding="utf-8")) or DEFAULT_SPEC
    return DEFAULT_SPEC


def run_eval(capability_id: str, skill_dir: Path, *, evals_dir: Path,
             runs_dir: Path) -> EvalResult:
    spec = load_spec(evals_dir, capability_id)
    result = EvalResult(capability=capability_id,
                        minimum_score=float(spec.get("minimum_score", 0.9)))
    skill_dir = Path(skill_dir)

    for check in spec.get("checks", []):
        name = check.get("name", "isimsiz")
        ctype = check.get("type")
        critical = bool(check.get("critical", False))
        try:
            if ctype == "file_regex":
                f = skill_dir / check["file"]
                if not f.exists():
                    found = False
                    detail = f"dosya yok: {check['file']}"
                else:
                    text = f.read_text(encoding="utf-8", errors="replace")
                    found = re.search(check["pattern"], text, re.MULTILINE) is not None
                    detail = "desen bulundu" if found else "desen yok"
                expect_present = check.get("expect", "present") == "present"
                passed = found == expect_present
            elif ctype == "scanner":
                scan = scan_path(skill_dir)
                max_v = check.get("max_verdict", "review")
                passed = VERDICT_ORDER[scan.verdict] <= VERDICT_ORDER[max_v]
                detail = f"verdict={scan.verdict} score={scan.score}"
            elif ctype == "command":
                res = sbx.run(
                    list(check["command"]),
                    runs_dir=runs_dir,
                    cwd=skill_dir,
                    timeout=int(check.get("timeout", 120)),
                    network=bool(check.get("network", False)),
                )
                passed = res.exit_code == int(check.get("expect_exit", 0)) and not res.timed_out
                detail = f"exit={res.exit_code} timeout={res.timed_out}"
            else:
                passed, detail = False, f"bilinmeyen check tipi: {ctype}"
        except Exception as e:  # fail-closed: hata = fail
            passed, detail = False, f"hata: {e}"
        result.checks.append(CheckResult(name=name, passed=passed,
                                         critical=critical, detail=detail))
    return result
