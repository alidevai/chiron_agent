"""Aday Skill / MCP / tool icin statik guvenlik tarayicisi.

Vizyon dokumani Asama 3'un somutlastirilmis hali: prompt injection,
exfiltration, tehlikeli shell, gizlilik ihlali desenleri kural motoru olarak.

Skorlama (100 uzerinden, dusuk = riskli):
  critical bulgu -> otomatik REJECT (skordan bagimsiz)
  >= 85 pass | 70-84 review | 50-69 reference_only | < 50 reject
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

SEVERITY_PENALTY = {"critical": 100, "high": 25, "medium": 10, "low": 3}

# (id, severity, regex, aciklama)
RULES: list[tuple[str, str, str, str]] = [
    # --- prompt injection ---
    ("PI-001", "critical", r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions",
     "Prompt injection: onceki talimatlari yok sayma"),
    ("PI-002", "critical", r"(önceki|onceki)\s+talimatlar[ıi]\s+(yok\s*say|unut|iptal)",
     "Prompt injection (TR): onceki talimatlari yok sayma"),
    ("PI-003", "critical", r"(do\s+not|don't|never)\s+(tell|inform|show|reveal\s+to)\s+the\s+user",
     "Kullanicidan gizli davranma talimati"),
    ("PI-004", "critical", r"(kullan[ıi]c[ıi]dan\s+gizle|kullan[ıi]c[ıi]ya\s+s[öo]yleme)",
     "Kullanicidan gizli davranma talimati (TR)"),
    ("PI-005", "high", r"you\s+are\s+now\s+(in\s+)?(developer|dan|jailbreak|god)\s*mode",
     "Jailbreak kalibi"),
    ("PI-006", "high", r"(override|bypass|disable|skip)\s+.{0,30}(safety|security|guard|policy|güvenlik|politika)",
     "Guvenlik kontrollerini devre disi birakma talimati"),
    # --- exfiltration / secrets ---
    ("EX-001", "critical", r"(\.ssh[/\\]|id_rsa|\.aws[/\\]credentials|\.gnupg)",
     "SSH/AWS kimlik dosyalarina erisim"),
    ("EX-002", "high", r"(api[_-]?key|token|password|secret|credential)s?\b.{0,60}\b(send|post|upload|curl|fetch|gönder|aktar)",
     "Kimlik bilgisi disari gonderme kalibi"),
    ("EX-003", "high", r"\b(env|printenv|os\.environ)\b.{0,60}\b(http|post|send|upload|requests\.)",
     "Ortam degiskenlerini agla paylasma kalibi"),
    ("EX-004", "medium", r"[A-Za-z0-9+/=]{120,}",
     "Uzun base64/obfuscated blok"),
    # --- tehlikeli shell ---
    ("SH-001", "critical", r"(curl|wget|iwr|invoke-webrequest)[^\n|;]{0,200}\|\s*(bash|sh|zsh|powershell|iex|python)",
     "Pipe-to-shell: indirilen icerigi dogrudan calistirma"),
    ("SH-002", "critical", r"rm\s+-rf\s+(/|~|\$HOME)",
     "Yikici dosya silme"),
    ("SH-003", "high", r"remove-item\s+.{0,80}-recurse\s+.{0,40}-force",
     "Yikici dosya silme (PowerShell)"),
    ("SH-004", "medium", r"\b(eval|exec)\s*\(",
     "Dinamik kod calistirma"),
    ("SH-005", "high", r"(chmod\s+777|icacls\s+.{0,40}/grant\s+everyone)",
     "Asiri genis dosya izni"),
    # --- kurulum / supply chain ---
    ("SC-001", "high", r"\"(pre|post)install\"\s*:",
     "npm install script'i (supply chain riski)"),
    ("SC-002", "medium", r"pip\s+install\s+(?!-r\b)[^\n]*--index-url",
     "Ozel paket indeksi (dependency confusion riski)"),
    ("SC-003", "medium", r"git\s+clone\s+http://",
     "Sifresiz (http) kaynaktan kod cekme"),
    # --- audit / policy kurcalama ---
    ("PO-001", "critical", r"(audit[/\\]audit\.jsonl|immutable-core\.(yaml|sha256))",
     "Audit log veya anayasal politika dosyasina referans"),
    ("PO-002", "high", r"(delete|truncate|clear|sil)\s+.{0,30}(audit|log)",
     "Log silme talimati"),
]

URL_ALLOWLIST = (
    "github.com", "raw.githubusercontent.com", "docs.python.org", "pypi.org",
    "modelcontextprotocol.io", "anthropic.com", "agentskills.io", "arxiv.org",
    "microsoft.com", "playwright.dev", "freqtrade.io", "example.com",
)

SCAN_EXTENSIONS = {".md", ".py", ".sh", ".ps1", ".yaml", ".yml", ".json", ".txt", ".js", ".ts", ".toml", ".cfg"}
MAX_FILE_BYTES = 1_000_000


@dataclass
class Finding:
    rule_id: str
    severity: str
    description: str
    file: str
    line: int
    excerpt: str


@dataclass
class ScanResult:
    target: str
    findings: list[Finding] = field(default_factory=list)

    @property
    def score(self) -> int:
        s = 100
        for f in self.findings:
            s -= SEVERITY_PENALTY.get(f.severity, 0)
        return max(0, s)

    @property
    def has_critical(self) -> bool:
        return any(f.severity == "critical" for f in self.findings)

    @property
    def verdict(self) -> str:
        if self.has_critical:
            return "reject"
        s = self.score
        if s >= 85:
            return "pass"
        if s >= 70:
            return "review"
        if s >= 50:
            return "reference_only"
        return "reject"

    def to_dict(self) -> dict:
        return {
            "target": self.target,
            "score": self.score,
            "verdict": self.verdict,
            "findings": [vars(f) for f in self.findings],
        }


_COMPILED = [(rid, sev, re.compile(rx, re.IGNORECASE), desc) for rid, sev, rx, desc in RULES]
_URL_RE = re.compile(r"https?://([A-Za-z0-9.-]+)")


def _scan_text(text: str, rel: str, result: ScanResult) -> None:
    for lineno, line in enumerate(text.splitlines(), 1):
        for rid, sev, rx, desc in _COMPILED:
            if rx.search(line):
                result.findings.append(Finding(rid, sev, desc, rel, lineno, line.strip()[:160]))
        for m in _URL_RE.finditer(line):
            host = m.group(1).lower()
            if not any(host == d or host.endswith("." + d) for d in URL_ALLOWLIST):
                result.findings.append(Finding(
                    "NET-001", "medium",
                    f"Allowlist disi ag hedefi: {host}", rel, lineno, line.strip()[:160]))


def scan_path(target: Path) -> ScanResult:
    """Bir skill dizinini veya tek dosyayi tarar."""
    target = Path(target)
    result = ScanResult(target=str(target))
    files = [target] if target.is_file() else sorted(
        p for p in target.rglob("*")
        if p.is_file() and p.suffix.lower() in SCAN_EXTENSIONS
    )
    if target.is_dir() and not (target / "SKILL.md").exists():
        result.findings.append(Finding(
            "ST-001", "medium", "SKILL.md yok: standart disi paket",
            str(target), 0, ""))
    for f in files:
        try:
            if f.stat().st_size > MAX_FILE_BYTES:
                result.findings.append(Finding(
                    "ST-002", "medium", "Beklenmedik buyuk dosya", str(f), 0, ""))
                continue
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        rel = str(f.relative_to(target)) if target.is_dir() else f.name
        _scan_text(text, rel, result)
    return result
