---
name: benign-skill
version: 0.1.0
status: experimental
description: Test fixture'i - zararsiz, temiz bir skill. Tarama pass almalidir.
domains: [example]
risk_level: low
---

# Amac

Bu skill bir metni Markdown baslik seviyesine gore ozetler. Tamamen yerel,
ag erisimsiz, salt-okunur bir prosedurdur.

# Kullanim kosullari

Bir dokumanin bolum yapisini cikarmak istendiginde kullanilir.

# Zorunlu prosedur

1. Dokumanı satir satir oku.
2. `#` ile baslayan satirlari basliktir; seviyesini `#` sayisindan bul.
3. Ic ice bir agac olustur ve ozetle.

# Kaynaklar

- https://docs.python.org/3/library/re.html
