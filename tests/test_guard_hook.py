"""guard_hook.py — anayasal PreToolUse uygulayicisinin dogrudan davranis testleri.

Onceki testler (test_setup_patch.py) yalnizca yama mantigini izole ediyordu.
Burada gercek `is_protected_file`, `command_touches_protected`, `HUMAN_ONLY` ve
`main()` dispatch davranisini — koruma sinirlarinin fiilen uygulandigini —
dogruluyoruz. guard_hook.py anayasal olarak korunmus bir dosyadir (degistirilmez);
bu testler onun mevcut garantilerini kilitler.
"""
from __future__ import annotations

import importlib.util
import io
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def _load_guard():
    """guard_hook modulunu izole yukler (ROOT sabiti gercek repo'ya isaret eder)."""
    spec = importlib.util.spec_from_file_location(
        "guard_hook_under_test", ROOT / "core" / "guard_hook.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


guard = _load_guard()
PROTECTED = guard.load_protected()


# --- is_protected_file -------------------------------------------------------

@pytest.mark.parametrize("path", [
    "policies/immutable-core.yaml",
    "policies/permissions.yaml",
    "core/guard_hook.py",
    "core/policy.py",
    "core/audit.py",
    ".claude/settings.json",
])
def test_protected_files_are_detected(path):
    assert guard.is_protected_file(path, PROTECTED) is not None


@pytest.mark.parametrize("path", [
    "README.md",
    "core/scanner.py",
    "tests/test_guard_hook.py",
    "some/random/file.txt",
])
def test_unprotected_files_pass(path):
    assert guard.is_protected_file(path, PROTECTED) is None


def test_backslash_and_case_normalized():
    # Windows yolu + buyuk harf -> yine yakalanmali
    assert guard.is_protected_file(r"POLICIES\Immutable-Core.yaml", PROTECTED) is not None


def test_directory_protection_matches_contents():
    # audit/ dizin korumasi: altindaki herhangi bir dosya
    prot = ["audit/"]
    assert guard.is_protected_file("audit/audit.jsonl", prot) is not None
    assert guard.is_protected_file("audit/subdir/x.log", prot) is not None
    assert guard.is_protected_file("audits.txt", prot) is None


def test_absolute_path_to_protected_file_detected():
    abs_path = str((ROOT / "core" / "policy.py").resolve())
    assert guard.is_protected_file(abs_path, PROTECTED) is not None


# --- command_touches_protected ----------------------------------------------

@pytest.mark.parametrize("cmd", [
    "echo x > policies/immutable-core.yaml",
    "rm core/guard_hook.py",
    "Remove-Item core/policy.py -Force",
    "mv audit/audit.jsonl /tmp/x",
    "sed -i 's/a/b/' policies/permissions.yaml",
    "Set-Content core/audit.py 'x'",
])
def test_mutating_commands_on_protected_blocked(cmd):
    assert guard.command_touches_protected(cmd, PROTECTED) is not None


@pytest.mark.parametrize("cmd", [
    "python -m core verify",
    "cat policies/immutable-core.yaml",
    "python -m core verify 2>&1 | Select-String immutable-core",
    "type core/policy.py",
    "grep foo core/audit.py",
])
def test_readonly_commands_on_protected_allowed(cmd):
    # Salt-okuma (redirect birlestirme dahil) mutasyon SAYILMAZ
    assert guard.command_touches_protected(cmd, PROTECTED) is None


# --- HUMAN_ONLY (approve / seal-policy) -------------------------------------

@pytest.mark.parametrize("cmd", [
    "python -m core approve abc-123",
    "python -m core seal-policy",
    "python core/__main__.py approve x",
    "py -m core seal-policy",
])
def test_human_only_commands_detected(cmd):
    assert guard.HUMAN_ONLY.search(cmd) is not None


@pytest.mark.parametrize("cmd", [
    "python -m core verify",
    "python -m core list",
    "python -m core gap --domain x",
    "python -m core scan staging/skills/x",
])
def test_agent_allowed_commands_not_human_only(cmd):
    assert guard.HUMAN_ONLY.search(cmd) is None


# --- main() dispatch (uctan uca, exit kodu ile) ------------------------------

def _run_main(monkeypatch, payload, env=None):
    """main()'i verilen JSON payload ile calistirir; sys.exit kodunu dondurur."""
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(payload)))
    monkeypatch.setattr(sys, "stderr", io.StringIO())
    # Gercek audit loguna yazmayi engelle (test yan etkisi olmasin)
    monkeypatch.setattr(guard, "_audit_block", lambda *a, **k: None)
    for k in ("AJAN_GUARD_BYPASS",):
        monkeypatch.delenv(k, raising=False)
    if env:
        for k, v in env.items():
            monkeypatch.setenv(k, v)
    with pytest.raises(SystemExit) as exc:
        guard.main()
    return exc.value.code


def test_main_blocks_write_to_protected(monkeypatch):
    code = _run_main(monkeypatch, {
        "tool_name": "Write",
        "tool_input": {"file_path": "policies/immutable-core.yaml", "content": "x"},
    })
    assert code == 2  # bloklandi


def test_main_allows_write_to_normal_file(monkeypatch):
    code = _run_main(monkeypatch, {
        "tool_name": "Write",
        "tool_input": {"file_path": "README.md", "content": "x"},
    })
    assert code == 0


def test_main_blocks_human_only_shell(monkeypatch):
    code = _run_main(monkeypatch, {
        "tool_name": "Bash",
        "tool_input": {"command": "python -m core approve some-id"},
    })
    assert code == 2


def test_main_blocks_shell_mutation_of_protected(monkeypatch):
    code = _run_main(monkeypatch, {
        "tool_name": "Bash",
        "tool_input": {"command": "echo hacked > core/guard_hook.py"},
    })
    assert code == 2


def test_main_allows_readonly_shell(monkeypatch):
    code = _run_main(monkeypatch, {
        "tool_name": "Bash",
        "tool_input": {"command": "python -m core verify"},
    })
    assert code == 0


def test_bypass_env_disables_guard(monkeypatch):
    # Insan kendi terminalinde AJAN_GUARD_BYPASS=1 ayarlayabilir (dokumante kacis)
    code = _run_main(monkeypatch, {
        "tool_name": "Write",
        "tool_input": {"file_path": "policies/immutable-core.yaml", "content": "x"},
    }, env={"AJAN_GUARD_BYPASS": "1"})
    assert code == 0


def test_malformed_stdin_fails_open(monkeypatch):
    # Bozuk girdi tum araclari kilitlememeli (kontrollu fail-open)
    monkeypatch.setattr(sys, "stdin", io.StringIO("not json {{{"))
    monkeypatch.delenv("AJAN_GUARD_BYPASS", raising=False)
    with pytest.raises(SystemExit) as exc:
        guard.main()
    assert exc.value.code == 0


def test_edit_tool_on_protected_blocked(monkeypatch):
    code = _run_main(monkeypatch, {
        "tool_name": "Edit",
        "tool_input": {"file_path": "core/policy.py", "old_string": "a", "new_string": "b"},
    })
    assert code == 2


def test_notebookedit_uses_notebook_path(monkeypatch):
    code = _run_main(monkeypatch, {
        "tool_name": "NotebookEdit",
        "tool_input": {"notebook_path": "policies/permissions.yaml"},
    })
    assert code == 2
