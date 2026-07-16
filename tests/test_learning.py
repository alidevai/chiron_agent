from core.learning import LessonStore


def _store(platform):
    return LessonStore(platform.lessons_db)


def test_add_and_recall(platform):
    s = _store(platform)
    s.add("Windows'ta subprocess'e liste ver, shell=True kullanma",
          domain="python", trigger="subprocess cagrisi",
          rationale="shell injection ve tirnak sorunlari")
    hits = s.recall(query="python subprocess windows", domain="python")
    assert hits
    assert "subprocess" in hits[0].render().lower()
    s.close()


def test_dedup_merges_similar(platform):
    s = _store(platform)
    r1 = s.add("Backtest'te look-ahead icin gelecek bar erisimini tara",
               domain="trading")
    r2 = s.add("Backtest look-ahead: gelecek bar erisimi taranmali",
               domain="trading")
    assert r1["merged"] is False
    assert r2["merged"] is True          # benzer -> birlestirildi
    assert r2["uses"] == 2
    # tek satir kalmali (anti-bloat)
    assert len([x for x in s.list() if x["status"] != "pruned"]) == 1
    s.close()


def test_recall_budget_k(platform):
    s = _store(platform)
    for i in range(10):
        s.add(f"security kural {i} sql injection input validation", domain="security",
              trigger=f"case{i}")
    hits = s.recall(query="security sql injection", domain="security", k=3)
    assert len(hits) <= 3                 # butce siniri
    s.close()


def test_reinforce_and_autoprune(platform):
    s = _store(platform)
    r = s.add("supheli ders", domain="x")
    lid = r["id"]
    for _ in range(3):
        s.reinforce(lid, "loss")
    row = [x for x in s.list() if x["id"] == lid][0]
    assert row["status"] == "pruned"      # net cok negatif -> otomatik budandi
    # budanmis ders recall'da gelmez
    assert all(h.id != lid for h in s.recall(query="supheli", domain="x"))
    s.close()


def test_promotion_gate(platform):
    s = _store(platform)
    r = s.add("tekrar eden faydali ders refactor test", domain="software")
    lid = r["id"]
    # 2 kez daha ayni ders -> uses=3
    s.add("tekrar eden faydali ders refactor test", domain="software")
    s.add("tekrar eden faydali ders refactor test", domain="software")
    s.reinforce(lid, "win")
    cands = s.promotion_candidates(min_uses=3)
    assert any(c["id"] == lid for c in cands)   # frekans kapisini gecti
    # tek kullanimlik ders aday olmamali
    s.add("tek seferlik alakasiz ders", domain="misc")
    cands2 = s.promotion_candidates(min_uses=3)
    assert all(c["rule"] != "tek seferlik alakasiz ders" for c in cands2)
    s.close()


def test_negative_lesson_not_recalled(platform):
    s = _store(platform)
    r = s.add("kotu tavsiye", domain="z")
    s.reinforce(r["id"], "loss")
    s.reinforce(r["id"], "loss")
    # wins=0 losses=2 -> net negatif, recall'da gizli
    assert all(h.id != r["id"] for h in s.recall(query="kotu tavsiye", domain="z"))
    s.close()
