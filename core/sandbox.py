"""Tasinabilir surec sandbox'i (Docker'siz Windows/macOS/Linux).

Saglananlar:
  - Temiz ortam degiskenleri (kullanici secret'lari/env sizmaz; allowlist)
  - Ag erisimi varsayilan kapali: HTTP(S)_PROXY olu proxy'ye yonlendirilir
    (cogu HTTP kutuphanesi proxy env'ine uyar; kernel duzeyi engel DEGILDIR)
  - Zaman asimi ve cikti limiti
  - Izole calisma dizini (sandbox/runs/<ts>)

Bilinen sinirlar (dokumante edilmis bilincli odun):
  - Kernel duzeyinde izolasyon yoktur; raw socket acan kotu niyetli kod
    proxy tuzagini asabilir. Bu nedenle sandbox calistirmadan ONCE statik
    tarama (scanner) zorunludur ve kritik bulgu tasiyan aday hic calistirilmaz.
"""
from __future__ import annotations

import os
import subprocess
import time
import uuid
from dataclasses import dataclass
from pathlib import Path

DEAD_PROXY = "http://127.0.0.1:9"  # discard port: baglanti aninda reddedilir
ENV_ALLOWLIST = ["SYSTEMROOT", "WINDIR", "COMSPEC", "PATHEXT", "NUMBER_OF_PROCESSORS", "OS", "LANG", "LC_ALL"]
MAX_OUTPUT = 200_000


@dataclass
class SandboxResult:
    exit_code: int
    stdout: str
    stderr: str
    duration_s: float
    timed_out: bool
    workdir: str

    @property
    def ok(self) -> bool:
        return self.exit_code == 0 and not self.timed_out

    def to_dict(self) -> dict:
        return vars(self)


def _clean_env(network: bool, extra_env: dict | None) -> dict:
    env = {k: os.environ[k] for k in ENV_ALLOWLIST if k in os.environ}
    env["PATH"] = os.environ.get("PATH", "")  # arac erisimi icin gerekli
    if not network:
        for var in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"):
            env[var] = DEAD_PROXY
        env["NO_PROXY"] = ""
        env["no_proxy"] = ""
    if extra_env:
        env.update(extra_env)
    return env


def run(cmd: list[str], *, runs_dir: Path, cwd: Path | None = None,
        timeout: int = 120, network: bool = False,
        extra_env: dict | None = None) -> SandboxResult:
    """Komutu izole calisma dizininde, temiz ortamda calistirir."""
    runs_dir = Path(runs_dir)
    workdir = runs_dir / f"{time.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"
    workdir.mkdir(parents=True, exist_ok=True)
    env = _clean_env(network, extra_env)
    env["TEMP"] = env["TMP"] = str(workdir)
    env["HOME"] = env["USERPROFILE"] = str(workdir)

    start = time.time()
    timed_out = False
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd or workdir),
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
            errors="replace",
        )
        exit_code, stdout, stderr = proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired as e:
        timed_out = True
        exit_code = -1
        stdout = (e.stdout or b"").decode("utf-8", "replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
        stderr = (e.stderr or b"").decode("utf-8", "replace") if isinstance(e.stderr, bytes) else (e.stderr or "")
    except FileNotFoundError as e:
        exit_code, stdout, stderr = 127, "", f"komut bulunamadi: {e}"

    return SandboxResult(
        exit_code=exit_code,
        stdout=stdout[:MAX_OUTPUT],
        stderr=stderr[:MAX_OUTPUT],
        duration_s=round(time.time() - start, 3),
        timed_out=timed_out,
        workdir=str(workdir),
    )
