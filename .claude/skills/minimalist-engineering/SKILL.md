---
name: minimalist-engineering
description: Ponytail felsefesi — "en iyi kod, hic yazmadigin koddur." Kod yazmadan, bagimlilik eklemeden veya yeni yetenek kurmadan ONCE uygulanan karar merdiveni. Asiri muhendisligi ve gereksiz token/maliyet israfini onler. Guvenlik, hata yonetimi ve dogrulamadan ASLA odun vermez.
version: 1.0.0
risk_level: low
---

# Minimalist Engineering (Ponytail felsefesi)

Kaynak felsefe: https://github.com/DietrichGebert/ponytail
Ozet: *"The best code is the code you never wrote."* Tembellik yalnizca gereksiz
karmasikliga uygulanir; problemi anlamaya, guvenlige ve dogrulamaya ASLA uygulanmaz.

## Karar merdiveni (kod/bagimlilik/yetenek eklemeden ONCE)

Sirayla sor, ilk "evet"te dur:

1. **Bu gercekten var olmali mi?** Gereksizse hic yazma / kurma.
2. **Kod tabaninda zaten var mi?** Varsa yeniden yazma, tekrar kullan.
3. **Standart kutuphane karsiliyor mu?** Varsa built-in kullan.
4. **Native platform ozelligi var mi?** Varsa onu kullan.
5. **Kurulu bir bagimlilik cozuyor mu?** Yeni paket ekleme.
6. **Tek satirla olur mu?** Minimal tut.
7. **Ancak o zaman:** minimum uygulanabilir kodu yaz.

## Bu platformdaki baglantilar

- **Yetenek edinme**: [[secure-capability-acquisition]] Asama 1 (ihtiyac dogrulama)
  bu merdiveni kullanir. "Yeni MCP/skill kurmadan once: mevcut skill yeterli mi,
  tek seferlik mi, stdlib/CLI yeter mi?" Cogu zaman en iyi yetenek, KURULMAYAN yetenektir.
- **Ogrenme**: [[experience-memory]] ders eklemeden once "bu gercekten yeni ve genel
  bir ders mi?" diye sorar — defteri (ve gelecekteki her context'i) sismekten korur.
- **Skill uretimi**: [[skill-creator-safe]] son caredir; once hazir/mevcut aranir.

## Token/maliyet etkisi

Gereksiz kod, gereksiz bagimlilik ve gereksiz skill; hepsi gelecekteki her gorevde
context ve bakim maliyeti olarak geri doner. Az yazmak = az token = az hata yuzeyi.

## Guvenlik istisnasi (pazarliksiz)

Su alanlarda "minimal" gerekcesiyle atlama YAPILMAZ:
- Girdi dogrulama
- Hata yonetimi
- Guvenlik kontrolleri ve izin sinirlari
- Erisilebilirlik
- Audit ve geri alinabilirlik

Bunlar karmasiklik degil, dogru muhendisligin tabanidir.

## Cikti / davranis

Bir cozum onerirken, eklemedigin seyleri de kisaca belirt: "X kutuphanesi yerine
stdlib yeterliydi", "mevcut Y skill'i bu ihtiyaci karsiladi, yeni kurulum gereksiz."

## Kaynaklar

- Ilgili: [[secure-capability-acquisition]], [[experience-memory]], [[capability-gap-analysis]]
