from core.confidence import assess
from core.registry import Registry


def test_registry_lifecycle(platform):
    reg = Registry(platform.registry_db)
    reg.add("s1", "0.1.0", status="experimental", domains=["x"])
    assert reg.latest("s1")["status"] == "experimental"
    reg.set_status("s1", "sandbox-validated")
    assert reg.latest("s1")["status"] == "sandbox-validated"
    reg.set_validation("s1", 0.95)
    assert reg.latest("s1")["validation_score"] == 0.95
    reg.close()


def test_search_active_only(platform):
    reg = Registry(platform.registry_db)
    reg.add("active-one", status="project-approved", domains=["fin"])
    reg.add("exp-one", status="experimental", domains=["fin"])
    active = reg.search(domain="fin", active_only=True)
    ids = {r["id"] for r in active}
    assert "active-one" in ids
    assert "exp-one" not in ids
    reg.close()


def test_confidence_missing_skill_triggers_research(platform):
    reg = Registry(platform.registry_db)
    report = assess(reg, domain="security",
                    required_skills=["nonexistent-skill"], risk_level="high")
    assert report.missing == ["nonexistent-skill"]
    assert report.action == "research_and_stage_capability"
    assert report.confidence < 0.6
    reg.close()


def test_confidence_high_when_all_present(platform):
    reg = Registry(platform.registry_db)
    reg.add("a", status="project-approved")
    reg.set_validation("a", 1.0)
    reg.add("b", status="production-approved")
    reg.set_validation("b", 1.0)
    report = assess(reg, domain="software",
                    required_skills=["a", "b"], risk_level="low")
    assert not report.missing
    assert report.confidence >= 0.75
    assert report.action == "proceed"
    reg.close()
