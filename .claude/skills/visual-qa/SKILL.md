---
name: visual-qa
description: Görsel/arayüz işlerinde (web sayfası, UI bileşeni, grafik/chart, animasyon, 3D sahne, oyun) teslimi GÖRSEL KALİTEDEN geçirme prosedürü. "Bitti" demeden önce gerçek bir tarayıcıda (Chrome) RENDER edip ekran görüntüsü alarak GÖZLE incele; layout/kontrast/taşma/bozuk efekt/görünmezlik/konsol hatalarını yakala; düzelt; tekrar render et — görsel temiz olana kadar döngü. Sözdizim/test yeşil olması görsel kaliteyi GARANTİ ETMEZ.
version: 1.0.0
risk_level: low
---

# Visual QA — görsel kaliteden geçirme

Görsel bir işte `node --check` veya birim testinin geçmesi YETMEZ; ekranda gerçekten
nasıl göründüğü ayrı bir kanıttır. Bu skill, görsel teslimleri gerçek tarayıcıda
render edip ekran görüntüsünü GÖZLE inceleyerek doğrular ve kusurları döngüyle giderir.

## Ne zaman uygulanır
Herhangi bir görsel/arayüz çıktısında: web sayfası/site, UI bileşeni, grafik/chart,
dashboard, animasyon, 3D/WebGL sahne, oyun. `software-lifecycle`'ın DOĞRULA
aşamasının görsel tamamlayıcısıdır (deterministik `python -m core gate` kod tarafını
kapatır; bu skill görünür kaliteyi kapatır).

## Prosedür (render → incele → düzelt → tekrar → temiz olana kadar)

1. **Çalıştır:** çıktıyı gerçek bir tarayıcıda aç. Otomasyon için headless Chrome
   (puppeteer-core/Playwright) — sistemdeki Chrome'u sür; sayfayı yerel sunucudan
   servis et (ör. `python -m http.server`).
2. **Ekran görüntüsü al (birden çok durum):**
   - Görünümler: masaüstü (ör. 1440×900) VE mobil (ör. 390×844).
   - Durumlar: scroll bölümleri, hover/etkileşim, açık/koyu tema, boş/dolu veri.
   - Animasyon/3D için sahne otursun diye kısa bekle; WebGL testinde SwiftShader
     bayrakları gerekebilir (`--use-angle=swiftshader --enable-unsafe-swiftshader`).
3. **GÖZLE incele** (ajan görüntüleri okur) — kontrol listesi:
   - Görünürlük: metin/panel gerçekten görünüyor mu, yoksa 0-opaklıkta mı kaldı?
   - Layout: taşma, kesilme, üst üste binme, hizalama, mobil bozulma.
   - Kontrast/okunabilirlik: zemin üstünde metin okunuyor mu (a11y).
   - Efekt kalitesi: bloom/parlaklık patlaması, bulanık leke, sönük/ölü sahne,
     yanlış renk tonu (ör. istenmeyen pus/cast).
   - 3D/canvas gerçekten çiziyor mu (boş/siyah değil)?
   - Konsol/pageerror ve 404'ler (eksik dosya).
4. **Düzelt:** bulunan her kusuru gider (materyal/ışık/bloom/fog, CSS layout,
   opaklık/observer, viewport/DPR, eksik asset).
5. **Tekrar render et ve karşılaştır:** aynı görüntüleri yeniden al, iyileştiğini
   GÖRSELDEN doğrula. Temiz olana kadar 2-4'ü tekrarla (loop-engineering).

## "Görsel bitti" ölçütü
- Konsol hatası / 404 yok (favicon istisnası kabul).
- Tüm bölümlerde içerik görünür ve okunur; mobilde bozulma yok.
- Efektler amaçlandığı gibi (leke/pus/patlama yok), sahne gerçekten render ediyor.
- reduced-motion ve düşük cihazda makul (bkz. performans/erişilebilirlik).

## İlkeler
- Sözdizim/test yeşili görsel kaliteyi KANITLAMAZ — mutlaka gözle bak.
- Kusuru tarif etmekle yetinme; düzelt ve yeniden-render ile kanıtla.
- Test araçlarını proje klasörü DIŞINDA tut (temiz teslim); geçici görüntüleri
  scratchpad'e al.
- İlgili: `software-lifecycle` (doğrula), `loop-engineering` (render-düzelt döngüsü),
  `prior-art-research` (kalite çıtasını benzerlerinden öğren).
