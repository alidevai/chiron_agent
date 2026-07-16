---
name: skill-creator-safe
description: Aranan skill guvenilir kaynaklarda bulunamazsa, birincil kaynaklardan (resmi dokumantasyon, standartlar, akademik makaleler) yeni bir skill uretme prosedurudur. Uretilen skill her zaman experimental baslar ve normal edinme akisindaki tarama/eval/onay kapilarindan gecer.
version: 1.0.0
risk_level: medium
---

# Skill Creator (Safe)

Hazir skill bulunamadiginda son caredir. Agent yalnizca kendi genel bilgisine
dayanarak YUKSEK RISKLI skill uretmez; birincil kaynaklara dayanir.

## Kaynak onceligi (zorunlu)

1. Resmi dokumantasyon
2. Standartlar (RFC, spec, resmi rehber)
3. Akademik makaleler
4. Guvenilir acik kaynak projelerin kodu
5. Alan uzmanlarinin iyi bilinen rehberleri
6. Projenin kendi kurallari

Her prosedur adimi en az bir kaynaga baglanmalidir. Kaynaksiz "genel bilgi"
yuksek riskli alanlarda (finans, guvenlik, saglik) tek basina yeterli degildir.

## Uretim akisi

```
Alan arastirmasi -> birincil kaynak toplama -> uzman is akisi cikarma
  -> SKILL.md taslagi -> ornekler + karsi ornekler -> test fixture'lari
  -> evals/<id>.yaml -> staging'e alma -> tarama -> eval -> experimental kayit
```

## Uretilen SKILL.md sablonu

Her uretilen skill su bolumleri icermelidir:

```markdown
---
name: <ad>
version: 0.1.0
status: experimental
description: <ne zaman, hangi amacla>
domains: [<alan>]
risk_level: <low|medium|high>
required_tools: [...]
allowed_permissions: [...]
forbidden_permissions: [...]
sources:
  - url: <birincil kaynak>
    type: official_documentation
evaluation_suite: evals/<ad>.yaml
---

# Amac
# Kullanim kosullari
# Kullanilmamasi gereken durumlar
# On kosullar
# Zorunlu prosedur
# Kalite kapilari
# Guvenlik kurallari
# Hata durumlari
# Cikti formati
# Ornekler
# Testler
# Kaynaklar
```

## Uretim sonrasi (atlanmaz)

1. `evals/<id>.yaml` olustur: en az bir olculebilir kontrol (frontmatter, guvenlik
   taramasi, mumkunse calisan bir ornek).
2. `python -m core stage <taslak-dizin> --id <ad> --risk <seviye> --source generated`
3. `security-gatekeeper` ve `evaluator` subagent'larindan bagimsiz inceleme al.
4. `python -m core eval <id>` -> gecerse sandbox-validated.
5. Uretimi yapan agent nihai onaylayici DEGILDIR; promote/approve akisina birak.

## Olgunluk seviyeleri

```
experimental -> sandbox-validated -> project-approved -> production-approved
```
Her yeni uretilen skill `experimental` baslar; kullanim ve dogrulama ile terfi eder.

## Kaynaklar

- Ilgili: [[secure-capability-acquisition]], [[capability-gap-analysis]]
