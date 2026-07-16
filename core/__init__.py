"""Otonom uzmanlasan AI agent platformu - Python cekirdegi.

Katmanlar:
  paths       - dizin yerlesimi
  audit       - hash-zincirli audit log
  policy      - deny-by-default politika motoru + anayasal butunluk
  scanner     - statik guvenlik tarayicisi (skill/MCP adaylari)
  registry    - SQLite surumlu yetenek katalogu
  sandbox     - tasinabilir surec izolasyonu
  confidence  - kanita dayali guven skoru / gap raporu
  evals       - olculebilir dogrulama testleri
  lifecycle   - stage -> eval -> promote -> approve/revoke orkestrasyonu
  guard_hook  - Claude Code PreToolUse anayasal koruma
"""
__version__ = "1.0.0"
