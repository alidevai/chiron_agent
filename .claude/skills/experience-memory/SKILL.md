---
name: experience-memory
description: Token-verimli kendi kendine ogrenme. Goreve baslarken gecmis dersleri leksikal olarak geri cagirir (yalnizca en ilgili 3-5 kisa ders enjekte edilir); gorev bitince genellenebilir, tekrar eden bir ders cikarsa kaydeder. Amac, transkriptleri context'e doldurmadan deneyimden ogrenmektir.
version: 1.0.0
risk_level: low
---

# Experience Memory (token-verimli ogrenme)

Bu skill, sistemin deneyimden ogrenmesini saglar AMA token patlamasina yol acmaz.
Butun sir sudur: **ogrenme deterministik Python'da saklanir; LLM'e yalnizca kucuk,
kirpik dersler enjekte edilir.**

## Neden token-verimli?

- Depolama ve geri cagirma `python -m core learn` (SQLite) ile yapilir -> LLM token'i 0.
- Bir ders ~1-2 satirdir; transkript, uzun aciklama, kod bloklari SAKLANMAZ.
- Geri cagirma leksikaldir (kelime ortusmesi); embedding API'si yok, ek maliyet yok.
- Goreve en fazla 5 ilgili ders enjekte edilir (progressive disclosure). Tum ders
  defteri asla context'e yuklenmez.
- Anti-bloat: benzer ders tekrar eklenince yeni satir acilmaz, mevcut dersin sayaci
  artar. Boylece defter kucuk kalir ve her gorevde az token tuketir.

## Gorev BASINDA (recall)

Gorevin alanini ve anahtar kelimelerini belirle, sonra:
```
python -m core learn recall --domain <alan> --query "anahtar kelimeler" --k 5
```
Donen 0-5 dersi kisaca dikkate al. Ders yoksa hicbir sey enjekte etme (sifir maliyet).
Bunu `capability-gap-analysis` ile ayni anda yap (gorev acilis ritueli).

## Gorev SONUNDA (distill) — ama her zaman degil

Ders eklemeden once ponytail sorusunu sor (bkz. [[minimalist-engineering]]):
**"Bu gercekten yeni, genel ve tekrar edecek bir ders mi?"** Degilse ekleme.

Bir ders yalnizca su kriterlerin HEPSI saglaninca eklenir:
- Ayni/benzer gorev tekrar edebilir
- Prosedur genel ve tasinabilir (projeye/sirra ozel degil)
- Basari veya basarisizlik acik bir ogrenim veriyor
- Kullaniciya ozel sir/veri icermiyor

Eklerken kisa tut:
```
python -m core learn add "KURAL (1-2 cumle)" --domain <alan> \
    --trigger "ne zaman gecerli" --why "gerekce"
```

## Pekistirme ve terfi

- Bir ders bir gorevde ise yaradiysa/yaramadiysa:
  `python -m core learn reinforce <id> win|loss`
- Bir ders yeterince tekrar edip (uses >= 3) net pozitifse skill adayidir:
  `python -m core learn promotion-candidates`
  Bu adaylari `skill-creator-safe` ile tam skill'e donustur. Boylece defter degil,
  yalnizca KANITLANMIS tekrar eden desenler kalici skill olur (context sismesini onler).
- Periyodik temizlik: `python -m core learn prune` (kullanilmayan dersleri budar).

## Kullanilmamasi gereken durum

- Tek seferlik, onemsiz gorevlerde ders ekleme; defteri gurultuye bogar.
- Uzun metin/transkript kaydetme; ders tek satirlik kural olmalidir.

## Kaynaklar

- Motor: core/learning.py
- Ilgili: [[minimalist-engineering]], [[capability-gap-analysis]], [[skill-creator-safe]]
