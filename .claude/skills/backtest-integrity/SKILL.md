---
name: backtest-integrity
description: Bir trading backtest'inin sonuclarini guvenilir kabul etmeden once butunluk denetimidir. Look-ahead (zaman sizintisi), survivorship bias, maliyet/slippage eksigi ve asiri iyimser yorumu yakalar. Herhangi bir strateji/indikator backtest edildiginde, canli veya paper trade DUSUNULMEDEN once zorunludur.
version: 1.0.0
risk_level: high
---

# Backtest Integrity

Bir backtest'in yuksek getiri gostermesi onu dogru yapmaz. Bu skill, sonucu
"guvenilir" ilan etmeden once gecmesi gereken kapilari tanimlar.

## Ne zaman kullanilir

Herhangi bir strateji, indikator veya sinyal backtest edildiginde. Paper trade
veya canli isleme gecis DUSUNULMEDEN once. Bu bir insan-onayi kapisidir; agent
tek basina canli isleme geciremez (policies/trading.yaml).

## Zorunlu kontrol listesi

1. **Look-ahead bias (zaman sizintisi)**: Her hesaplama yalnizca o an KAPANMIS
   bar'lara mi dayaniyor? Gelecek bilgisi (kapanmamis bar, ileriki fiyat,
   yeniden ifade edilen veri) sinyale karisiyor mu? Repaint eden indikatorleri isaretle.

2. **Warm-up dogru mu**: Indikatorun isinma periyodu once atlaniyor mu, yoksa
   eksik veriyle uretilen ilk sinyaller islenmis mi?

3. **Survivorship bias**: Evren yalnizca hayatta kalan enstrumanlardan mi olusuyor?
   Delist olanlar, iflaslar hesaba katilmis mi?

4. **Transaction cost + slippage**: Komisyon, spread ve slippage modellenmis mi?
   Sifir maliyetli backtest gecersizdir.

5. **Out-of-sample + walk-forward**: Parametreler tek bir donemde mi optimize edildi?
   Gorulmemis veride (OOS) ve ileri-donuslu (walk-forward) test edildi mi?

6. **Overfitting**: Kac parametre denendi? Parametre hassasiyeti (kucuk degisiklikte
   sonuc cokuyor mu)? Cok sayida denemeden en iyisini secmek (p-hacking) var mi?

## Kalite kapilari

- Yukaridaki kontrollerden herhangi biri BASARISIZ ise sonuc "guvenilir degil".
- Golden dataset varsa referans hesaplama ile birebir karsilastir.
- Sonucu `evaluator` subagent'ina bagimsiz dogrulat (isi yapan onaylamaz).

## Trading guvenlik hatti (policies/trading.yaml)

```
arastirma -> backtest -> BAGIMSIZ AUDIT -> OOS -> walk-forward
  -> maliyet/slippage -> paper trade (insan onayi) -> risk limitleri
  -> INSAN ONAYI -> kucuk sermaye -> canli izleme + kill switch
```
- withdrawal, limitsiz trade, agent'in kendi risk limitini degistirmesi: yasak.
- paper_trade ve live_trade: insan onayi zorunlu.

## Cikti formati

Her kontrol icin PASS/FAIL ve gerekce ver. Genel karar: RELIABLE / NOT_RELIABLE /
INSUFFICIENT_EVIDENCE. Asla "strateji karli" deme; "denetimden gecti/gecmedi" de.

## Kaynaklar

- Referans araclar: Qlib, Freqtrade, CCXT (skill degil, tool/framework).
- Ilgili: [[capability-gap-analysis]]
