"""sandbox.py — tasinabilir surec izolasyonunun davranis testleri.

Kapsananlar: temiz env allowlist (secret sizmasi), ag-kesme (olu proxy env),
timeout enforcement, cikti limiti, izole calisma dizini. Testler `sys.executable`
ile kucuk Python snippet'leri kosar; Windows/macOS/Linux'ta calisir.

Not: sandbox kernel-duzeyi izolasyon SAGLAMAZ (kod bunu itiraf eder); bu testler
saglanan garantileri (env temizligi, proxy env, timeout, limit) dogrular.
"""
from __future__ import annotations

import sys

from core.sandbox import DEAD_PROXY, ENV_ALLOWLIST, MAX_OUTPUT, run


def _py(code: str) -> list[str]:
    return [sys.executable, "-c", code]


def test_basic_run_success(tmp_path):
    res = run(_py("print('merhaba')"), runs_dir=tmp_path)
    assert res.ok
    assert res.exit_code == 0
    assert "merhaba" in res.stdout
    assert not res.timed_out


def test_nonzero_exit_is_not_ok(tmp_path):
    res = run(_py("import sys; sys.exit(3)"), runs_dir=tmp_path)
    assert res.exit_code == 3
    assert not res.ok


def test_secret_env_does_not_leak(tmp_path, monkeypatch):
    # Kullanici secret'i sandbox surecine SIZMAMALI (allowlist disi)
    monkeypatch.setenv("MY_SECRET_TOKEN", "sk-super-secret")
    res = run(
        _py("import os; print(os.environ.get('MY_SECRET_TOKEN', 'YOK'))"),
        runs_dir=tmp_path,
    )
    assert "sk-super-secret" not in res.stdout
    assert "YOK" in res.stdout


def test_allowlisted_env_still_available(tmp_path):
    # PATH her zaman gecmeli (arac erisimi icin)
    res = run(_py("import os; print('PATH' in os.environ and len(os.environ['PATH'])>0)"),
              runs_dir=tmp_path)
    assert "True" in res.stdout


def test_network_off_sets_dead_proxy(tmp_path):
    res = run(
        _py("import os; print(os.environ.get('HTTP_PROXY','NONE'))"),
        runs_dir=tmp_path, network=False,
    )
    assert DEAD_PROXY in res.stdout


def test_network_on_does_not_force_dead_proxy(tmp_path, monkeypatch):
    monkeypatch.delenv("HTTP_PROXY", raising=False)
    res = run(
        _py("import os; print(os.environ.get('HTTP_PROXY','NONE'))"),
        runs_dir=tmp_path, network=True,
    )
    # network=True iken olu proxy zorlanmaz
    assert DEAD_PROXY not in res.stdout


def test_timeout_enforced(tmp_path):
    res = run(
        _py("import time; time.sleep(30)"),
        runs_dir=tmp_path, timeout=1,
    )
    assert res.timed_out
    assert not res.ok


def test_output_is_truncated(tmp_path):
    # MAX_OUTPUT'tan cok daha fazla uret; kesilmeli
    res = run(
        _py(f"print('A' * ({MAX_OUTPUT} + 50000))"),
        runs_dir=tmp_path,
    )
    assert len(res.stdout) <= MAX_OUTPUT


def test_workdir_is_isolated_and_created(tmp_path):
    res = run(_py("print('x')"), runs_dir=tmp_path)
    from pathlib import Path
    wd = Path(res.workdir)
    assert wd.exists()
    assert tmp_path in wd.parents


def test_home_redirected_into_workdir(tmp_path):
    # HOME/USERPROFILE sandbox workdir'ine yonlendirilir (kullanici home'u gizlenir)
    res = run(
        _py("import os; print(os.environ.get('HOME') or os.environ.get('USERPROFILE'))"),
        runs_dir=tmp_path,
    )
    assert res.workdir in res.stdout


def test_missing_executable_returns_127(tmp_path):
    res = run(["definitely-not-a-real-binary-xyz"], runs_dir=tmp_path)
    assert res.exit_code == 127
    assert not res.ok


def test_env_allowlist_is_minimal():
    # Guvenlik regresyon korumasi: allowlist'e sinsi bir secret degiskeni eklenmesin
    for name in ENV_ALLOWLIST:
        assert not any(s in name.upper() for s in ("SECRET", "TOKEN", "KEY", "PASSWORD", "AWS", "GITHUB"))
