"""GitHub kütüphane/repo arama aracı — "bu iş için en iyi kütüphane hangisi?".

Yazılım/tasarım işlerinde planlama sırasında, sistemin GitHub'ı DETERMINISTIK
sorgulayıp aday kütüphane/araç/referans repo bulmasını sağlar (ör. 3D için
three.js). Yıldız, bakım (pushed_at), lisans, arşiv durumu ve dili döner; karar
LLM'e kalır ama kanıt buradan gelir.

Minimal bağımlılık (stdlib urllib). Kimlik doğrulama opsiyonel: env'de GITHUB_TOKEN
varsa oran limiti yükselir (yoksa da anonim çalışır). Ağ hatası/limit -> zarif boş.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.github.com/search/repositories"


def _get(url: str, headers: dict, timeout: int) -> dict:
    req = urllib.request.Request(url, headers=headers, method="GET")  # nosec B310 - sabit https GitHub API
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # nosec B310
        return json.loads(resp.read().decode("utf-8", "replace"))


def _license(item: dict) -> str:
    lic = item.get("license")
    if isinstance(lic, dict):
        return lic.get("spdx_id") or lic.get("key") or ""
    return ""


def search_repos(query: str, *, language: str = "", sort: str = "stars",
                 limit: int = 10, timeout: int = 15, env: dict | None = None) -> dict:
    """GitHub'da repo arar; yıldıza göre sıralı aday listesi döner.

    sort: stars | updated | forks | help-wanted-issues
    """
    env = env if env is not None else dict(os.environ)
    q = query.strip()
    if language:
        q += f" language:{language}"
    limit = max(1, min(50, limit))
    url = (f"{API}?q={urllib.parse.quote(q)}&sort={sort}&order=desc"
           f"&per_page={limit}")
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "chiron-github-search"}
    token = env.get("GITHUB_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        data = _get(url, headers, timeout)
    except urllib.error.HTTPError as e:
        return {"query": q, "error": f"HTTP {e.code}", "repos": [],
                "note": "GitHub limiti/aeği (GITHUB_TOKEN ile limit yükselir)"}
    except Exception as e:  # noqa: BLE001 - ağ hatası zarifçe boş
        return {"query": q, "error": f"{type(e).__name__}: {e}", "repos": []}

    repos = []
    for it in data.get("items", []):
        repos.append({
            "full_name": it.get("full_name", ""),
            "stars": it.get("stargazers_count", 0),
            "language": it.get("language") or "",
            "license": _license(it),
            "updated": (it.get("pushed_at") or "")[:10],
            "archived": bool(it.get("archived")),
            "description": (it.get("description") or "")[:160],
            "url": it.get("html_url", ""),
        })
    return {"query": q, "count": len(repos), "repos": repos,
            "total_available": data.get("total_count", len(repos))}
