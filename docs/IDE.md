# IDE'lerde ve her projede kullanim (global)

Bu belge, ajan sistemini Cursor / Windsurf / VS Code'da ve **her projede** nasil
kullanacagini anlatir.

## Onemli on kosul: Claude Code eklentisi

Bu sistem Claude Code'un mekanizmalari (hooks + `.claude/` + `python -m core` CLI)
uzerine kuruludur. Bu yuzden:

- **Calisir:** Cursor / Windsurf / VS Code icinde **Claude Code eklentisi** ile.
  Eklenti `~/.claude/` (kullanici seviyesi) konfigurasyonunu okur.
- **Calismaz:** Cursor'un yerlesik AI'i (Composer/Chat) veya Windsurf Cascade ile.
  Bunlar ayri agent'lardir; `.claude/` hook'larini calistirmaz, skill'leri yuklemez.

> Yerlesik AI'lar icin ayri bir "kural (rules)" koprusu gerekir (Cursor rules /
> Windsurf rules). Python tabanli zorlama (guard hook, policy engine) orada
> ayni sekilde calismaz. Isterseniz o hafif surumu ayrica hazirlariz.

## Global kurulum (bir kez, insan calistirir)

```bash
cd <ajan-repo-dizini>
python scripts/install_global.py
```

Bu betik:
1. `pip install -e .` yapar -> `ajan` ve `python -m core` HER dizinden calisir.
2. Seed skill'leri ve subagent'lari `~/.claude/skills` ve `~/.claude/agents` altina
   kopyalar -> hangi projeyi acarsan ac Claude Code bunlari yukler.
3. Hook'lari `~/.claude/settings.json`'a ekler:
   - `PreToolUse: python -m core guard` — anayasal koruma her projede
   - `SessionStart: python -m core session-start` — otomatik devreye girme
   - `UserPromptSubmit: python -m core on-prompt` — "ajan devreye gir" / "is bitti"

Ayrica guard hook 2>&1 false-positive yamasi icin (bir kez):
```bash
python scripts/setup_ajan.py
```

## Kurulumdan sonra

1. IDE'de **Claude Code eklentisinin** kurulu oldugundan emin ol.
2. IDE'yi (veya Claude Code oturumunu) yeniden baslat — hook'lar oturum basinda yuklenir.
   Eklenti ilk seferinde hook'lara guvenmeni isteyebilir; onayla.
3. Artik herhangi bir projede ajan otomatik devrede. Kontrol:
   - "ajan devreye gir" / "is bitti" ile ac/kapa
   - `python -m core ajan status` ile durum

## Mimari notu (global davranis)

- Platformun **evi bu repo'dur** (editable kurulum). `policies/`, `registry/`,
  `audit/` merkezi olarak burada kalir. Yani hangi projeden calistirirsan calistir
  ayni **tek yetenek kutuphanesini** ve ayni politikalari paylasirsin. Ogrenilen
  dersler, edinilen yetenekler tum projelerde ortaktir.
- Guard hook her projede calisir ama yalnizca **bu repo'nun** anayasal dosyalarini
  korur; actigin diger projelerin dosyalarina karismaz.
- `python -m core` farkli bir cwd'den calistiginda bile platform evini kendi konumundan
  bulur (paths.py `__file__` tabanli), cwd'ye bagimli degildir.

## Sorun giderme

| Belirti | Cozum |
|---|---|
| Hook calismiyor | IDE'yi yeniden baslat; `~/.claude/settings.json` hook'lari iceriyor mu bak |
| `python -m core` bulunamiyor | `pip install -e .` yapildi mi (install_global.py)? |
| `ajan` komutu yok | Python Scripts dizini PATH'te mi? Alternatif: `python -m core ...` kullan |
| Skill'ler gorunmuyor | `~/.claude/skills/` altina kopyalandi mi (install_global.py)? |
| Yerlesik Cursor AI kullaniyorum | Bu sistem Claude Code eklentisi gerektirir (yukari bak) |
