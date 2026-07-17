"""backlog.py — insan gorev kuyrugu / operator konsolu testleri.

AI'in insana biraktigi isleri kalici karta yazma (request_human), toplama
(collect), render ve arsivleme (resolve) davranislarini izole platformda dogrular.
"""
from __future__ import annotations

from core import backlog
from core.registry import Registry


def test_request_human_writes_card(platform):
    card = backlog.request_human(
        platform, "Prod DB index", category="deploy",
        why="AI production'a yazamaz", action="DBA uygular", risk="high")
    assert card["category"] == "deploy" and card["risk"] == "high"
    f = platform.human_pending / f"{card['id']}.md"
    assert f.exists()
    text = f.read_text(encoding="utf-8")
    assert "AI production'a yazamaz" in text
    assert "DBA uygular" in text


def test_invalid_category_falls_back(platform):
    card = backlog.request_human(platform, "X", category="uydurma")
    assert card["category"] == "other"


def test_collect_aggregates_all_sources(platform):
    backlog.request_human(platform, "Bir insan isi", category="infra")
    data = backlog.collect(platform)
    assert data["counts"]["agent_tasks"] == 1
    assert data["counts"]["deferred_infra"] >= 4      # statik ertelenen altyapi
    assert "capability_approvals" in data
    assert "stale_revalidation" in data


def test_deferred_infra_always_present(platform):
    # hic gorev yokken bile ertelenen altyapi kullaniciya gosterilir
    data = backlog.collect(platform)
    titles = [d["title"] for d in data["deferred_infra"]]
    assert any("sandbox" in t.lower() for t in titles)


def test_render_markdown_sections(platform):
    backlog.request_human(platform, "Gorunur is", category="policy")
    md = backlog.render_markdown(backlog.collect(platform))
    assert "# İnsan Görev Kuyruğu" in md
    assert "Gorunur is" in md
    assert "Bilinçli ertelenen" in md


def test_resolve_archives_task(platform):
    card = backlog.request_human(platform, "Cozulecek is")
    assert (platform.human_pending / f"{card['id']}.md").exists()
    assert backlog.resolve(platform, card["id"]) is True
    assert not (platform.human_pending / f"{card['id']}.md").exists()
    assert (platform.human_decided / f"{card['id']}.md").exists()
    # ikinci kez cozme -> False
    assert backlog.resolve(platform, card["id"]) is False


def test_stale_appears_in_backlog(platform):
    reg = Registry(platform.registry_db)
    reg.add("eski-skill", "1.0.0", status="project-approved", risk_level="low",
            source="seed", scan_score=100)
    # last_validated_at gecmise cek -> stale
    reg._conn.execute(
        "UPDATE capabilities SET last_validated_at=?, updated_at=? WHERE id=?",
        ("2020-01-01T00:00:00", "2020-01-01T00:00:00", "eski-skill"))
    reg._conn.commit()
    reg.close()
    data = backlog.collect(platform)
    assert any(s["id"] == "eski-skill" for s in data["stale_revalidation"])


def test_write_backlog_creates_file(platform):
    data = backlog.write_backlog(platform)
    assert platform.human_backlog.exists()
    assert data["backlog_file"] == str(platform.human_backlog)
