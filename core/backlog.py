"""Insan Gorev Kuyrugu / Operator Konsolu.

AI, calisirken YALNIZCA insanin yapabilecegi bir seye carptiginda (altyapi/mimari
degisiklik, politika duzenleme, production dagitimi, tehlikeli izin) bunu sohbette
soyleyip unutmak yerine kalici bir KARTA yazar (`request_human`). Kullanici tek
bakista tum insan-isi listesini gorur (`collect` + `render_markdown`).

Bu, `approvals/pending/` (yetenek onaylari) ile ayni felsefenin genellemesidir:
"AI hazirlar/bildirir, insan karar verir/yapar." Salt dosya tabanli; ek bagimlilik yok.

Kategoriler ve toplanan kaynaklar:
  - onay bekleyen yetenekler   -> approvals/pending/*.md  (insan: `approve`/`revoke`)
  - AI'in bildirdigi insan isi  -> human/pending/*.md      (bu modul yazar)
  - yeniden dogrulama bekleyen  -> registry.stale()
  - bilincli ertelenen altyapi  -> DEFERRED_INFRA (statik; DevOps/gelistirici isi)
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

import yaml

from .paths import Paths
from .registry import Registry

CATEGORIES = ("infra", "policy", "deploy", "permission", "security", "other")

# Anayasal olarak AI'in YAPAMAYACAGI, insan/gelistirici tarafindan yapilacak
# bilincli ertelenen isler (vizyon dokumani ile hizali). Kullaniciya her zaman
# gorunur ki "AI bunu bir gun kendi yapacak" yanilgisi olmasin.
DEFERRED_INFRA = [
    {"title": "Container/kernel duzeyi sandbox izolasyonu",
     "category": "infra", "risk": "medium",
     "why": "Mevcut sandbox surec-duzeyi; kernel/ag izolasyonu yok (bilincli odun).",
     "action": "Docker/gVisor/firecracker ile izole calisma; RO-fs + ag kapali profil."},
    {"title": "Imzali release + SBOM imzalama + provenance",
     "category": "security", "risk": "medium",
     "why": "SBOM uretiliyor (core sbom) ama imzali/attested release yok.",
     "action": "sigstore/cosign ile artefakt imzalama; SLSA provenance CI adimi."},
    {"title": "RBAC + secret-broker + gozlemlenebilirlik (Faz 5)",
     "category": "infra", "risk": "medium",
     "why": "Kurumsal olgunluk katmani; runtime AI bunu kurmaz.",
     "action": "Rol tabanli erisim, merkezi secret store, metrik/log toplama."},
    {"title": "Canary / staged deployment sureci",
     "category": "deploy", "risk": "low",
     "why": "Kademeli yayim + otomatik geri alma yok.",
     "action": "Yeni surumu once sinirli kapsamda calistir, metrik esigiyle ilerlet."},
]


@dataclass
class HumanTask:
    id: str
    title: str
    category: str
    risk: str
    why: str
    action: str
    created: str
    source: str = "agent"


def _slug(text: str) -> str:
    keep = [c.lower() if c.isalnum() else "-" for c in text]
    s = "".join(keep).strip("-")
    while "--" in s:
        s = s.replace("--", "-")
    return s[:40] or "task"


def request_human(paths: Paths, title: str, *, category: str = "other",
                  why: str = "", action: str = "", risk: str = "medium") -> dict:
    """AI'in insana birakmasi gereken bir isi kalici karta yazar."""
    paths.human_pending.mkdir(parents=True, exist_ok=True)
    if category not in CATEGORIES:
        category = "other"
    tid = f"{time.strftime('%Y%m%d-%H%M%S')}-{_slug(title)}"
    card = {
        "id": tid, "title": title, "category": category, "risk": risk,
        "created": time.strftime("%Y-%m-%dT%H:%M:%S"), "source": "agent",
    }
    body = (
        f"---\n{yaml.safe_dump(card, allow_unicode=True, sort_keys=False)}---\n\n"
        f"**Neden (AI yapamaz):** {why or '-'}\n\n"
        f"**Onerilen insan aksiyonu:** {action or '-'}\n"
    )
    (paths.human_pending / f"{tid}.md").write_text(body, encoding="utf-8")
    return card


def _read_cards(directory: Path) -> list[dict]:
    out: list[dict] = []
    if not directory.exists():
        return out
    for f in sorted(directory.glob("*.md")):
        text = f.read_text(encoding="utf-8", errors="replace")
        meta: dict = {}
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                try:
                    meta = yaml.safe_load(parts[1]) or {}
                except yaml.YAMLError:
                    meta = {}
        meta.setdefault("id", f.stem)
        meta.setdefault("title", f.stem)
        meta["_file"] = str(f)
        out.append(meta)
    return out


def resolve(paths: Paths, task_id: str) -> bool:
    """Bir insan gorevini 'yapildi' olarak arsivler (human/decided)."""
    src = paths.human_pending / f"{task_id}.md"
    if not src.exists():
        return False
    paths.human_decided.mkdir(parents=True, exist_ok=True)
    src.replace(paths.human_decided / f"{task_id}.md")
    return True


def collect(paths: Paths) -> dict:
    """Insanin yapmasi/karar vermesi gereken her seyi tek yerde toplar."""
    approvals = []
    if paths.approvals_pending.exists():
        approvals = [p.stem for p in sorted(paths.approvals_pending.glob("*.md"))]

    reg = Registry(paths.registry_db)
    try:
        stale = [{"id": r["id"], "version": r["version"], "status": r["status"]}
                 for r in reg.stale()]
    finally:
        reg.close()

    return {
        "capability_approvals": approvals,            # insan: approve/revoke
        "agent_filed_tasks": _read_cards(paths.human_pending),
        "stale_revalidation": stale,
        "deferred_infra": DEFERRED_INFRA,
        "counts": {
            "approvals": len(approvals),
            "agent_tasks": len(_read_cards(paths.human_pending)),
            "stale": len(stale),
            "deferred_infra": len(DEFERRED_INFRA),
        },
    }


def render_markdown(data: dict) -> str:
    lines = ["# İnsan Görev Kuyruğu (Operatör Konsolu)", ""]
    lines.append("AI'ın çalışırken **yapamayacağı / insan onayı gereken** işler. "
                 "Bunlar yalnızca **insan** tarafından yapılır.\n")

    ap = data["capability_approvals"]
    lines.append(f"## 🔴 Onay bekleyen yetenekler ({len(ap)})")
    if ap:
        for a in ap:
            lines.append(f"- `{a}` → `python -m core approve {a} --by <isim>` veya `revoke`")
    else:
        lines.append("- (yok)")
    lines.append("")

    tasks = data["agent_filed_tasks"]
    lines.append(f"## 🟠 AI'ın bildirdiği insan işleri ({len(tasks)})")
    if tasks:
        for t in tasks:
            lines.append(f"- **[{t.get('category','?')}/{t.get('risk','?')}]** "
                         f"{t.get('title','?')}  \n  `resolve`: "
                         f"`python -m core resolve-human {t.get('id')}`")
    else:
        lines.append("- (yok)")
    lines.append("")

    st = data["stale_revalidation"]
    lines.append(f"## 🟡 Yeniden doğrulama bekleyen ({len(st)})")
    if st:
        for s in st:
            lines.append(f"- `{s['id']}` v{s['version']} ({s['status']})")
    else:
        lines.append("- (yok)")
    lines.append("")

    lines.append("## 🔵 Bilinçli ertelenen altyapı/mimari (DevOps/geliştirici işi)")
    for d in data["deferred_infra"]:
        lines.append(f"- **{d['title']}** _(risk: {d['risk']})_  \n"
                     f"  neden: {d['why']}  \n  aksiyon: {d['action']}")
    lines.append("")
    return "\n".join(lines)


def write_backlog(paths: Paths) -> dict:
    """Konsolu toplar, human/BACKLOG.md dosyasina yazar ve veriyi dondurur."""
    data = collect(paths)
    paths.human_backlog.parent.mkdir(parents=True, exist_ok=True)
    paths.human_backlog.write_text(render_markdown(data), encoding="utf-8")
    data["backlog_file"] = str(paths.human_backlog)
    return data
