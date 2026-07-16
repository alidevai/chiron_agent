from core.audit import AuditLog


def test_chain_append_and_verify(platform):
    log = AuditLog(platform.audit_log)
    log.append("test", "a", {"x": 1})
    log.append("test", "b", {"y": 2})
    ok, msg = log.verify()
    assert ok, msg


def test_tamper_breaks_chain(platform):
    log = AuditLog(platform.audit_log)
    log.append("test", "a", {"x": 1})
    log.append("test", "b", {"y": 2})
    # bir satiri elle boz
    lines = platform.audit_log.read_text(encoding="utf-8").splitlines()
    lines[0] = lines[0].replace('"x": 1', '"x": 999')
    platform.audit_log.write_text("\n".join(lines) + "\n", encoding="utf-8")
    ok, msg = log.verify()
    assert not ok
    assert "degistiril" in msg or "zincir" in msg


def test_tail(platform):
    log = AuditLog(platform.audit_log)
    for i in range(5):
        log.append("test", f"e{i}")
    tail = log.tail(3)
    assert len(tail) == 3
    assert tail[-1]["action"] == "e4"
