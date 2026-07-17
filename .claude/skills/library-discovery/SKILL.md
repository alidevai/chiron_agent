---
name: library-discovery
description: Bir yazılım/tasarım/teknik iş kurmadan önce "bu iş için en iyi kütüphane/araç/framework hangisi?" diye GitHub'ı sorgulayıp aday keşfetme ve seçme prosedürü. Kod yazmadan önce, sıfırdan çözmek yerine olgun bir kütüphane var mı diye bakar (ör. 3D için three.js). Yıldız, bakım, lisans ve göreve uygunlukla değerlendirip gerekçeyle seçer. Yazılım/frontend/3D/veri/ML gibi işlerde plan aşamasında uygulanır.
version: 1.0.0
risk_level: low
---

# Library / Tool Discovery (GitHub)

"Bildiğim kütüphaneyle başla" değil, "bu iş için EN İYİ kütüphane hangisi" diye sor.
Kod yazmadan önce GitHub'ı deterministik sorgula; olgun bir çözüm varsa onu kullan
(ör. 3D grafik için three.js), yoksa üret. Bu, `prior-art-research`'ün teknoloji
tarafıdır; tasarım/UX örnekleri için onu, kütüphane seçimi için bunu kullan.

## Ne zaman uygulanır
Yazılım/frontend/3D/oyun/veri/ML/otomasyon işine başlarken, plan aşamasında.
Küçük mekanik düzeltmede gerekmez (ponytail).

## Nasıl (sistem GitHub'ı sorgular)
İhtiyacı bir arama sorgusuna çevir ve çalıştır:
```
python -m core github-search "3d rendering webgl" --lang JavaScript --limit 8
python -m core github-search "pdf table extraction" --lang Python
```
Çıktı her aday için: `full_name`, `stars`, `license`, `updated` (son push),
`archived`, `language`, kısa açıklama, url.

## Değerlendirme (aday seçimi)
Adayları şu ölçütlerle tart (yalnız yıldız değil):
- **Uygunluk:** göreve gerçekten cevap veriyor mu? (kapsam, özellikler)
- **Bakım:** `updated` yakın mı, `archived` değil mi? (ölü repo elenir)
- **Olgunluk/güven:** yıldız + kullanım yaygınlığı (tek başına yeterli değil).
- **Lisans:** projeyle uyumlu mu? (MIT/Apache/BSD serbest; GPL/ticari-kısıt dikkat).
- **Ağırlık/bağımlılık:** ponytail — en hafif yeterli çözüm; stdlib yetiyorsa onu seç.
- **Belgeler/topluluk:** dokümantasyon, örnek, issue yanıt hızı (gerekirse `context7`
  ile güncel doküman çek, `ai-council` ile ikinci görüş al).

## İki ayrı yol (KARIŞTIRMA)
- **İş için kütüphane** (ör. three.js): dış projede DOĞRUDAN kullan; Chiron'a
  skill olarak kurmana gerek yok. Yerel/offline gerekiyorsa vendor'la (indir, yerelde tut).
- **Yeniden kullanılabilir YETENEK** (skill/MCP/tool) Chiron'a eklenecekse: doğrudan
  kurma; `capability-manager` + `secure/auto-capability-acquisition` hattından
  (tara -> eval -> politika) geçir.

## Çıktı (plana yansıt)
```
LIBRARY DISCOVERY
İhtiyaç: ...
Adaylar: (full_name — stars — license — updated — 1 satır uygunluk)
SEÇİM: <repo>  — gerekçe (uygunluk + bakım + lisans + ağırlık)
Kullanım biçimi: doğrudan / vendor (offline) / acquisition-pipeline (skillse)
```

## İlkeler
- Yıldız tek başına kalite değildir; bakım + lisans + uygunluk birlikte bakılır.
- Arşivli/terk edilmiş repoyu seçme.
- Lisans uyumunu doğrula (ticari/telif).
- İlgili: `prior-art-research` (tasarım/örnek), `software-lifecycle` (plan),
  `capability-gap-analysis`, `secure-capability-acquisition` (skill edinme).
