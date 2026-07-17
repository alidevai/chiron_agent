"""github_search.py — GitHub kütüphane arama aracı (network MOCK'lu).

Gerçek API çağrısı yapılmaz; `_get` monkeypatch'lenir. Sorgu kurulumu, dil filtresi,
sonuç şekli, lisans çıkarımı ve hata/zarif-boş davranışı doğrulanır.
"""
from __future__ import annotations

import urllib.error

from core import github_search as ghs


def _fake_items():
    return {"total_count": 2, "items": [
        {"full_name": "mrdoob/three.js", "stargazers_count": 113000, "language": "JavaScript",
         "license": {"spdx_id": "MIT"}, "pushed_at": "2026-07-16T10:00:00Z",
         "archived": False, "description": "JavaScript 3D library", "html_url": "https://github.com/mrdoob/three.js"},
        {"full_name": "old/dead", "stargazers_count": 10, "language": "JavaScript",
         "license": None, "pushed_at": "2018-01-01T00:00:00Z", "archived": True,
         "description": None, "html_url": "https://github.com/old/dead"},
    ]}


def test_search_shape(monkeypatch):
    monkeypatch.setattr(ghs, "_get", lambda url, headers, timeout: _fake_items())
    res = ghs.search_repos("3d webgl", language="JavaScript", limit=5, env={})
    assert res["count"] == 2
    r0 = res["repos"][0]
    assert r0["full_name"] == "mrdoob/three.js"
    assert r0["stars"] == 113000
    assert r0["license"] == "MIT"
    assert r0["updated"] == "2026-07-16"
    assert r0["archived"] is False
    # ikinci: lisans yok, arşivli
    assert res["repos"][1]["license"] == ""
    assert res["repos"][1]["archived"] is True


def test_language_and_query_in_url(monkeypatch):
    captured = {}
    monkeypatch.setattr(ghs, "_get",
                        lambda url, headers, timeout: (captured.update(url=url, headers=headers) or _fake_items()))
    ghs.search_repos("pdf extraction", language="Python", env={})
    assert "language%3APython" in captured["url"] or "language:Python" in captured["url"]
    assert "sort=stars" in captured["url"]


def test_token_sets_auth_header(monkeypatch):
    captured = {}
    monkeypatch.setattr(ghs, "_get",
                        lambda url, headers, timeout: (captured.update(headers=headers) or _fake_items()))
    ghs.search_repos("x", env={"GITHUB_TOKEN": "ghp_test1234"})
    assert captured["headers"].get("Authorization") == "Bearer ghp_test1234"


def test_no_token_no_auth(monkeypatch):
    captured = {}
    monkeypatch.setattr(ghs, "_get",
                        lambda url, headers, timeout: (captured.update(headers=headers) or _fake_items()))
    ghs.search_repos("x", env={})
    assert "Authorization" not in captured["headers"]


def test_http_error_graceful(monkeypatch):
    def boom(url, headers, timeout):
        raise urllib.error.HTTPError(url, 403, "rate limited", {}, None)
    monkeypatch.setattr(ghs, "_get", boom)
    res = ghs.search_repos("x", env={})
    assert res["repos"] == []
    assert "403" in res["error"]


def test_network_error_graceful(monkeypatch):
    def boom(url, headers, timeout):
        raise TimeoutError("ağ yok")
    monkeypatch.setattr(ghs, "_get", boom)
    res = ghs.search_repos("x", env={})
    assert res["repos"] == []
    assert "TimeoutError" in res["error"]


def test_limit_clamped(monkeypatch):
    captured = {}
    monkeypatch.setattr(ghs, "_get",
                        lambda url, headers, timeout: (captured.update(url=url) or _fake_items()))
    ghs.search_repos("x", limit=999, env={})
    assert "per_page=50" in captured["url"]   # üst sınır 50
