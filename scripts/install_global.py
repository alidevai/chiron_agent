"""Ajan'i GLOBAL kur — her projede (Cursor/Windsurf/VS Code + Claude Code eklentisi).

INSAN calistirir (bir kez):  python scripts/install_global.py

Ne yapar:
  1) `pip install -e .`  -> 'ajan' ve `python -m core` HER dizinden calisir.
  2) Seed skill'leri ve subagent'lari ~/.claude/ (kullanici seviyesi) altina kopyalar
     -> hangi projeyi acarsan ac Claude Code bunlari yukler.
  3) Hook'lari ~/.claude/settings.json'a ekler (idempotent):
       - PreToolUse    : python -m core guard        (anayasal koruma, her projede)
       - SessionStart  : python -m core session-start (otomatik devreye girme)
       - UserPromptSubmit: python -m core on-prompt   ("ajan devreye gir"/"is bitti")

Onemli notlar:
  - Platformun evi BU repo'dur (editable kurulum). policies/registry/audit merkezi
    olarak burada kalir; global kullanim tek yetenek kutuphanesini paylasir.
  - Cursor/Windsurf'un YERLESIK AI'i (Composer/Cascade) bu hook'lari calistirmaz;
    bu sistem yalnizca iclerindeki Claude Code eklentisiyle gecerlidir.
  - Guard hook, bu repo'nun anayasal dosyalarini korur; baska projelerdeki
    dosyalara karismaz (yalnizca ayni ada sahip korumali dosya adlarina dikkat).
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
USER_CLAUDE = Path.home() / ".claude"

HOOKS = {
    "PreToolUse": {
        "matcher": "Write|Edit|MultiEdit|NotebookEdit|Bash|PowerShell",
        "command": "python -m core guard",
    },
    "SessionStart": {"matcher": None, "command": "python -m core session-start"},
    "UserPromptSubmit": {"matcher": None, "command": "python -m core on-prompt"},
}


def pip_install() -> str:
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-e", "."],
                       cwd=str(REPO), check=True, capture_output=True, text=True)
        return "pip install -e . tamam ('ajan' ve 'python -m core' her yerde)"
    except subprocess.CalledProcessError as e:
        return f"pip install BASARISIZ: {e.stderr[-300:] if e.stderr else e}"


def copy_tree(src: Path, dst: Path) -> int:
    if not src.exists():
        return 0
    n = 0
    for item in src.iterdir():
        if item.is_dir():
            shutil.copytree(item, dst / item.name, dirs_exist_ok=True)
            n += 1
        elif item.suffix == ".md":
            dst.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, dst / item.name)
            n += 1
    return n


def copy_config() -> str:
    (USER_CLAUDE / "skills").mkdir(parents=True, exist_ok=True)
    (USER_CLAUDE / "agents").mkdir(parents=True, exist_ok=True)
    ns = copy_tree(REPO / ".claude" / "skills", USER_CLAUDE / "skills")
    na = copy_tree(REPO / ".claude" / "agents", USER_CLAUDE / "agents")
    return f"~/.claude'a kopyalandi: {ns} skill, {na} agent"


def _has_command(hook_list: list, command: str) -> bool:
    return command in json.dumps(hook_list)


def install_hooks() -> str:
    settings = USER_CLAUDE / "settings.json"
    data = {}
    if settings.exists():
        try:
            data = json.loads(settings.read_text(encoding="utf-8"))
        except Exception:
            data = {}
    hooks = data.setdefault("hooks", {})
    added = []
    for event, spec in HOOKS.items():
        bucket = hooks.setdefault(event, [])
        if _has_command(bucket, spec["command"]):
            continue
        entry = {"hooks": [{"type": "command", "command": spec["command"]}]}
        if spec["matcher"]:
            entry["matcher"] = spec["matcher"]
        bucket.append(entry)
        added.append(event)
    if added:
        USER_CLAUDE.mkdir(parents=True, exist_ok=True)
        settings.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                            encoding="utf-8")
        return f"~/.claude/settings.json hook eklendi: {', '.join(added)}"
    return "~/.claude/settings.json: hook'lar zaten kurulu"


def main() -> None:
    print("=== Ajan GLOBAL kurulum ===")
    print(" -", pip_install())
    print(" -", copy_config())
    print(" -", install_hooks())
    print("\nSonraki adimlar:")
    print("  1) Cursor/Windsurf/VS Code'da CLAUDE CODE EKLENTISININ kurulu oldugundan emin ol.")
    print("  2) IDE'yi (veya Claude Code oturumunu) yeniden baslat; hook'lar oturum basinda yuklenir.")
    print("  3) Herhangi bir projede: sistem otomatik devrede. \"ajan devreye gir\" / \"is bitti\" ile ac/kapa.")
    print("\nNot: Cursor/Windsurf yerlesik AI'i (Composer/Cascade) bu hook'lari calistirmaz;")
    print("     bu sistem yalnizca Claude Code eklentisiyle gecerlidir.")


if __name__ == "__main__":
    main()
