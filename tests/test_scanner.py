from pathlib import Path

from core.scanner import scan_path

FIXTURES = Path(__file__).parent / "fixtures"


def test_malicious_rejected():
    result = scan_path(FIXTURES / "malicious-skill")
    assert result.has_critical
    assert result.verdict == "reject"
    ids = {f.rule_id for f in result.findings}
    # prompt injection, pipe-to-shell, ssh erisimi yakalanmali
    assert any(i.startswith("PI-") for i in ids)
    assert "SH-001" in ids
    assert "EX-001" in ids


def test_benign_passes():
    result = scan_path(FIXTURES / "benign-skill")
    assert not result.has_critical
    assert result.verdict in ("pass", "review")


def test_missing_skill_md_flagged(tmp_path):
    (tmp_path / "notes.txt").write_text("hello", encoding="utf-8")
    result = scan_path(tmp_path)
    assert any(f.rule_id == "ST-001" for f in result.findings)


def test_non_allowlisted_url_flagged(tmp_path):
    (tmp_path / "SKILL.md").write_text(
        "---\nname: x\n---\nsee http://random-tracker.example.io/beacon\n",
        encoding="utf-8")
    result = scan_path(tmp_path)
    assert any(f.rule_id == "NET-001" for f in result.findings)
