"""audit.py — hash-zincirinin kurcalama tespiti ve BILINEN sinirlari.

Mevcut test_audit.py temel append/verify/in-place-tamper kapsiyor. Burada
saldiri modelini genisletiyoruz: satir silme, yeniden siralama, in-place
degisiklik YAKALANMALI; buna karsilik sondan-kirpma (truncation) ve tam
yeniden-zincirleme (re-forge) mevcut tasarimca YAKALANAMAZ — bu bosluklar
`xfail(strict)` ile acikca belgelenir (harici capa/imzali bas gerekir).

audit.py anayasal korumali; testler yalnizca mevcut davranisi kilitler.
"""
from __future__ import annotations

import json

import pytest

from core.audit import AuditLog


def _seed(path, n=4):
    log = AuditLog(path)
    for i in range(n):
        log.append("actor", "action", {"i": i})
    return log


def test_valid_chain_verifies(tmp_path):
    log = _seed(tmp_path / "audit.jsonl")
    ok, _ = log.verify()
    assert ok


def test_inplace_tamper_detected(tmp_path):
    p = tmp_path / "audit.jsonl"
    log = _seed(p)
    lines = p.read_text(encoding="utf-8").splitlines()
    rec = json.loads(lines[1])
    rec["details"] = {"i": 999}          # icerik degistir, hash'i birak
    lines[1] = json.dumps(rec, ensure_ascii=False)
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    ok, msg = log.verify()
    assert not ok


def test_middle_line_deletion_detected(tmp_path):
    p = tmp_path / "audit.jsonl"
    log = _seed(p)
    lines = p.read_text(encoding="utf-8").splitlines()
    del lines[1]                          # ortadan bir kayit sil -> zincir kirilir
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    ok, msg = log.verify()
    assert not ok
    assert "zincir" in msg or "hash" in msg


def test_reordering_detected(tmp_path):
    p = tmp_path / "audit.jsonl"
    log = _seed(p)
    lines = p.read_text(encoding="utf-8").splitlines()
    lines[1], lines[2] = lines[2], lines[1]   # iki kaydi yer degistir
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    ok, _ = log.verify()
    assert not ok


def test_corrupt_json_detected(tmp_path):
    p = tmp_path / "audit.jsonl"
    _seed(p)
    with p.open("a", encoding="utf-8") as f:
        f.write("{bozuk json\n")
    ok, msg = log = AuditLog(p).verify()
    assert not ok


def test_append_extends_chain(tmp_path):
    p = tmp_path / "audit.jsonl"
    log = _seed(p, 2)
    log.append("actor", "more", {})
    ok, _ = log.verify()
    assert ok
    assert len(log.tail(10)) == 3


# --- BILINEN sinirlar (harici capa olmadan yakalanamaz) ----------------------

@pytest.mark.xfail(reason="Bilinen sinir: sondan-kirpma (truncation) zinciri gecerli "
                          "birakir; tespit icin imzali/harici capalanan bas gerekir",
                   strict=True)
def test_truncation_detected(tmp_path):
    p = tmp_path / "audit.jsonl"
    log = _seed(p, 5)
    lines = p.read_text(encoding="utf-8").splitlines()
    p.write_text("\n".join(lines[:2]) + "\n", encoding="utf-8")  # son 3 kaydi at
    ok, _ = log.verify()
    assert not ok  # ideal: kirpma tespit edilmeli


@pytest.mark.xfail(reason="Bilinen sinir: saldirgan tum zinciri bastan yeniden "
                          "uretirse (re-forge) verify gecer; harici imza gerekir",
                   strict=True)
def test_full_reforge_detected(tmp_path):
    p = tmp_path / "audit.jsonl"
    _seed(p, 3)
    # Saldirgan gecmisi silip kendi tutarli zincirini kurar
    forged = AuditLog(p)
    p.write_text("", encoding="utf-8")
    forged.append("attacker", "planted", {"fake": True})
    ok, _ = forged.verify()
    assert not ok  # ideal: yeniden-uretim tespit edilmeli


def test_tail_returns_last_n(tmp_path):
    p = tmp_path / "audit.jsonl"
    log = _seed(p, 6)
    assert len(log.tail(3)) == 3
    assert log.tail(100)[-1]["details"]["i"] == 5
