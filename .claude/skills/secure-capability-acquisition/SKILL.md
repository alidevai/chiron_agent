---
name: secure-capability-acquisition
description: Eksik bir skill/MCP/tool'u guvenli sekilde edinme prosedurunun tam akisi. "Hemen bulup kur" yerine "hemen arastir, hemen sandbox'a al, hemen test et, risk uygunsa ekle; degilse onay iste veya reddet" ilkesini uygular. Yeni bir yetenek kurulmasi gerektiginde kullanilir.
version: 1.0.0
risk_level: medium
---

# Secure Capability Acquisition Pipeline

Platformun en kritik guvenlik akisidir. Internette bulunan HICBIR skill veya MCP
dogrudan kurulmaz. Agent arastirmada ve sandbox testinde otonomdur; kalici
kurulumda politika ve insan onayina tabidir.

## Zorunlu akis (asla atlanmaz)

```
1. Ihtiyac dogrulama    -> gercekten yeni yetenek mi gerekli?
2. Kesif + puanlama     -> capability-manager subagent (kaynak oncelikli arama)
3. Staging + statik tarama -> python -m core stage ...   (kritik bulgu = otomatik red)
4. Bagimsiz guvenlik    -> security-gatekeeper subagent  (kor, dusmanca inceleme)
5. Sandbox eval         -> python -m core eval <id>       (olculebilir testler)
6. Politika karari      -> python -m core promote <id>
                            - allow            -> otomatik kurulur (yalnizca dusuk risk)
                            - require_approval -> onay paketi olusur -> INSAN
                            - deny             -> reddedilir
7. Kurulum sonrasi      -> registry'de izlenir, periyodik yeniden dogrulanir
```

## Adim adim

### 1. Ihtiyac dogrulama
Once sor: Mevcut bir skill parametre/ornek eklenerek yeterli olur mu? Ihtiyac tek
seferlik mi (o zaman kalici kurulum yerine tek seferlik sandbox kullanimi)? Yeni
bagimlilik teknik borc yaratir mi? Cevap "yeni yetenek gerekli" ise devam et.

### 2. Kesif ve puanlama
`capability-manager` subagent'ini cagir. O, kaynak oncelik sirasiyla (resmi repo
> dogrulanmis koleksiyon > buyuk kurum > akademik > topluluk listesi > genel arama
> kendin uret) aday bulur, 100 uzerinden puanlar ve en iyisini staging'e alir.

### 3. Staging + statik tarama
```
python -m core stage <indirilen-dizin> --id <ad> --risk <seviye> \
    --domains <alan1,alan2> --source <kaynak-url>
```
Tarama otomatik calisir. Kritik bulgu (prompt injection, exfiltration, pipe-to-shell,
audit/policy kurcalama...) varsa aday ANINDA reddedilir ve registry'ye revoked yazilir.

### 4. Bagimsiz guvenlik incelemesi
`security-gatekeeper` subagent'ini cagir. Makine taramasi tek basina yeterli
degildir; gatekeeper dosyalari insan gibi okur, izin manifesti cikarir, en kotu
senaryoyu tanimlar. REJECT verirse dur.

### 5. Sandbox eval
```
python -m core eval <id>
```
Eval skoru >= 0.90 ve kritik hata = 0 olmali. Gecerse durum otomatik
`sandbox-validated` olur.

### 6. Politika karari
```
python -m core promote <id>
```
- **allow**: yalnizca dusuk riskli, ag erisimsiz, salt-okunur yetenekler.
  Otomatik `.claude/skills/` altina kurulur.
- **require_approval**: orta/yuksek risk. `approvals/pending/<id>.md` onay paketi
  olusur. Kullaniciya bu paketi ozetle ve `python -m core approve <id> --by "AD"`
  komutunu INSANIN interaktif terminalde calistirmasi gerektigini soyle.
  Sen (agent) bu komutu calistiramazsin; guard hook engeller.
- **deny**: kritik risk. Reddedilir.

## Kesin kurallar

- Staging'deki hicbir sey aktif degildir; yalnizca `.claude/skills/` altindakiler yuklenır.
- Indirilen kod yalnizca `sandbox-run` / `eval` uzerinden calistirilir, dogrudan degil.
- Yuksek riskli yetenegi ureten/bulan agent, kendi guvenlik onayini VEREMEZ.
- Emin degilsen reddet (fail-closed).

## Kaynaklar

- Pipeline: core/lifecycle.py, core/scanner.py
- Ilgili: [[capability-gap-analysis]], [[mcp-security-review]], [[skill-creator-safe]]
