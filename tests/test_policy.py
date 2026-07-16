from core.policy import ALLOW, DENY, REQUIRE_APPROVAL, PolicyEngine


def test_integrity_ok(platform):
    ok, msg = PolicyEngine(platform).verify_integrity()
    assert ok, msg


def test_tampered_immutable_fails_closed(platform):
    # muhur sonrasi dosyayi degistir -> her sey deny
    text = platform.immutable_core.read_text(encoding="utf-8")
    platform.immutable_core.write_text(text + "\n# sinsi ekleme\n", encoding="utf-8")
    eng = PolicyEngine(platform)
    ok, _ = eng.verify_integrity()
    assert not ok
    d = eng.decide("research")  # normalde allow
    assert d.effect == DENY
    assert "fail-closed" in d.reason


def test_default_deny(platform):
    d = PolicyEngine(platform).decide("bilinmeyen_eylem")
    assert d.effect == DENY
    assert d.rule_id == "default"


def test_research_allowed(platform):
    d = PolicyEngine(platform).decide("research")
    assert d.effect == ALLOW


def test_forbidden_action_denied(platform):
    for action in ("modify_policy", "broker_withdrawal", "disable_audit",
                   "change_own_risk_limits", "push_main_direct"):
        d = PolicyEngine(platform).decide(action)
        assert d.effect == DENY
        assert d.rule_id == "immutable"


def test_install_low_risk_needs_conditions(platform):
    eng = PolicyEngine(platform)
    # kosullar saglanmadan low risk install -> fail-closed deny
    d = eng.decide("install_capability", "low", {})
    assert d.effect == DENY
    assert d.missing_conditions
    # kosullar saglaninca -> allow
    d2 = eng.decide("install_capability", "low",
                    {"security_scan_passed": True, "sandbox_eval_passed": True})
    assert d2.effect == ALLOW


def test_install_medium_requires_approval(platform):
    d = PolicyEngine(platform).decide(
        "install_capability", "medium",
        {"security_scan_passed": True, "sandbox_eval_passed": True})
    assert d.effect == REQUIRE_APPROVAL


def test_install_critical_denied(platform):
    d = PolicyEngine(platform).decide(
        "install_capability", "critical",
        {"security_scan_passed": True, "sandbox_eval_passed": True})
    assert d.effect == DENY


def test_trading_live_requires_approval_and_conditions(platform):
    eng = PolicyEngine(platform)
    d = eng.decide("live_trade", "high", {})
    # human_approval_always + eksik kosullar -> require_approval (onaya cikar,
    # kosullar onay asamasinda doldurulur)
    assert d.effect == REQUIRE_APPROVAL


def test_withdrawal_denied(platform):
    d = PolicyEngine(platform).decide("withdrawal")
    assert d.effect == DENY
