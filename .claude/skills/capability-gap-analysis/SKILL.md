---
name: capability-gap-analysis
description: Bir goreve baslamadan once yetkinlik acigini ve guven skorunu olcer; eksik olanin bilgi mi, skill mi, tool mu oldugunu ayirir ve sonraki adimi (dogrudan yurut / dogrulayarak yurut / yetenek edin) belirler. Yuksek riskli, belirsiz veya "en guncel/en iyi/dogrula" istenen gorevlerde ilk adim olarak kullanilir.
version: 1.0.0
risk_level: low
---

# Capability Gap Analysis

Bu skill, "her seyi bildigini varsayan" davranisin panzehiridir. Goreve dalmadan
once sistemin o gorev icin gercekten hazir olup olmadigini kanitla olcer.

## Ne zaman kullanilir

Su durumlardan HERHANGI biri varsa, koda/analize baslamadan once bunu calistir:
- Alan yuksek riskli: finans, trading, guvenlik, saglik, hukuk
- Kullanici "en guncel", "en iyi", "dogrula", "emin ol" diyor
- Gorev mevcut skill'lerin acikca kapsami disinda
- Kullanilacak kutuphane/standart guncel olmayabilir
- Ayni hata tekrar ediyor veya bir tool cagrisi iki kez basarisiz oldu
- Kullanici ozel/bilinmeyen bir teknoloji, format veya sistem istiyor

## Prosedur

1. **Gorevi alanlara ayir.** task_domain ve task_subdomains cikar.
   Ornek: "Solidity kontrati guvenlik incelemesi" ->
   domain=security, subdomains=[solidity, smart-contract, static-analysis]

2. **Gerekli yetenekleri listele.** Hangi prosedurler (skill), hangi araclar
   (tool/MCP), hangi veri kaynaklari gerekiyor? Somut skill id'leri olarak yaz.

3. **Gap raporunu calistir:**
   ```
   python -m core gap --domain <alan> --skills <id1,id2,id3> --risk <low|medium|high|critical>
   ```
   Cikti: existing / missing / stale yetenekler, confidence (0-1), action.

4. **Action'a gore yonlen:**
   - `proceed` (confidence >= 0.75, eksik yok): dogrudan mevcut skill'lerle yurut.
   - `proceed_with_verification` (0.60-0.75): yurut, ama sonucu `evaluator`
     subagent'ina bagimsiz dogrulat. Yuksek riskte bu zorunludur.
   - `research_and_stage_capability` (< 0.60 veya eksik var): `capability-manager`
     subagent'ini cagirarak eksik yetenegi guvenli sekilde edin (bkz.
     [[secure-capability-acquisition]]).

5. **Riske gore kapilar:**
   - risk high/critical ise: bagimsiz evaluator ZORUNLU.
   - Eylem geri donusu zor ise (production, email, trade, dosya silme): insan onayi.

## Kullanilmamasi gereken durumlar

- Onemsiz, tek seferlik, dusuk riskli gorevlerde (or. bir yazim hatasi duzeltme)
  bu analiz gereksiz surtunmedir; dogrudan yap.

## Cikti formati

Gorevin basinda kisa bir "hazirlik notu" ver: alan, gerekli yetenekler,
confidence skoru, secilen action ve gerekiyorsa hangi subagent'in cagrilacagi.

## Kaynaklar

- Platform gap motoru: core/confidence.py
- Ilgili: [[secure-capability-acquisition]], [[skill-router]]
