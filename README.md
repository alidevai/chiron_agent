# Otonom Uzmanlasan AI Agent Platformu

Bir AI agent'in (Claude Code) karsilastigi gorevlerde **uzman prosedurleri zorunlu
kilan**, eksik yeteneklerini fark edip **guvenli sandbox'ta test ederek** ve
**politika kapilarindan gecirerek** kendi yetenek kutuphanesine kontrollu bicimde
ekleyen calisir bir sistem.

Tasarim gerekcesi: [otonom_uzmanlasan_ai_agent_skills_mcp_mimarisi.md](otonom_uzmanlasan_ai_agent_skills_mcp_mimarisi.md)
Agent calisma kurallari: [CLAUDE.md](CLAUDE.md)

## Ana ilke

> Agent arastirmada ve sandbox testinde otonomdur; kalici kurulum, genis yetki,
> production degisikligi ve canli trading deny-by-default ve onay kontrollüdur.

Uc katmanli davranis:
1. **Bilineni dogru yap** — dogrulanmis skill/tool kullan.
2. **Eksik yetenegi guvenli edin** — arastir, tara, sandbox'ta test et, politikaya gore ekle.
3. **Yeni uzmanlik uret** — skill yoksa birincil kaynaklardan uret, evaluator ile dogrula.

## Kurulum

```bash
pip install -r requirements.txt
python -m core init      # dizinler, politika muhru, seed skill kayitlari
python -m core verify    # audit zinciri + politika butunlugu
pytest -q                # 34 cekirdek testi
```

## Bilesenler

| Katman | Konum | Islev |
|---|---|---|
| Anayasal politika | `policies/immutable-core.yaml` | Agent'in degistiremeyecegi sinirlar (muhurlu) |
| Politika motoru | `core/policy.py` | Deny-by-default, risk temelli karar |
| Statik tarayici | `core/scanner.py` | Prompt injection / exfiltration / pipe-to-shell tespiti |
| Registry | `core/registry.py` | SQLite surumlu yetenek katalogu |
| Sandbox | `core/sandbox.py` | Tasinabilir surec izolasyonu (temiz env, ag kapali) |
| Guven skoru | `core/confidence.py` | Kanita dayali yetkinlik acigi olcumu |
| Eval runner | `core/evals.py` | Olculebilir dogrulama testleri |
| Pipeline | `core/lifecycle.py` | stage -> eval -> promote -> approve/revoke |
| Audit | `core/audit.py` | Hash-zincirli, degistirilemez denetim kaydi |
| Ogrenme | `core/learning.py` | Token-verimli ders defteri (ponytail felsefesi) |
| Guard hook | `core/guard_hook.py` | Claude Code PreToolUse anayasal koruma |

## Guvenlik ozeti

- Internetten bulunan hicbir skill/MCP **dogrudan kurulmaz**; kesif -> tarama ->
  bagimsiz guvenlik incelemesi -> sandbox eval -> politika karari zorunludur.
- Kritik bulgulu aday **otomatik reddedilir**.
- Isi yapan/bulan agent, ayni isin **nihai onaylayicisi olamaz** (ayri subagent'lar).
- `approve` ve `seal-policy` yalnizca **insan** tarafindan calistirilir; guard hook
  agent'i engeller.
- Token verimliligi (ponytail): gereksiz kod/bagimlilik/skill eklenmez; ogrenme
  context'i sismeden, kucuk dersler ve leksikal geri cagirma ile yapilir.
