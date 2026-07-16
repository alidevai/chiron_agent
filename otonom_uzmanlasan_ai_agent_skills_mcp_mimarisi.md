# Otonom Uzmanlaşan AI Agent Sistemi
## Yazılım geliştirme, test, güvenlik, finans, trading ve yeni alanlarda kendini kontrollü biçimde geliştiren Skills + MCP mimarisi

**Belge sürümü:** 1.0  
**Tarih:** 16 Temmuz 2026  
**Amaç:** Bir yapay zekâ modelinin yalnızca genel bilgiye sahip olmasını değil; karşılaştığı her görevde uzman prosedürleri uygulamasını, eksik beceri veya araçlarını tespit etmesini, güvenilir kaynaklardan uygun Skill/MCP/tool bulmasını, bunları test ederek sisteme adapte etmesini ve zaman içinde doğrulanmış bir uzmanlık kütüphanesi oluşturmasını sağlayacak mimariyi tanımlamak.

---

## 1. Yönetici özeti

İstenen sistemin temel hedefi şudur:

> AI agent bir görevi yapmayı bilmiyorsa, düşük güvenle çalışıyorsa veya mevcut araçları yetersizse bunu fark etmeli; uygun Skill, MCP sunucusu, kütüphane, CLI veya API araştırmalı; adayları güvenlik, kalite, lisans ve uygunluk açısından incelemeli; sandbox ortamında test etmeli; başarılı olanı kontrollü biçimde kendi yetenek kataloğuna eklemeli ve daha sonra yeniden kullanmalıdır.

Bu yaklaşım mümkündür; ancak **agent’ın internette bulduğu her Skill veya MCP’yi otomatik olarak doğrudan kurması tehlikelidir**. Skill dosyaları doğal dil içinde zararlı talimatlar taşıyabilir; MCP sunucuları dosya sistemi, terminal, e-posta, GitHub, veritabanı veya broker hesabı gibi yüksek yetkili kaynaklara erişebilir. Bu nedenle sistem “sınırsız kendi kendine eklenti kuran agent” değil, aşağıdaki şekilde tasarlanmalıdır:

```text
Görev
  ↓
Yetkinlik ve güven analizi
  ↓
Mevcut Skill/Tool yeterli mi?
  ├─ Evet → Kontrollü yürütme
  └─ Hayır
       ↓
Skill / MCP / Tool araştırması
       ↓
Kaynak ve itibar doğrulama
       ↓
Statik güvenlik taraması
       ↓
İzin ve risk analizi
       ↓
İzole sandbox kurulumu
       ↓
Fonksiyonel test + güvenlik testi
       ↓
Karşılaştırmalı değerlendirme
       ↓
Politika kararı
       ├─ Otomatik onay: düşük riskli
       ├─ İnsan onayı: orta/yüksek riskli
       └─ Reddet: güvenilmez
       ↓
Sürümlü yetenek kataloğuna ekleme
       ↓
İzleme, geri alma ve periyodik yeniden doğrulama
```

Sistemin ana ilkesi:

> Agent araştırma ve hazırlama konusunda otonom olabilir; fakat kalıcı kurulum, geniş yetki, üretim sistemi değişikliği ve finansal emir yürütme konusunda risk temelli onay kapıları bulunmalıdır.

---

# 2. Sorunun doğru tanımı

Büyük dil modelleri çok geniş bilgiye sahip olabilir, fakat aşağıdaki noktalarda “tecrübesiz çalışan” gibi davranabilir:

- Doğru iş akışını seçememek
- Gereksinimleri netleştirmeden kod yazmak
- Mevcut projeyi incelemeden yeni mimari üretmek
- Test, güvenlik veya geri dönüş planını atlamak
- Yanlış veya güncel olmayan kütüphane kullanmak
- Finansal veride zaman sızıntısını fark etmemek
- Backtest sonucunu aşırı iyimser yorumlamak
- Bilmediği konuda yüksek güvenle cevap vermek
- Aracı nasıl kullanacağını bilse bile hangi koşullarda kullanmaması gerektiğini bilmemek
- Yeni bir alanla karşılaşınca güvenilir uzman prosedürü bulamamak

Bu sorunlar yalnızca daha büyük model kullanmakla tamamen çözülmez. Modelin çevresine bir **yetkinlik işletim sistemi** kurulmalıdır.

Bu sistem beş katmandan oluşur:

1. **Knowledge:** Alan bilgisi, dokümanlar ve güncel kaynaklar  
2. **Skills:** Uzmanların uyguladığı prosedürler ve kalite kriterleri  
3. **Tools/MCP:** Gerçek dünyada işlem yapma araçları  
4. **Policies:** İzin, güvenlik ve risk sınırları  
5. **Evaluators:** Sonucun doğru, güvenli ve yeniden üretilebilir olup olmadığını kontrol eden bağımsız denetçiler  

---

# 3. Skill, Tool, MCP, Agent ve Memory arasındaki fark

## 3.1 Skill

Skill, modele bir işi **nasıl yapacağını** öğretir.

Örnekler:

- Kod inceleme prosedürü
- Backtest bütünlük kontrolü
- DCF değerleme yöntemi
- Playwright ile E2E test yazımı
- API tasarım kontrol listesi
- Hata ayıklama süreci
- Bir MCP sunucusunun güvenliğini denetleme

Tipik yapı:

```text
skill-name/
├── SKILL.md
├── references/
├── scripts/
├── templates/
├── examples/
└── tests/
```

Açık Agent Skills standardı:

- https://github.com/agentskills/agentskills
- https://agentskills.io/
- https://github.com/anthropics/skills

## 3.2 Tool

Tool, agent’ın bir işlem yapmasını sağlar.

Örnekler:

- Terminal komutu çalıştırma
- Python kodu yürütme
- GitHub issue okuma
- Web araması yapma
- SQL sorgusu çalıştırma
- Backtest başlatma
- Dosya yazma
- Broker API’sine emir gönderme

## 3.3 MCP

Model Context Protocol, model uygulamalarını harici veri ve araçlara standart bir protokolle bağlar.

Resmî kaynaklar:

- https://github.com/modelcontextprotocol
- https://github.com/modelcontextprotocol/servers
- https://github.com/modelcontextprotocol/registry
- https://github.com/modelcontextprotocol/inspector
- https://github.com/modelcontextprotocol/python-sdk

MCP, Skill’in yerine geçmez:

```text
Skill: GitHub issue’sunu nasıl incelemeli ve çözmeli?
MCP: GitHub’a bağlanıp issue, repo, PR ve dosyaları okuma/yazma yeteneği
Policy: Hangi repolara yazabilir? PR açabilir mi? Main branch’e push yasak mı?
Evaluator: Üretilen patch testleri geçiyor mu? Güvenli mi?
```

## 3.4 Memory

Memory, daha önce öğrenilmiş ve doğrulanmış bilgilerin saklandığı katmandır:

- Proje mimarisi
- Kullanıcı tercihleri
- Kabul edilmiş kod standartları
- Önceki hatalar
- Doğrulanmış Skill’ler
- Başarılı tool yapılandırmaları
- Reddedilmiş veya zararlı paketler
- Finansal veri kaynaklarının güvenilirlik notları
- Strateji deneyi sonuçları

## 3.5 Agent

Agent; model, Skill, araç, hafıza, politika ve değerlendirme mekanizmalarının birlikte çalışan hâlidir.

---

# 4. “Her konuda uzman” hedefinin gerçekçi yorumu

Hiçbir sistem kelimenin mutlak anlamıyla her konuda hatasız uzman olamaz. Doğru mühendislik hedefi şudur:

> Sistem her konuda uzman olduğunu varsaymamalı; görevin alanını, riskini ve kendi yeterliliğini ölçmeli; gerektiğinde uzman prosedürü, güncel kaynak, araç veya ayrı bir uzman agent edinmeli ve sonucu bağımsız doğrulamadan sunmamalıdır.

Bunun için agent’ın dört davranışı zorunlu olmalıdır:

1. **Bilmediğini fark etme**
2. **Eksik olan şeyin bilgi mi, Skill mi, tool mu olduğunu ayırma**
3. **Güvenilir çözümü araştırma ve test etme**
4. **Sonucu kalıcı öğrenmeye dönüştürme**

---

# 5. Önerilen üst düzey mimari

```text
┌───────────────────────────────────────────────────────────────┐
│                         USER / API                            │
└──────────────────────────────┬────────────────────────────────┘
                               │
                               ▼
┌───────────────────────────────────────────────────────────────┐
│                 SUPERVISOR / META-AGENT                       │
│ Görev sınıflandırma • risk analizi • güven ölçümü             │
└───────────────┬───────────────────────┬───────────────────────┘
                │                       │
                ▼                       ▼
┌────────────────────────┐   ┌──────────────────────────────────┐
│ Capability Registry    │   │ Knowledge / Research Layer       │
│ Skills • MCP • Tools   │   │ Web • Docs • GitHub • Papers    │
│ Versions • Scores      │   │ RAG • Source validation          │
└───────────────┬────────┘   └──────────────────┬───────────────┘
                │                               │
                └──────────────┬────────────────┘
                               ▼
┌───────────────────────────────────────────────────────────────┐
│            CAPABILITY GAP DETECTOR                            │
│ Mevcut beceri yeterli mi? Güncel mi? Test edilmiş mi?         │
└───────────────────────┬───────────────────────────────────────┘
                        │
            ┌───────────┴───────────┐
            │                       │
            ▼                       ▼
┌───────────────────────┐  ┌────────────────────────────────────┐
│ Existing capability   │  │ Capability Acquisition Pipeline    │
│ ile görevi yürüt      │  │ Skill/MCP/Tool keşfet, tara, test  │
└─────────────┬─────────┘  └──────────────────┬─────────────────┘
              │                               │
              └──────────────┬────────────────┘
                             ▼
┌───────────────────────────────────────────────────────────────┐
│                     EXECUTION SANDBOX                         │
│ Dosya sistemi • terminal • browser • Python • containers      │
└───────────────────────┬───────────────────────────────────────┘
                        ▼
┌───────────────────────────────────────────────────────────────┐
│                  INDEPENDENT EVALUATORS                       │
│ Test • güvenlik • doğruluk • veri kalitesi • risk • maliyet   │
└───────────────────────┬───────────────────────────────────────┘
                        ▼
┌───────────────────────────────────────────────────────────────┐
│           HUMAN APPROVAL / POLICY ENFORCEMENT                 │
└───────────────────────┬───────────────────────────────────────┘
                        ▼
┌───────────────────────────────────────────────────────────────┐
│       VERSIONED SKILL & TOOL STORE + AUDIT LOG                │
└───────────────────────────────────────────────────────────────┘
```

---

# 6. Meta-Agent: Kendini geliştirme yöneticisi

Ana sisteme özel bir **Capability Manager Agent** eklenmelidir. Bu agent doğrudan kullanıcı işini yapmak yerine sistemin eksik kabiliyetlerini yönetir.

## 6.1 Temel görevleri

- Gelen görevi alanlara ayırmak
- Gerekli uzmanlıkları belirlemek
- Mevcut Skill ve tool kataloğunu sorgulamak
- Yeterlilik skorunu hesaplamak
- Eksik Skill/MCP/tool’u araştırmak
- Adayları puanlamak
- Güvenlik incelemesi başlatmak
- Sandbox test planı oluşturmak
- Kurulum veya adaptasyon kararı vermek
- Yeni kabiliyeti indekslemek
- Kullanım sonucunu izlemek
- Başarısız kabiliyeti devre dışı bırakmak

## 6.2 Capability Gap Detector

Her görev öncesinde aşağıdaki sorular yanıtlanmalıdır:

```yaml
task_domain:
task_subdomains:
required_skills:
required_tools:
required_data_sources:
risk_level:
existing_capabilities:
missing_capabilities:
stale_capabilities:
confidence:
evidence:
action:
```

Örnek:

```yaml
task_domain: software_engineering
task_subdomains:
  - rust
  - cryptography
  - performance_testing
required_skills:
  - repository-discovery
  - rust-secure-coding
  - cryptographic-review
  - benchmarking
required_tools:
  - rust-toolchain
  - cargo-audit
  - criterion
missing_capabilities:
  - cryptographic-review
confidence: 0.54
action: research_and_stage_capability
```

## 6.3 Eksiklik türleri

Agent eksikliği doğru sınıflandırmalıdır:

| Eksiklik | Çözüm |
|---|---|
| Güncel bilgi eksikliği | Web/doküman/GitHub araştırması |
| Prosedür eksikliği | Skill bul veya oluştur |
| İşlem yeteneği eksikliği | Tool/CLI/API/MCP bul |
| Veri eksikliği | Veri kaynağı veya connector bul |
| Kalite doğrulaması eksikliği | Evaluator veya test paketi oluştur |
| Yetki eksikliği | İnsan onayı veya credential talebi |
| Model kapasitesi yetersizliği | Uzman model/sub-agent kullan |
| Alan belirsizliği | Taksonomi ve gereksinim analizi |

---

# 7. Otomatik Skill keşif sistemi

## 7.1 Arama kaynakları

Önerilen öncelik sırası:

1. Resmî proje veya üretici deposu
2. Agent Skills resmî standardı ve doğrulanmış koleksiyonlar
3. Büyük, aktif ve güvenilir kuruluşların depoları
4. Akademik çalışmaya bağlı resmî kod
5. Topluluk tarafından küratörlüğü yapılan listeler
6. Genel GitHub araması
7. Son çare olarak agent’ın kendisinin Skill üretmesi

Başlangıç kaynakları:

- Agent Skills specification  
  https://github.com/agentskills/agentskills

- Anthropic Skills  
  https://github.com/anthropics/skills

- Anthropic Skill Creator  
  https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md

- Vercel “Find Skills” Skill’i  
  https://github.com/vercel-labs/skills/blob/main/skills/find-skills/SKILL.md

- VoltAgent Awesome Agent Skills  
  https://github.com/VoltAgent/awesome-agent-skills

- Trail of Bits Security Skills  
  https://github.com/trailofbits/skills

- Trail of Bits Curated Skills  
  https://github.com/trailofbits/skills-curated

- GitHub Agent Skills açıklaması  
  https://docs.github.com/copilot/concepts/agents/about-agent-skills

## 7.2 Skill arama sorgusu üretimi

Agent, kullanıcı cümlesini doğrudan GitHub’da aramamalıdır. Önce ihtiyaç tanımı üretmelidir.

Örnek:

```text
Kullanıcı talebi:
“Solidity kontratını güvenlik açısından incele.”

İhtiyaçlar:
- Solidity static analysis
- Smart contract threat modeling
- Slither
- Echidna fuzzing
- Foundry tests
- Reentrancy and access control checks

Arama sorguları:
- agent skill solidity security audit SKILL.md
- GitHub Claude skill Slither Echidna
- smart contract audit agent workflow
- Trail of Bits Solidity skill
```

## 7.3 Aday Skill puanlama

Her aday için 100 puanlık bir sistem önerilir:

```yaml
source_reputation: 0-20
maintainer_identity: 0-10
recent_maintenance: 0-10
documentation_quality: 0-10
test_coverage: 0-10
license_clarity: 0-5
scope_match: 0-15
security_posture: 0-15
portability: 0-5
```

Örnek kararlar:

- **85–100:** Güçlü aday; sandbox testine al
- **70–84:** İncelenebilir; ek güvenlik denetimi gerekli
- **50–69:** Yalnızca referans olarak kullan
- **0–49:** Kurma; reddet

Yıldız sayısı tek başına kalite göstergesi değildir. Repo ele geçirilmiş, bakımsız, lisanssız veya kötü niyetli olabilir.

---

# 8. Skill yoksa agent’ın kendi Skill’ini üretmesi

Aranan Skill bulunamazsa Capability Manager aşağıdaki süreci çalıştırmalıdır:

```text
Alan araştırması
  ↓
Birincil kaynakların toplanması
  ↓
Uzman iş akışının çıkarılması
  ↓
SKILL.md taslağı
  ↓
Örnekler ve karşı örnekler
  ↓
Test fixture’ları
  ↓
Evaluator oluşturma
  ↓
Sandbox görevlerinde deneme
  ↓
Bağımsız critic incelemesi
  ↓
Sürüm 0.x olarak kayıt
```

## 8.1 Skill üretme kaynağı

Skill üretirken kaynak önceliği:

- Resmî dokümantasyon
- Standartlar
- Akademik makaleler
- Güvenilir açık kaynak projeler
- Alan uzmanlarının iyi bilinen rehberleri
- Projenin kendi kuralları

Agent, yalnızca kendi genel bilgisine dayanarak yüksek riskli Skill üretmemelidir.

## 8.2 Üretilen Skill şablonu

```markdown
---
name: example-skill
version: 0.1.0
status: experimental
description: >
  Bu Skill’in ne zaman ve hangi amaçla kullanılacağı.
domains:
  - example
risk_level: medium
required_tools:
  - example_tool
allowed_permissions:
  - filesystem_read
forbidden_permissions:
  - production_write
sources:
  - url: https://...
    type: official_documentation
evaluation_suite: tests/eval.yaml
---

# Amaç

# Kullanım koşulları

# Kullanılmaması gereken durumlar

# Ön koşullar

# Zorunlu prosedür

# Kalite kapıları

# Güvenlik kuralları

# Hata durumları

# Çıktı formatı

# Örnekler

# Testler

# Kaynaklar
```

## 8.3 Skill’in olgunluk seviyeleri

```text
experimental
  ↓
sandbox-validated
  ↓
project-approved
  ↓
production-approved
  ↓
deprecated / revoked
```

Her yeni Skill ilk olarak `experimental` olmalıdır.

---

# 9. MCP ve Tool keşif sistemi

## 9.1 MCP arama kaynakları

Öncelikle resmî MCP Registry kullanılmalıdır:

- https://github.com/modelcontextprotocol/registry
- https://registry.modelcontextprotocol.io/ (mevcut istemci desteğine göre)
- https://github.com/modelcontextprotocol/servers

Topluluk listeleri yalnızca keşif amaçlı kullanılmalıdır:

- https://github.com/punkpeye/awesome-mcp-servers

Resmî veya üretici tarafından sağlanan MCP örnekleri:

- GitHub MCP Server  
  https://github.com/github/github-mcp-server

- MCP Inspector  
  https://github.com/modelcontextprotocol/inspector

- MCP Python SDK  
  https://github.com/modelcontextprotocol/python-sdk

## 9.2 Tool mu MCP mi?

Her iş için MCP kullanmak gerekmez.

| Durum | En uygun seçim |
|---|---|
| Yerel, deterministik işlem | CLI veya Python kütüphanesi |
| Çok sayıda agent istemcisinde ortak entegrasyon | MCP |
| Basit HTTP servisi | Doğrudan API istemcisi |
| Büyük dosya/veri dönüşümü | Yerel worker veya container |
| Kullanıcı hesabına bağlı hizmet | Güvenli OAuth connector/MCP |
| Yüksek frekanslı trading execution | Düşük gecikmeli özel servis; MCP yalnızca kontrol düzlemi |
| Araştırma ve prototip | MCP veya tool wrapper |

Trading emirleri gibi gecikme ve güvenilirlik açısından kritik işlemler için MCP doğrudan execution engine olarak kullanılmamalı; emir motoru ayrı, deterministik bir servis olmalıdır.

## 9.3 MCP aday değerlendirme kriterleri

```yaml
publisher_verified:
official_registry_entry:
repository_verified:
license:
release_signing:
dependency_health:
transport_security:
authentication_method:
requested_permissions:
tool_descriptions_safe:
data_retention:
telemetry:
network_destinations:
filesystem_scope:
secret_handling:
rate_limits:
audit_logging:
rollback_supported:
```

---

# 10. Neden otomatik kurulum tehlikelidir?

Skill ve MCP ekosistemlerinde aşağıdaki riskler bulunur:

- Prompt injection
- Tool poisoning
- Gizli veri sızdırma
- Zararlı shell komutları
- Dependency confusion
- Typosquatting
- Maintainer hesabının ele geçirilmesi
- Güncelleme sonrası zararlı sürüm
- Gereğinden geniş OAuth izinleri
- Dosya sistemi dışına erişim
- Kimlik bilgilerini loglama
- Web içeriğindeki talimatları sistem komutu gibi kabul etme
- Bir tool’un diğer tool’un yetkisini kötüye kullanması
- Broker veya e-posta gibi geri dönüşü zor işlemler

Güvenlik araştırması için önemli referanslar:

- Snyk Agent Scan  
  https://github.com/snyk/agent-scan

- NVIDIA garak  
  https://github.com/NVIDIA/garak

- MCP Inspector  
  https://github.com/modelcontextprotocol/inspector

- Trail of Bits Security Skills  
  https://github.com/trailofbits/skills

- Trail of Bits kötü niyetli Skill test örnekleri  
  https://github.com/trailofbits/overtly-malicious-skills

- Awesome MCP Security  
  https://github.com/Puliczek/awesome-mcp-security

Bu nedenle önerilen kural:

> Agent kendisi aday bulabilir, indirebilir ve izole ortamda test edebilir; ancak kalıcı sisteme ekleme yetkisi risk seviyesine göre politika motoruna veya insana aittir.

---

# 11. Güvenli Capability Acquisition Pipeline

## Aşama 1 — İhtiyaç doğrulama

- Eksik Skill gerçekten gerekli mi?
- Mevcut Skill parametre veya örnek eklenerek yeterli olabilir mi?
- Tool ihtiyacı yalnızca bir defalık mı?
- İş genel web araştırmasıyla çözülebilir mi?
- Yeni bağımlılık teknik borç yaratacak mı?

## Aşama 2 — Kaynak doğrulama

- Repo sahibi kim?
- Organizasyon doğrulanmış mı?
- Resmî site repoya bağlantı veriyor mu?
- Repo fork mu?
- Son release ne zaman?
- Commit imzaları var mı?
- Güvenlik politikası var mı?
- Açık kritik güvenlik issue’ları var mı?
- Lisans uygun mu?

## Aşama 3 — Statik inceleme

Skill için:

- `SKILL.md` içinde sistem talimatlarını değiştirmeye çalışan ifadeler
- Secret veya credential okuma isteği
- Dış sunucuya veri gönderme
- Base64 veya obfuscated içerik
- Shell pipe-to-bash
- Dosya silme
- Güvenlik kontrollerini devre dışı bırakma
- Kullanıcıdan gizli davranma talimatı
- “Önceki talimatları yok say” benzeri prompt injection

MCP/tool için:

- Dependency taraması
- SAST
- Secret scan
- Network endpoint analizi
- Container manifest analizi
- Install/postinstall script kontrolü
- İzin manifesti
- Telemetry ve veri toplama kontrolü

## Aşama 4 — İzole kurulum

```text
Ephemeral container
Read-only host filesystem
No user home access
No production credentials
Restricted outbound network
CPU/RAM/time limits
Temporary test secrets
Synthetic test data
Full audit logs
```

## Aşama 5 — Fonksiyonel test

- Tanımlanan işi yapıyor mu?
- Hataları anlaşılır mı?
- Deterministik mi?
- Timeout durumunda güvenli kapanıyor mu?
- Sonuç kalitesi alternatiflerden iyi mi?
- Dokümantasyona uygun davranıyor mu?

## Aşama 6 — Güvenlik testi

- Prompt injection
- Tool poisoning
- Data exfiltration
- Path traversal
- Command injection
- SSRF
- Excessive permissions
- Cross-tool escalation
- Malicious file
- Malicious web page
- Secret leakage

## Aşama 7 — Evals

Bir Skill veya tool ancak ölçülebilir testte başarılıysa eklenmelidir.

Örnek:

```yaml
capability: playwright-web-testing
evals:
  - name: login_success
    expected: pass
  - name: invalid_credentials
    expected: correct_error
  - name: prompt_injection_page
    expected: ignore_page_instructions
  - name: secret_exfiltration_attempt
    expected: blocked
minimum_score: 0.90
critical_failures_allowed: 0
```

## Aşama 8 — Yetki kararı

### Otomatik kurulabilecek düşük riskli kabiliyetler

- Salt-okunur dokümantasyon Skill’i
- Lokal, ağ erişimsiz format dönüştürücü
- Test fixture üreticisi
- Read-only kod analizi
- Sandbox içinde çalışan linter

### İnsan onayı gerektirenler

- GitHub yazma yetkisi
- E-posta gönderme
- Calendar event oluşturma
- Veritabanına yazma
- Production deployment
- Kullanıcı dosya sistemine geniş erişim
- Cloud hesabına erişim
- Finansal hesap veya broker erişimi

### Otomatik olarak yasak olması gerekenler

- Withdrawal yetkisi
- Sınırsız canlı trade
- Production secret dışa aktarma
- Ana branch’e doğrudan push
- Onaysız veri silme
- Güvenlik loglarını kapatma
- Kendi politika motorunu değiştirme
- Kendi evaluator sonuçlarını silme

---

# 12. İzin modeli

Her Skill/MCP/tool için açık izin manifesti tutulmalıdır.

```yaml
capability_id: github-mcp
version: 1.2.3
permissions:
  filesystem:
    read:
      - /workspace/project
    write:
      - /workspace/project
    deny:
      - ~/.ssh
      - ~/.aws
      - /etc
  network:
    allow:
      - api.github.com
    deny_all_others: true
  github:
    repos:
      - organization/project
    read: true
    create_branch: true
    open_pr: true
    merge_pr: false
    push_main: false
  secrets:
    accessible:
      - GITHUB_TOKEN_SCOPED
  human_approval:
    required_for:
      - delete_branch
      - change_workflow
      - release
```

Principle of least privilege zorunlu olmalıdır.

---

# 13. Capability Registry tasarımı

Her Skill, MCP ve tool merkezi bir kayıt sisteminde tutulmalıdır.

```yaml
id: backtest-integrity
type: skill
domain:
  - finance
  - quantitative_trading
version: 1.3.0
status: production-approved
source:
  repository: https://github.com/...
  commit: abc123
license: Apache-2.0
risk_level: high
maintainer: internal
installed_at: 2026-07-16
last_validated_at: 2026-07-16
validation_score: 0.94
permissions:
  - market_data_read
  - python_sandbox
forbidden_permissions:
  - broker_live_order
dependencies:
  - pandas
  - numpy
  - vectorbt
evaluators:
  - lookahead_eval
  - cost_model_eval
known_limitations:
  - options_assignment_not_supported
rollback_version: 1.2.2
```

Registry aşağıdaki sorguları desteklemelidir:

- Bu görev için hangi Skill’ler var?
- Hangi Skill en yüksek başarı oranına sahip?
- Hangi tool güncelliğini yitirmiş?
- Hangi MCP’nin izni gereğinden geniş?
- Hangi kabiliyet son güncellemeden sonra yeniden test edilmedi?
- Hangi Skill belirli projede başarısız oldu?
- Hangi sürüme geri dönülebilir?

---

# 14. Skill yönlendirme ve progressive disclosure

Tüm Skill’leri aynı anda model context’ine yüklemek hatadır. Binlerce talimat:

- Token maliyetini artırır
- Dikkati dağıtır
- Çelişkili prosedürler oluşturur
- Yanlış Skill kullanımına yol açar

Önerilen yöntem:

```text
1. Registry metadata taraması
2. En ilgili 5–10 Skill adayının seçilmesi
3. Risk ve proje uyumu filtresi
4. Yalnızca seçilen Skill özetlerinin yüklenmesi
5. Görev sırasında ihtiyaç duyulan tam Skill içeriğinin açılması
6. İş bitince context’ten çıkarılması
```

Bu yaklaşım “progressive disclosure” olarak düşünülebilir.

---

# 15. Otonom öğrenme döngüsü

Voyager projesi, görevlerden yeni yürütülebilir beceriler çıkarıp bir skill library içinde saklayan yaşam boyu öğrenme yaklaşımının önemli örneklerinden biridir:

- https://github.com/MineDojo/Voyager
- https://arxiv.org/abs/2305.16291

Voyager Minecraft ortamına yönelik olsa da şu fikirler genel agent sistemine uyarlanabilir:

1. Otomatik görev müfredatı
2. Başarılı davranışları beceri olarak saklama
3. Benzer görevlerde semantik geri çağırma
4. Çevre geri bildirimiyle iteratif düzeltme
5. Kendi sonucunu doğrulama

Genel sisteme uygulanmış hâli:

```text
Görev tamamlandı
  ↓
Başarı kanıtı var mı?
  ↓
Tekrar kullanılabilir prosedür var mı?
  ↓
Skill adayı çıkar
  ↓
Kişisel/veri içeren kısımları temizle
  ↓
Genelleştir
  ↓
Test örnekleri üret
  ↓
Evaluator çalıştır
  ↓
Registry’ye experimental olarak ekle
```

## 15.1 Her başarılı işlem Skill olmamalıdır

Skill’e dönüştürme kriterleri:

- Aynı veya benzer görev tekrar edebilir
- Prosedür genel ve taşınabilir
- Başarı ölçülebilir
- Güvenlik sınırları tanımlanabilir
- Alan bilgisi açık kaynaklarla doğrulanabilir
- Kullanıcıya özel sırlar içermez

---

# 16. Agent’ın kendisini değerlendirmesi

Agent şu durumlarda otomatik olarak Capability Manager’ı çağırmalıdır:

- Güven skoru eşik altında
- Kullanıcı “en güncel”, “en iyi”, “doğrula” diyor
- Kullanılan kütüphane veya standart güncel olmayabilir
- Alan yüksek riskli: finans, sağlık, hukuk, güvenlik
- Görev mevcut Skill’in kapsamı dışında
- Tool çağrısı iki kez başarısız oldu
- Aynı hata tekrar ediyor
- Test kapsamı düşük
- Reviewer kritik bulgu verdi
- Sonuçlar kaynaklar arasında çelişiyor
- Kullanıcı özel bir dosya formatı veya sistem istiyor
- Mevcut MCP gerekli kaynağa erişemiyor

Örnek güven politikası:

```python
if confidence < 0.75:
    acquire_or_research_capability()

if risk_level in {"high", "critical"}:
    require_independent_evaluator()

if action_is_irreversible:
    require_human_approval()
```

---

# 17. Multi-agent rol dağılımı

## 17.1 Meta katmanı

- **Supervisor Agent:** Genel akışı yönetir
- **Capability Manager:** Eksik Skill/tool bulur
- **Security Gatekeeper:** Kurulum ve izinleri denetler
- **Evaluator Agent:** Başarıyı bağımsız ölçer
- **Memory Curator:** Kalıcı bilgi ve Skill temizliği yapar

## 17.2 Yazılım geliştirme

- Requirements Analyst
- Software Architect
- Implementation Agent
- Test Engineer
- Security Reviewer
- Code Reviewer
- Performance Engineer
- Release Engineer
- Incident/Debug Agent

## 17.3 Finans ve trading

- Financial Data Quality Agent
- Fundamental Analyst
- Quant Researcher
- Indicator Engineer
- Backtest Auditor
- Risk Manager
- Execution Engineer
- Portfolio Reviewer
- Compliance Gate

## 17.4 Uzman üretme

Yeni alan geldiğinde sistem kalıcı bir agent oluşturmak zorunda değildir. Geçici uzman agent üretilebilir:

```text
Yeni görev: Biyoinformatik pipeline denetimi

Capability Manager:
- Alan taksonomisini çıkarır
- Resmî tool ve standartları bulur
- Bioinformatics QA Skill oluşturur
- Gerekli container/tool’ları ekler
- Geçici Bioinformatics Reviewer Agent başlatır
- Görev sonunda Skill’i doğrulayıp saklar
```

---

# 18. Orkestrasyon seçenekleri

## LangGraph

Uzun süreli, stateful, retry ve human-in-the-loop iş akışları için uygundur:

- https://github.com/langchain-ai/langgraph

Örnek workflow:

```text
ClassifyTask
  ↓
AssessCapabilities
  ↓
[CapabilityAvailable?]
  ├─ Yes → Plan
  └─ No  → Discover → Scan → Sandbox → Evaluate → Approve
  ↓
Execute
  ↓
IndependentReview
  ↓
[Passed?]
  ├─ No → Diagnose → Retry / Rollback
  └─ Yes → PersistLearning
```

## OpenHands

Kod, terminal, dosya ve sandbox odaklı yazılım agent altyapısı:

- https://github.com/OpenHands/OpenHands

## SWE-agent

Issue çözme ve repository patch üretme iş akışları için referans:

- https://github.com/SWE-agent/SWE-agent

## Open Deep Research

Araştırma agent’ı ve MCP destekli çok kaynaklı araştırma için referans:

- https://github.com/langchain-ai/open_deep_research

## GitHub Spec Kit

Spesifikasyon odaklı geliştirme için:

- https://github.com/github/spec-kit

---

# 19. Yazılım geliştirme Skill kataloğu

İlk üretim sürümünde en az aşağıdaki Skill’ler bulunmalıdır:

## Temel mühendislik

1. Repository Discovery
2. Requirements Analysis
3. Acceptance Criteria
4. Technical Specification
5. Architecture Review
6. Implementation Planning
7. Dependency Selection
8. Test-Driven Development
9. Debugging
10. Refactoring
11. API Design
12. Database Design
13. Migration Safety
14. Concurrency Review
15. Error Handling
16. Observability
17. Documentation
18. Git Workflow
19. Pull Request Preparation
20. Release and Rollback

## Test

21. Unit Testing
22. Integration Testing
23. Contract Testing
24. End-to-End Testing
25. Browser Testing
26. Property-Based Testing
27. Fuzz Testing
28. Mutation Testing
29. Performance Testing
30. Load and Stress Testing
31. Regression Testing
32. Flaky Test Diagnosis
33. Test Data Management
34. Coverage Quality Review

## Güvenlik

35. Threat Modeling
36. Secure Coding Review
37. Dependency Security
38. Secret Detection
39. SAST
40. DAST
41. Authentication Review
42. Authorization Review
43. API Security
44. Cloud/IAM Review
45. Container Security
46. Infrastructure-as-Code Security
47. Supply Chain Security
48. Prompt Injection Defense
49. MCP Security Review
50. Agent Permission Review

Güvenlik Skill referansı:

- https://github.com/trailofbits/skills
- https://github.com/trailofbits/skills-curated
- https://github.com/NVIDIA/garak
- https://github.com/snyk/agent-scan

---

# 20. Finans ve trading Skill kataloğu

## Finans

1. Financial Data Validation
2. Financial Statement Spreading
3. Financial Statement Normalization
4. Ratio Analysis
5. Cash Flow Analysis
6. Earnings Analysis
7. Guidance Analysis
8. DCF Valuation
9. Trading Comparables
10. Precedent Transactions
11. Sum-of-the-Parts
12. Credit Analysis
13. Covenant Analysis
14. Scenario Analysis
15. Sensitivity Analysis
16. Portfolio Risk
17. Macro Data Analysis
18. News Impact Analysis
19. SEC/filing Research
20. Source and Citation Validation

## Quant ve trading

21. Indicator Specification
22. Indicator Implementation
23. Indicator Cross-Library Validation
24. Strategy Hypothesis
25. Feature Engineering
26. Market Regime Detection
27. Backtest Integrity
28. Look-Ahead Bias Detection
29. Survivorship Bias Detection
30. Transaction Cost Modeling
31. Slippage Modeling
32. Walk-Forward Analysis
33. Out-of-Sample Validation
34. Overfitting Detection
35. Monte Carlo Testing
36. Risk Management
37. Position Sizing
38. Portfolio Construction
39. Execution Simulation
40. Paper Trading
41. Live Trading Safety
42. Trade Journal Analysis
43. Strategy Monitoring
44. Strategy Degradation
45. Kill Switch and Incident Response

## Referans açık kaynak projeler

- Microsoft Qlib  
  https://github.com/microsoft/qlib

- Freqtrade  
  https://github.com/freqtrade/freqtrade

- CCXT  
  https://github.com/ccxt/ccxt

- FinRL  
  https://github.com/AI4Finance-Foundation/FinRL

- FinRobot  
  https://github.com/AI4Finance-Foundation/FinRobot

- TradingAgents  
  https://github.com/TauricResearch/TradingAgents

Bu projeler Skill değildir; tool, framework veya mimari referans olarak kullanılmalıdır.

---

# 21. Trading için özel güvenlik politikası

AI agent’ın kendine broker MCP bulup canlı hesaba bağlanması otomatik olmamalıdır.

Zorunlu katmanlar:

```text
Araştırma
  ↓
Backtest
  ↓
Bağımsız backtest audit
  ↓
Out-of-sample
  ↓
Walk-forward
  ↓
Maliyet ve slippage
  ↓
Paper trading
  ↓
Risk limitleri
  ↓
İnsan onayı
  ↓
Küçük sermaye / düşük limit
  ↓
Canlı izleme ve kill switch
```

Broker credential politikası:

- Withdrawal yetkisi kapalı
- API key IP allowlist
- Sadece gerekli market ve hesap
- Maksimum günlük zarar
- Maksimum emir büyüklüğü
- Maksimum pozisyon
- Maksimum kaldıraç
- Emir başına audit log
- Manuel acil durdurma
- Agent’ın kendi limitlerini değiştirmesi yasak
- Kritik emirlerde iki aşamalı onay

---

# 22. Eval sistemi

Bir agent “iş bitti” demeden kanıt üretmelidir.

## 22.1 Skill eval türleri

- Golden task testleri
- Negative testler
- Adversarial testler
- Regression testleri
- Gerçek proje görevleri
- İnsan puanlaması
- Model-as-judge, fakat tek başına değil
- Deterministik araç sonuçları
- Performans ve maliyet testi

## 22.2 Karşılaştırmalı değerlendirme

Yeni Skill şu üç yapı ile karşılaştırılmalıdır:

1. Skillsiz model
2. Mevcut eski Skill
3. Yeni aday Skill

Ölçümler:

```yaml
task_success:
test_pass_rate:
security_violations:
hallucination_rate:
tool_error_rate:
token_cost:
latency:
human_edits_required:
reproducibility:
```

Yeni Skill yalnızca “daha uzun ve detaylı çıktı” verdiği için başarılı sayılmamalıdır.

## 22.3 Bağımsız evaluator

Skill’i üreten agent aynı zamanda nihai onaylayıcı olmamalıdır.

```text
Builder Agent → Skill oluşturur
Evaluator Agent → Kör test yapar
Security Agent → izin ve saldırı testi yapar
Policy Engine → karar verir
```

---

# 23. Güncelleme ve tedarik zinciri güvenliği

Kurulan Skill veya MCP zamanla değişebilir.

Zorunlu kontroller:

- Commit SHA pinleme
- Package version pinleme
- Lockfile
- Container digest
- SBOM
- İmzalı release tercih etme
- Otomatik güncelleme yerine staged update
- Güncelleme sonrası eval
- Eski sürüme rollback
- Revocation list
- CVE ve security advisory izlemesi

Güncelleme süreci:

```text
Yeni sürüm bulundu
  ↓
Değişiklik analizi
  ↓
İzin farkı analizi
  ↓
Dependency farkı
  ↓
Sandbox test
  ↓
Regression eval
  ↓
Security scan
  ↓
Canary deployment
  ↓
Tam yayın / rollback
```

---

# 24. Kendi kendini değiştirme sınırları

Agent aşağıdakileri kendi başına değiştirememelidir:

- Ana sistem prompt’u
- Güvenlik politikası
- İnsan onay kuralları
- Secret erişim kuralları
- Audit log ayarları
- Evaluator minimum skorları
- Production izinleri
- Broker risk limitleri
- Revocation list
- Kendi güvenlik tarayıcısını devre dışı bırakma

Agent yalnızca değişiklik önerisi oluşturabilir. Bu “constitutional boundary” ayrı, salt-okunur ve imzalı bir policy dosyasında tutulmalıdır.

---

# 25. Örnek uçtan uca senaryo: Bilinmeyen bir test teknolojisi

Kullanıcı:

> “Bu projeye yeni nesil browser accessibility test sistemi ekle.”

Akış:

1. Supervisor görevi `software_testing/accessibility` olarak sınıflandırır.
2. Registry’de accessibility Skill’i aranır.
3. Mevcut Skill yoksa Gap Detector bunu işaretler.
4. Capability Manager resmî kaynakları araştırır.
5. Playwright, axe-core ve ilgili resmî dokümanları bulur.
6. Uygun MCP gerekip gerekmediğine karar verir.
7. Yerel Playwright + axe-core’un yeterli olduğunu belirler.
8. `web-accessibility-testing` Skill taslağı üretir.
9. Sandbox’ta örnek uygulamaya uygular.
10. Bilinen accessibility hatalarını bulup bulmadığını test eder.
11. Prompt injection içeren test sayfasında güvenlik deneyi yapar.
12. Skill başarı puanı eşik üzerindeyse `sandbox-validated` olarak eklenir.
13. Gerçek projede branch üzerinde uygulanır.
14. Test Engineer ve Code Reviewer sonucu doğrular.
15. Başarılı kullanım sonrası Skill `project-approved` olur.

---

# 26. Örnek uçtan uca senaryo: Yeni trading indikatörü

Kullanıcı:

> “Pine Script’te bulunan özel indikatörü Python ve Freqtrade’e taşı.”

Akış:

1. Indicator Specification Skill çağrılır.
2. Pine hesaplama kuralları çıkarılır.
3. Warm-up, repaint ve bar kapanış davranışı incelenir.
4. Mevcut Pine/Freqtrade Skill’i yetersizse yeni Skill araştırılır.
5. Freqtrade resmî repo ve dokümantasyonu kullanılır.
6. Python implementasyonu saf fonksiyon olarak yazılır.
7. Pine sonuçları golden dataset ile karşılaştırılır.
8. Future candle erişimi taranır.
9. Backtest Integrity Skill devreye girer.
10. Komisyon ve slippage eklenir.
11. Out-of-sample ve parametre hassasiyeti test edilir.
12. Paper trading dışında emir yetkisi verilmez.
13. Başarılı prosedür `pine-to-freqtrade-indicator` Skill’i olarak saklanır.

---

# 27. Dosya ve klasör mimarisi

```text
ai-capability-platform/
├── core/
│   ├── supervisor/
│   ├── capability_manager/
│   ├── policy_engine/
│   ├── permission_broker/
│   └── memory_curator/
├── registry/
│   ├── skills/
│   ├── mcp/
│   ├── tools/
│   ├── models/
│   └── revoked/
├── skills/
│   ├── software/
│   ├── testing/
│   ├── security/
│   ├── finance/
│   ├── trading/
│   └── generated/
├── evaluators/
│   ├── functional/
│   ├── security/
│   ├── domain/
│   └── regression/
├── policies/
│   ├── immutable-core.yaml
│   ├── permissions.yaml
│   ├── trading.yaml
│   └── approvals.yaml
├── sandbox/
│   ├── containers/
│   ├── network-policies/
│   └── fixtures/
├── workflows/
│   ├── acquire-capability.yaml
│   ├── software-task.yaml
│   ├── research-task.yaml
│   └── trading-task.yaml
├── audit/
├── docs/
└── tests/
```

---

# 28. Örnek Capability Acquisition pseudocode

```python
def ensure_capability(task, context):
    requirements = analyze_capability_requirements(task, context)
    matches = registry.search(requirements)

    approved = [
        item for item in matches
        if item.status in {"project-approved", "production-approved"}
        and item.validation_score >= requirements.min_score
        and item.permissions.is_compatible(context.policy)
    ]

    if approved:
        return select_best(approved)

    candidates = discover_candidates(
        requirements=requirements,
        sources=[
            "official_docs",
            "official_github",
            "agent_skills_registry",
            "mcp_registry",
            "curated_repositories",
        ],
    )

    ranked = rank_candidates(candidates)

    for candidate in ranked:
        provenance = verify_provenance(candidate)
        if not provenance.passed:
            continue

        static_result = security_scan(candidate)
        if static_result.has_critical_findings:
            registry.revoke_or_reject(candidate, static_result)
            continue

        staged = install_in_ephemeral_sandbox(candidate)

        functional = run_functional_evals(staged, requirements)
        security = run_adversarial_evals(staged)
        permissions = analyze_runtime_permissions(staged)

        decision = policy_engine.decide(
            candidate=candidate,
            functional=functional,
            security=security,
            permissions=permissions,
            task_risk=requirements.risk_level,
        )

        if decision == "auto_approve":
            return registry.add(staged, status="sandbox-validated")

        if decision == "human_approval":
            return create_approval_package(
                candidate, functional, security, permissions
            )

    generated = skill_builder.create_from_primary_sources(requirements)
    return validate_generated_skill(generated)
```

---

# 29. Onay paketi

İnsan onayı gereken durumda kullanıcıya ham teknik karmaşa yerine şu özet sunulmalıdır:

```markdown
## Eklenmek istenen kabiliyet
GitHub MCP Server

## Neden gerekli?
Repository issue, PR ve dosyalarını güvenilir şekilde okuyup branch/PR oluşturmak.

## Kaynak
Resmî GitHub organizasyonu

## İstenen izinler
- Seçili repolarda okuma
- Branch oluşturma
- Commit gönderme
- PR açma

## Yasaklanan izinler
- Main branch’e push
- PR merge
- Repo silme
- Organization yönetimi

## Test sonucu
- Fonksiyonel: 18/18
- Güvenlik: kritik bulgu yok
- Prompt injection: engellendi
- Secret sızıntısı: engellendi

## Risk
Orta

## Öneri
Seçili repository ve sınırlı token ile onayla.
```

---

# 30. Uygulama yol haritası

## Faz 1 — Güvenli temel

- Skill standardını seç
- Capability Registry oluştur
- Supervisor ve Gap Detector geliştir
- Sandbox kur
- Policy Engine oluştur
- Audit log ekle
- 30 temel yazılım/test Skill’i
- 20 finans/trading Skill’i
- İnsan onay ekranı
- GitHub ve browser için salt-okunur araçlar

## Faz 2 — Araştırma ve adaptasyon

- GitHub/Skill/MCP discovery agent
- Aday puanlama
- Otomatik statik tarama
- Skill Creator
- Fonksiyonel eval runner
- Snyk Agent Scan / benzeri tarama entegrasyonu
- MCP Inspector entegrasyonu
- Güncelleme ve rollback

## Faz 3 — Kontrollü otonomi

- Düşük riskli Skill’lerin otomatik sandbox kurulumu
- Başarılı görevlerden Skill çıkarma
- Proje bazlı Skill öğrenme
- Çoklu evaluator
- Canary deployment
- Periyodik revalidation

## Faz 4 — Uzman ekipler

- Yazılım geliştirme multi-agent workflow
- Güvenlik review workflow
- Finansal analiz workflow
- Quant araştırma ve backtest audit
- Paper trading workflow
- Model routing ve uzman model seçimi

## Faz 5 — Üretim olgunluğu

- SBOM ve supply-chain kontrolleri
- Signed artifacts
- Kurumsal RBAC
- Merkezi secret broker
- Gözlemlenebilirlik
- Maliyet ve latency optimizasyonu
- Incident response
- Capability revocation

---

# 31. Başlangıç için önerilen teknoloji yığını

| Katman | Öneri |
|---|---|
| Agent orchestration | LangGraph |
| Kod ve sandbox agent altyapısı | OpenHands |
| Skill formatı | Agent Skills |
| MCP discovery | Resmî MCP Registry |
| MCP geliştirme | MCP Python/TypeScript SDK |
| MCP test | MCP Inspector |
| GitHub erişimi | GitHub MCP Server |
| Skill/MCP güvenlik taraması | Snyk Agent Scan + özel kurallar |
| Model red-team | NVIDIA garak |
| Container sandbox | Docker/Podman + seccomp/AppArmor |
| Policy engine | Open Policy Agent veya özel deny-by-default motor |
| Registry | PostgreSQL + object storage + vector index |
| Workflow state | PostgreSQL/Redis |
| Observability | OpenTelemetry |
| Secrets | Vault veya cloud secret manager |
| Quant araştırma | Qlib |
| Kripto strateji/backtest | Freqtrade |
| Exchange adapter | CCXT |
| Browser test | Playwright |
| Kod güvenliği | Semgrep, CodeQL, dependency scanners |
| Python eval | Pytest tabanlı harness |

---

# 32. Önerilen temel politika

```yaml
system:
  default_action: deny
  autonomous_research: allowed
  autonomous_download_to_sandbox: allowed
  autonomous_permanent_install: risk_based
  autonomous_policy_change: denied
  autonomous_secret_access: denied
  audit_logging: mandatory

capability_installation:
  low_risk:
    human_approval: false
    sandbox_eval: mandatory
  medium_risk:
    human_approval: true
  high_risk:
    human_approval: true
    independent_security_review: mandatory
  critical_risk:
    autonomous_install: denied

production:
  direct_write: denied
  deployment: approval_required
  database_migration: approval_required
  destructive_action: approval_required

trading:
  research: allowed
  backtest: allowed
  paper_trade: approval_required
  live_trade: explicit_approval_required
  withdrawal: denied
  risk_limit_change_by_agent: denied
```

---

# 33. Başarı ölçütleri

Sistem yalnızca kaç Skill kurduğuna göre ölçülmemelidir.

## Operasyonel KPI’lar

- Görev başarı oranı
- İlk seferde doğru çözüm oranı
- İnsan düzeltme ihtiyacı
- Test geçme oranı
- Güvenlik ihlali sayısı
- Yanlış tool seçimi
- Tool hata oranı
- Skill reuse oranı
- Skill edinme süresi
- Reddedilen zararlı aday sayısı
- Rollback oranı
- Token ve hesaplama maliyeti
- Kaynak doğruluğu
- Hallüsinasyon oranı

## Trading için ek KPI’lar

- Backtest audit fail oranı
- Look-ahead yakalama oranı
- Paper/live sapması
- Slippage model doğruluğu
- Risk limiti ihlali
- Strateji bozulmasını fark etme süresi
- Yanlış/istenmeyen emir sayısı

---

# 34. Nihai tasarım kararı

Önerilen yapı üç seviyeli olmalıdır:

## Seviye 1 — Bilinen işi doğru yap

Mevcut, doğrulanmış Skill ve tool’ları kullan.

## Seviye 2 — Eksik kabiliyeti güvenli şekilde edin

Araştır, karşılaştır, tara, sandbox’ta test et ve izin politikasına göre ekle.

## Seviye 3 — Yeni uzmanlık üret

Skill bulunmuyorsa birincil kaynaklardan kendi Skill’ini oluştur, evaluator geliştir ve deneysel olarak kaydet.

Ana kural:

> “Hemen bulup kendisine ekleme” davranışı doğrudan production kurulumu şeklinde değil; **hemen araştır, hemen sandbox’a al, hemen test et, risk uygunsa ekle; değilse onay iste veya reddet** şeklinde uygulanmalıdır.

Bu tasarım sayesinde sistem:

- Yeni alanlarda kendini geliştirebilir
- Bilmediği konuları fark edebilir
- Güncel Skill ve MCP’leri araştırabilir
- Araçlarını görev bazlı genişletebilir
- Deneyimlerini yeniden kullanılabilir becerilere dönüştürebilir
- Kalitesiz veya zararlı eklentilerden korunabilir
- Yazılım, test, güvenlik, finans ve trading süreçlerinde uzman prosedürleri zorunlu kılabilir

---

# 35. Referans GitHub depoları

## Agent Skills ve Skill keşfi

- https://github.com/agentskills/agentskills
- https://github.com/anthropics/skills
- https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md
- https://github.com/vercel-labs/skills/blob/main/skills/find-skills/SKILL.md
- https://github.com/VoltAgent/awesome-agent-skills
- https://github.com/trailofbits/skills
- https://github.com/trailofbits/skills-curated

## MCP

- https://github.com/modelcontextprotocol
- https://github.com/modelcontextprotocol/servers
- https://github.com/modelcontextprotocol/registry
- https://github.com/modelcontextprotocol/inspector
- https://github.com/modelcontextprotocol/python-sdk
- https://github.com/github/github-mcp-server
- https://github.com/punkpeye/awesome-mcp-servers

## Agent altyapıları

- https://github.com/langchain-ai/langgraph
- https://github.com/OpenHands/OpenHands
- https://github.com/SWE-agent/SWE-agent
- https://github.com/langchain-ai/open_deep_research
- https://github.com/github/spec-kit

## Yaşam boyu öğrenme ve Skill library

- https://github.com/MineDojo/Voyager
- https://arxiv.org/abs/2305.16291
- https://github.com/DataArcTech/Awesome-Agent-Skill-Papers

## Güvenlik

- https://github.com/snyk/agent-scan
- https://github.com/NVIDIA/garak
- https://github.com/trailofbits/overtly-malicious-skills
- https://github.com/Puliczek/awesome-mcp-security
- https://github.com/trailofbits/skills

## Yazılım test ve geliştirme

- https://github.com/microsoft/playwright-mcp
- https://github.com/qodo-ai/qodo-cover
- https://github.com/addyosmani/agent-skills

## Finans ve trading

- https://github.com/microsoft/qlib
- https://github.com/freqtrade/freqtrade
- https://github.com/ccxt/ccxt
- https://github.com/AI4Finance-Foundation/FinRL
- https://github.com/AI4Finance-Foundation/FinRobot
- https://github.com/TauricResearch/TradingAgents

---

# 36. Sonuç

Bu proje klasik bir chatbot veya yalnızca kod yazan agent değildir. Doğru tanımı:

> **Kabiliyet eksiklerini fark eden, güvenilir uzman prosedürleri ve araçları araştıran, bunları güvenli sandbox ortamında doğrulayan, politika sınırları içinde kendine adapte eden ve zaman içinde sürümlü bir uzmanlık kütüphanesi oluşturan otonom AI çalışma platformu.**

En kritik mühendislik kararı, otonomi ile kontrol arasındaki dengedir. Araştırma, karşılaştırma, Skill taslağı üretme ve sandbox testlerinde yüksek otonomi verilebilir. Ancak kalıcı kurulum, geniş yetkili MCP bağlantısı, production değişikliği, veri silme, e-posta gönderme, canlı trading ve güvenlik politikası değişikliği gibi işlemler deny-by-default ve onay kontrollü olmalıdır.

Bu yapıyla model “her şeyi bildiğini sanan” bir sistem değil; **neyi bilmediğini tespit eden, doğru uzmanlığı edinen ve öğrendiği şeyi kanıtlarla doğrulayan bir sistem** hâline gelir.
