# Mercek — Görev Uygulama Rehberi

Bu doküman `mercek-is-plani.md`'deki her görevin **nasıl** yapılacağını anlatır. Görev kodları ve sorumluluk numaraları ([n]) aynıdır. Her görev başlığının altında, o görevi Copilot'a yaptırmak için kullanılacak hazır prompt'un `mercek-copilot-promptlari.md` dosyasındaki kodu yazar. Önce bu rehberdeki bölümü okuyun (ne ve neden), sonra ilgili prompt'u kopyalayıp Copilot'a yapıştırın (nasıl). Rehberin tamamını Copilot'a bağlam olarak eklemeyin; prompt'lar kendi içinde yeterlidir.

> Hackathon öncesi kod yazılmıyor. Bu rehber yarın VDI'de uygulanacak adımları tarif eder; bugün okunup üzerinde konuşulabilir, pratik kişisel hesaplarla yapılabilir.

---

## 0. Önce bilinmesi gerekenler

### 0.1 Azure servisleri ve puan bağlantısı

AstreAI'ın "Azure Ortamı & Runtime" metriği (15 puan) **Azure Resource Graph ve canlı sağlık kontrolü** ile ölçülür: kaynak var mı, çalışıyor mu? Jüri de mimari slaytında gösterilen servislerin gerçekten çalışmasını bekler. Bu yüzden her servis **gerçek bir iş** yapmalı ve README'de amacı yazmalı.

| Servis | Mercek'teki işi | Puan bağlantısı | Zorunlu mu |
|---|---|---|---|
| **App Service (Linux)** | React arayüzü + API'yi tek uygulama olarak sunar, `/health` | Web App çalışıyor: 5 | Evet |
| **Azure AI Foundry** (kaynak + proje) | Model barındırma ve yönetimi | Foundry kaynağı: 3 | Evet |
| **Foundry model deploy'ları** | Sohbet modeli (sınıflandırma, özet, analiz) + embedding modeli (benzerlik) | Model deploy: 3 | Evet |
| **Azure SQL Database** | Ekranlar, loglar, çağrılar, talepler, takvim | Destek servisi: 4'ün parçası | Evet (mimari gereği) |
| **Azure AI Search** | Geçmiş çözümler, çağrılar ve taleplerde hibrit (vektör + metin) arama | Destek servisi: 4'ün parçası | Evet (mimari gereği) |
| Key Vault | Secret'ların kod/config dışında tutulması | Destek servisi (opsiyonel) | Opsiyonel — yetki ve süre varsa |
| Application Insights | İstek süreleri (Q3 iş değeri ölçümü), hata izleme | Destek servisi (opsiyonel) | Opsiyonel — Q3 için faydalı |

**Kural:** Kullanmayacağımız servisi (ör. Storage) açmıyoruz. Açılan her servis README tablosunda yer alır.

### 0.2 Teknoloji seçimi (önerilen)

| Konu | Öneri | Gerekçe |
|---|---|---|
| Backend | **Python 3.12 + FastAPI** | AI SDK'ları olgun, hızlı prototip, Pydantic ile şema doğrulama |
| Frontend | **React + Vite + TypeScript** | Joyride uyumu, hızlı build |
| Dağıtım | Frontend build'i backend'in `static/` klasörüne kopyalanır, **tek App Service** | Tek sağlık kontrolü, tek deploy, CORS derdi yok |
| SQL erişimi | `pyodbc` + ODBC Driver 18 (sorun çıkarsa Microsoft'un `mssql-python` sürücüsü) | App Service Linux Python imajında yaygın |
| AI erişimi | `openai` Python SDK (Azure istemcisi) ile Foundry'deki deploy | Structured output (JSON şeması) desteği |
| Arama | `azure-search-documents` | Hibrit arama + vektör |
| Test | `pytest` (backend), `vitest` (frontend) | CI'da hızlı |

Ekip .NET'te daha rahatsa aynı yapı ASP.NET Core ile kurulabilir; rehberdeki adımlar mantık olarak aynı kalır. **Karar 1. gün 10:30'da, ilk 10 dakikada verilir.**

### 0.3 Kimlik doğrulama: ideal yol ve yedek yol

Hackathon hesaplarının yetkisi resource group ile sınırlı. Bazı adımlar (rol ataması, Entra'da uygulama kaydı) yetki gerektirebilir. Her biri için yedek yol hazır:

| Konu | İdeal (ekstra güvenlik puanı) | Yedek (yetki yoksa) |
|---|---|---|
| App Service → SQL / AI Search / Foundry | **Managed Identity** + rol ataması (anahtarsız) | Anahtar/connection string **App Service ayarlarında** (repoda asla) |
| GitHub Actions → Azure | **OIDC** (federated credential) | App Service **publish profile**, GitHub Secret olarak |
| Secret saklama | Key Vault + App Settings Key Vault referansı | Sadece App Settings |

Yedek yol puan kaybettirmez; secret'ın repoya girmesi kaybettirir.

### 0.4 Copilot'u ucuz kullanma (her görev için geçerli)

- **Ucuz model** (Haiku / Flash sınıfı): boilerplate, test, YAML, SQL şema, küçük düzeltmeler, açıklama.
- **Orta model** (Sonnet sınıfı): RAG akışı, takvim algoritması, prompt + şema tasarımı, hata ayıklama.
- **Pahalı model** (Opus / büyük GPT sınıfı): sadece gerçekten takılınca.
- Copilot'a bütün repoyu değil, ilgili dosyayı ve bu rehberin ilgili bölümünü verin.
- **Büyük veri / uzun metin ürettirmeyin.** Veriyi üreten betiği yazdırın.

---

## A — Altyapı

### A1 — Repo iskeleti [16]

> 🤖 Copilot prompt'u: `mercek-copilot-promptlari.md` → **A1, A1-FE**

**Amaç:** Herkesin paralel çalışabileceği, değerlendirmeye uygun bir repo.

**Adımlar**
1. Takım reposunu klonla. `.github/workflows/` altındaki **CodeQL dosyasına dokunma**; sadece varlığını kontrol et.
2. Klasörleri oluştur:
   ```
   backend/        app/ (main.py, routers/, services/, repositories/, models/), tests/
   frontend/       src/ (bank-sim/, support-console/, request-assistant/, shared/)
   prompts/        *.md (her prompt ayrı dosya)
   data/           generator/ (betik), seed/ (senaryo kayıtları JSON), schema.sql
   sample-codebase/ (S2 için sentetik servis kodu ve SP'ler)
   docs/           mimari diyagram, karar notları
   .github/        copilot-instructions.md, pull_request_template.md, workflows/ci-cd.yml
   ```
3. `.gitignore`: `.env`, `__pycache__/`, `node_modules/`, `dist/`, `.venv/`. **`.github/` asla ignore edilmez.**
4. `.env.example`: yalnızca anahtar adları ve `<PLACEHOLDER>` değerleri (ör. `AZURE_OPENAI_ENDPOINT=<PLACEHOLDER>`).
5. `copilot-instructions.md` → `.github/`, `hackathon-teknik-kilavuz.md` → `docs/`.
6. PR şablonu: "Ne değişti / Nasıl test edildi / Secret içermiyor ✔ / İlgili görev kodu".
7. Backend katmanları: `routers` (HTTP) → `services` (iş mantığı) → `repositories` (SQL/Search) → `clients` (LLM). Bu ayrım LLM Judge'ın "mimari" puanına doğrudan yazılır.

**Kabul:** İskelet main'de, CodeQL dosyası değişmemiş, ilk CodeQL taraması temiz.

### A2 — CI/CD workflow [17]

> 🤖 Copilot prompt'u: `mercek-copilot-promptlari.md` → **A2**

**Amaç:** CI/CD metriğinin 15 puanı: kaliteli YAML (5), en az bir çalıştırma (5), son çalıştırma success (5).

**Dosya:** `.github/workflows/ci-cd.yml` (CodeQL dosyasından ayrı)

**Tetikleyiciler:** `pull_request` (main'e) ve `push` (main), ayrıca `workflow_dispatch` (elle çalıştırma).

**İşler (jobs)**
1. **`quality`** (PR + main):
   - Python kur, `pip install -r backend/requirements.txt`
   - `ruff check` (lint), `pytest` (test + coverage raporu)
   - `pip-audit` (bağımlılık açıkları)
   - Node kur, `npm ci`, `npm run lint`, `npm test`, `npm audit --audit-level=high`
   - **gitleaks** (secret taraması) — CodeQL değil, kural ihlali yok
2. **`build`** (quality'ye bağlı): frontend `npm run build` → çıktıyı `backend/static/`'e kopyala → backend'i zip'le → artifact olarak yükle.
3. **`deploy`** (sadece main push, build'e bağlı): artifact'ı indir → Azure'a giriş → `azure/webapps-deploy` ile App Service'e yükle → **deploy sonrası `/health` kontrolü** (curl, 200 değilse job başarısız).

**Azure girişi**
- İdeal: `azure/login` + OIDC. Entra'da uygulama kaydı + federated credential gerekir; GitHub Secrets'a `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`. `permissions: id-token: write`.
- Yedek: App Service → "Download publish profile" → GitHub Secret `AZURE_WEBAPP_PUBLISH_PROFILE`. (App Service'te SCM basic auth açık olmalı.)

**Kalite puanı için ipuçları:** Bağımlılık önbelleği (`cache: pip` / `cache: npm`), `concurrency` (aynı branch'te eski çalıştırmayı iptal), `permissions` en az yetki (`contents: read`), action'larda sabit sürüm, job'lar arası `needs`.

**Kabul:** PR'da `quality` yeşil, main'de deploy + health check yeşil.

**Dikkat:** Son çalıştırma success olmalı. 2. gün 12:00'den sonra main'e merge yok; zorunluysa merge sonrası pipeline'ın yeşil bittiğini görmeden bırakma.

### A3 — Azure kaynakları [18]

> 🤖 Copilot prompt'u: `mercek-copilot-promptlari.md` → **A3**

**Amaç:** Azure metriğinin 15 puanı + jürinin "gerçekten çalışıyor mu" sorusu.

Tüm kaynaklar **takımın resource group'unda**, aynı bölgede, anlamlı adlarla: `mercek-app`, `mercek-sql`, `mercek-search`, `mercek-foundry`.

**1. App Service**
- App Service Plan: Linux, B1 (veya izin verilen en düşük ücretli plan; F1 yavaş ve kısıtlı olabilir).
- Web App: Python 3.12 runtime.
- Başlangıç komutu: `gunicorn -k uvicorn.workers.UvicornWorker -w 2 app.main:app`
- **Configuration → General settings:** "Always On" açık (ilk istekte soğuk başlangıç olmasın), HTTPS only açık.
- **Health check** ayarı: `/health` yolu.
- Environment variables (App Settings): `AZURE_OPENAI_ENDPOINT`, `CHAT_DEPLOYMENT`, `EMBEDDING_DEPLOYMENT`, `SEARCH_ENDPOINT`, `SQL_SERVER`, `SQL_DATABASE` (+ yedek yolda anahtarlar).
- Managed Identity: "Identity → System assigned → On".

**2. Azure AI Foundry**
- Foundry kaynağı + proje oluştur.
- Model deploy et: **1 küçük sohbet modeli** (o gün katalogda olan mini sınıfı bir model) + **1 embedding modeli** (ör. text-embedding-3-small sınıfı). Deploy adlarını sabit tut: `chat`, `embedding`.
- Foundry playground'da kısa bir istekle "erişilebilir" olduğunu doğrula (metrik "deploy edilmiş ve erişilebilir" diyor).
- İdeal: Web App'in managed identity'sine Foundry kaynağında "Cognitive Services OpenAI User" rolü. Yedek: API anahtarı App Settings'te.

**3. Azure SQL Database**
- Logical server + veritabanı `mercekdb`. **Serverless** veya en düşük vCore/DTU; varsa ücretsiz teklif.
- Kimlik doğrulama: Entra yöneticisi olarak kendi kurumsal hesabın (yetki varsa) + SQL kimlik doğrulama yedek.
- Networking: "Allow Azure services and resources to access this server" açık; ekip VDI IP'leri için firewall kuralı (veri yüklemek için).
- İdeal: Web App managed identity için `CREATE USER [mercek-app] FROM EXTERNAL PROVIDER` + `db_datareader`, `db_datawriter`.

**4. Azure AI Search**
- Free tier yeterli olabilir (3 indeks, vektör destekli); kapasite yetmezse Basic.
- İndeksler: `solutions`, `incidents`, `requests` (A5'te tanımlanır).
- İdeal: managed identity + "Search Index Data Reader/Contributor" rolü (RBAC'ı servis ayarından aç). Yedek: query key App Settings'te, admin key sadece veri yükleme betiğinde ortam değişkeni olarak.

**5. (Opsiyonel) Application Insights** — Web App'e bağla, Q3 süre ölçümü ve hata izleme için.

**Kabul:** Portal'da tüm kaynaklar, `/health` 200, Foundry playground yanıt veriyor.

**Zaman kazandırıcı:** Kaynak oluşturmayı Portal yerine `az` CLI komutlarıyla `docs/azure-setup.md`'ye yazarak yap; tekrarlanabilir olur ve README'de referans verilir. (Bicep yazmaya vakit varsa daha da iyi — LLM Judge "infra as code" görür; ama zorunlu değil.)

### A4 — README [16]

> 🤖 Copilot prompt'u: `mercek-copilot-promptlari.md` → **A4**

**Bölümler**
1. Mercek nedir (tek cümle + slogan)
2. Mimari diyagram (Mermaid: kullanıcı → App Service → Foundry / SQL / AI Search)
3. **Azure kaynakları tablosu**: kaynak adı · tür · Mercek'teki amacı · kimlik doğrulama yöntemi
4. AI ne yapar / kod ne yapar tablosu (jüri ve LLM Judge için)
5. Yerel çalıştırma (`.env.example`'dan `.env`)
6. Sentetik veri: nasıl üretilir, nasıl yüklenir
7. Test ve CI/CD akışı
8. Güvenlik: secret yönetimi, PR'da tarama, gerçek veri yok

**Kabul:** README main'de ve her Azure kaynağı amacıyla listeli.

### A5 — Sentetik veri üretimi ve yükleme [5] [6]

> 🤖 Copilot prompt'u: `mercek-copilot-promptlari.md` → **A5-a, A5-b, A5-c, A5-d**

**Amaç:** Senaryoları taşıyan, tutarlı, tekrar üretilebilir veri. Ayrıntılı varlık listesi: `mercek-sentetik-veri-plani.md`.

**1. SQL şeması (`data/schema.sql`)**

| Tablo | Ana alanlar |
|---|---|
| `teams` | team_id, name, daily_capacity_md |
| `services` | service_id, name, team_id, description |
| `service_dependencies` | service_id, depends_on_service_id |
| `screens` | screen_id, name, module, flow_definition (JSON: adım listesi) |
| `screen_services` | screen_id, service_id |
| `screen_elements` | screen_id, element_id, label, type (Joyride hedefleri) |
| `field_standards` | field_name, data_type, format, validation, masking, example |
| `error_codes` | error_code, service_id, description, severity |
| `logs` | log_id, ts, session_id, screen_id, service_id, level, error_code, message |
| `incidents` | incident_id, created_at, screen_id, category, user_text, enriched_json, service_id, team_id, solution_id, resolution_minutes, status |
| `solutions` | solution_id, error_code, symptom, root_cause, steps, created_at |
| `requests` | request_id, type, screen_id, title, description, affected_services, effort_md, cost, start_date, end_date |
| `team_calendar` | team_id, date_from, date_to, allocation_pct, note |

**2. Üretim betiği (`data/generator/generate.py`)**
- `Faker('tr_TR')`, **sabit seed** (ör. 42) → her çalıştırmada aynı veri.
- Sabit referans veriler (ekranlar, servisler, ekipler, hata kodları) betikte sözlük olarak.
- Dağılımlar: logların %80'i INFO, hata kodları ekran–servis ilişkisine uygun; çağrı kategorileri ağırlıklı.
- **Senaryo kayıtları** `data/seed/scenarios.json`'dan okunur ve üretilen verinin üzerine eklenir (S1–S4'ün rakamları: 312 çağrı, %41 IBN-504, efor 15/17/19/22, takvim 9 Kasım'a kadar dolu…).
- Çıktı: tablolar için CSV veya doğrudan SQL insert.

**3. Doğal dil alanları (çağrı metinleri, çözüm metinleri, talep açıklamaları)**
- Ayrı bir betik Foundry'deki sohbet modeline **küçük partilerle** (ör. 20'şerli) şablon + 2 örnek vererek üretim yaptırır, sonucu JSON dosyasına yazar.
- Bu harcama Copilot bütçesine değil Azure aboneliğine yazılır.
- Üretilen metinler repoya commit'lenir (`data/seed/texts.json`); her seferinde yeniden üretmeye gerek kalmaz.
- Metinlerde gerçek kişi adı, TCKN, IBAN gibi gerçek görünümlü kişisel veri olmasın (Faker'ın ürettiği IBAN'lar bile maskelenmiş gösterilsin, ör. `TR** **** 1234`).

**4. Yükleme (`data/generator/load.py`)**
- SQL: şemayı uygula, tabloları doldur (bağlantı bilgisi ortam değişkeninden).
- AI Search: indeksleri oluştur ve doldur:
  - `solutions`: `id`, `error_code` (filtrelenebilir), `symptom`, `root_cause`, `steps`, `content` (birleşik metin), `content_vector` (embedding).
  - `incidents`: `id`, `screen_id`, `category`, `text`, `solution_id`, `text_vector`.
  - `requests`: `id`, `type`, `screen_id`, `title`, `description`, `effort_md`, `affected_services`, `desc_vector`.
  - Vektör alanı boyutu embedding modelinin boyutuyla aynı olmalı; HNSW vektör profili.
  - Embedding'leri betik Foundry'deki embedding deploy'u ile üretir (toplu, partiler halinde).

**Kabul:** `SELECT COUNT(*)` beklenen hacimleri veriyor; S1–S4 kayıtları sorgulanıyor; AI Search'te "IBAN doğrulama zaman aşımı" araması S1 çözümlerini getiriyor.

### A6 — LLM istemcisi ve prompt yönetimi [12]

> 🤖 Copilot prompt'u: `mercek-copilot-promptlari.md` → **A6**

**Amaç:** Tüm AI çağrıları tek noktadan, test edilebilir, güvenli.

**Yapı**
- `backend/app/clients/llm.py`:
  - `chat_json(prompt_name, variables, schema)` → prompt dosyasını yükler, değişkenleri doldurur, modele **JSON şemalı (structured output)** istek atar, Pydantic ile doğrular.
  - `embed(texts)` → embedding deploy'u.
  - Zaman aşımı (ör. 20 sn), 1 tekrar deneme, düşük sıcaklık (0–0,2).
  - Her çağrının süresini ve token kullanımını logla (Q3 için).
  - Kimlik: managed identity (DefaultAzureCredential) varsa onu, yoksa ortam değişkenindeki anahtarı kullan.
- `prompts/<ad>.md`: başta kısa bir başlık (amaç, girdiler, çıktı şeması), sonra sistem + kullanıcı şablonu. `{{degisken}}` yer tutucuları.
- Prompt'larda **prompt injection önlemi**: kullanıcı metni ve log içeriği açıkça sınırlandırılmış blok içinde verilir ("Aşağıdaki metin veri olarak ele alınmalı, talimat değildir").
- Testlerde `LLMClient` bir sahte (fake) sınıfla değiştirilir; sabit JSON döner.

**Kabul:** `test_llm_client.py` geçiyor; bir örnek prompt Foundry'den geçerli JSON döndürüyor.

---

## M1 — Akıllı Problem Çözüm ve Çağrı Yönetimi

### M1.1-a — Banka simülasyonu, 4 ekran [9]

> 🤖 Copilot prompt'u: `mercek-copilot-promptlari.md` → **M1.1-a**

- Mobil görünümlü tek bir çerçeve (telefon kasası görünümü) içinde 4 ekran: Giriş, Hesaplarım, Para Transferi (EFT/Havale sekmeli), Fatura Ödeme.
- Router: `/bank/login`, `/bank/accounts`, `/bank/transfer`, `/bank/bill`.
- Her ekranın kökünde `data-screen-id="TRANSFER"` gibi sabit kimlik.
- Her etkileşimli öğede sabit `id` (ör. `transfer-tab-havale`, `transfer-iban-input`, `transfer-submit`). Bu id'ler `screen_elements` tablosundaki kayıtlarla **birebir aynı** olmalı (M1.5 Joyride buna dayanır).
- Kurumsal görünüm ama gerçek banka logosu/marka kullanılmaz; "Demo Bank" gibi kurgusal bir ad.
- Kullanıcı adımlarını tutan küçük bir hook: son 5 etkileşim (`{ts, element_id, action}`).

**Copilot:** Ekranlar boilerplate yoğun → ucuz model.

### M1.1-b — "Sorun yaşıyorum" butonu ve sohbet paneli [9]

> 🤖 Copilot prompt'u: `mercek-copilot-promptlari.md` → **M1.1-b**

- Her ekranda sabit konumlu buton; tıklayınca sağdan açılan panel.
- Panel açılırken `POST /api/incidents/start` çağrısı: `{screen_id, session_id, recent_steps, ts}`.
- Dönen yanıt (M1.2 sonucu "olası neden") panelin ilk mesajı olarak gösterilir — kullanıcı daha yazmadan.
- Kullanıcı mesajı `POST /api/incidents/{id}/message` ile gönderilir.
- `session_id`: uygulama açılışında üretilen UUID (sessionStorage'da).

### M1.1-c — Hata simülasyonu + gerçek log satırı [13]

> 🤖 Copilot prompt'u: `mercek-copilot-promptlari.md` → **M1.1-c**

- `POST /api/bank/transfer` uç noktası: senaryo modunda EFT isteğine hata döner **ve** `logs` tablosuna `IBN-504` kodlu, o `session_id` ve `TRANSFER` ekranına ait gerçek bir satır yazar (birkaç saniye arayla 2–3 satır: WARN timeout, ERROR IBN-504).
- Hata tetikleme kuralı deterministik: ör. tutar > 1.000 ve tür EFT ise ya da bir "demo modu" bayrağı açıksa. Demoda sürpriz olmasın.
- Fatura Ödeme için benzer şekilde S2 hatası (yuvarlama) — 100,005 TL girişinde 100,00 ödenir ve uyarı logu yazılır.

**Neden önemli:** Jüri "anlık log kontrolü gerçekten var mı?" diye bakarsa SQL'de az önce oluşan satır görünür.

### M1.1-d — `POST /api/incidents/start` [13]

> 🤖 Copilot prompt'u: `mercek-copilot-promptlari.md` → **M1.1-d**

- Girdi: `screen_id`, `session_id`, `recent_steps`, `ts`. Pydantic ile doğrula (izinli ekran listesi, uzunluk sınırları).
- `incidents` tablosuna `status='draft'` kayıt aç.
- M1.2 servisini çağır, sonucu döndür: `{incident_id, screen_name, probable_cause, confidence}`.

### M1.2-a — Log getirme ve gruplama [13]

> 🤖 Copilot prompt'u: `mercek-copilot-promptlari.md` → **M1.2-a**

- SQL (parametreli!): son 15 dakika, `session_id` eşleşen VEYA aynı `screen_id`'de son 15 dakikadaki ERROR/WARN.
- Kodda grupla: `error_code` → adet, ilk/son zaman, servis, örnek mesaj.
- En ağırlıklı grup (session'a ait ERROR önce) "baskın hata" olarak seçilir.
- Log yoksa: "Şu an sistemde bir hata görünmüyor" yolu (AI çağrısı yok → maliyet de yok).

### M1.2-b — Prompt `log-ozet` [12]

> 🤖 Copilot prompt'u: `mercek-copilot-promptlari.md` → **M1.2-b**

- Girdi: ekran adı, gruplanmış loglar (en fazla 10 satır, maskeli), hata kodu açıklaması (`error_codes` tablosundan).
- Çıktı şeması: `{user_message, technical_summary, probable_cause, suggested_user_action, confidence}`.
- Kurallar: kullanıcı mesajı en fazla 2 cümle, teknik terim yok, suçlayıcı dil yok; teknik özet destek ekibi için.
- Girdiye gerçek hata kodu açıklaması verildiği için model uydurmaya daha az yönelir.

### M1.2-c — "Olası neden" kartı [10]

> 🤖 Copilot prompt'u: `mercek-copilot-promptlari.md` → **M1.2-c**

- Panelde ilk mesaj olarak kart: ikon + kullanıcı mesajı + "Bana göster" (M1.5) + "Yine de çağrı aç".
- Destek Konsolu'nda aynı bilginin teknik özeti görünür.

### M1.3-a — Prompt `cagri-zenginlestir` [12] [13]

> 🤖 Copilot prompt'u: `mercek-copilot-promptlari.md` → **M1.3-a**

- Girdi: kullanıcı metni, ekran, son adımlar, baskın hata grubu, `log-ozet` çıktısı.
- Çıktı şeması: `{title, category (enum), priority (enum), summary, steps_to_reproduce[], log_refs[], customer_impact}`.
- Kategori ve öncelik **enum** olarak şemada sabit (model listede olmayan değer üretemez).
- Sonuç `incidents.enriched_json`'a yazılır, `status='open'`.

### M1.3-b — Servis ve ekip tespiti [13]

> 🤖 Copilot prompt'u: `mercek-copilot-promptlari.md` → **M1.3-b**

- **Kural katmanı (kod):** `error_code → service_id` (error_codes tablosu) → `service_id → team_id`. Hata kodu yoksa `screen_id → screen_services`.
- Kural tek servis veriyorsa: AI yok, doğrudan atama. Birden çok aday varsa: AI'a aday listesi + çağrı özeti verilir, **yalnızca listeden** seçmesi ve gerekçe yazması istenir.
- Yanıtta `assignment_method: "rule" | "ai"` alanı → Destek Konsolu'nda rozet olarak görünür (jüriye "AI nerede, kural nerede" kanıtı).

### M1.3-c — Destek Konsolu çağrı kartı [10]

> 🤖 Copilot prompt'u: `mercek-copilot-promptlari.md` → **M1.3-c**

- Liste: açık çağrılar (numara, başlık, öncelik, ekip, oluşma zamanı).
- Detay: sol tarafta "Kullanıcının yazdığı" (tek cümle), sağ tarafta "Mercek'in oluşturduğu" kayıt → önce/sonra etkisi.
- Log referansları tıklanınca ilgili log satırları (Kibana benzeri tablo görünümü).

### M1.4-a — Hibrit arama ve eşik [14]

> 🤖 Copilot prompt'u: `mercek-copilot-promptlari.md` → **M1.4-a**

- Sorgu metni: `title + summary + error_code`.
- AI Search'te `solutions` ve `incidents` indekslerinde **hibrit sorgu** (metin + vektör), `error_code` eşleşirse filtre/boost.
- İlk 3 sonuç + skor. Skoru 0–1'e normalize et (hibrit skorlar ham haliyle karşılaştırılamaz; reranker skoru veya basit min-max).
- Eşik kodda sabit: ≥ 0,75 "eşleşme var", altı "eşleşme yok". Eşik değeri README'de ve konsolda görünür.
- Demo öncesi S1 ve S2 ile kalibre et (S1 yüksek, S2 düşük çıkmalı).

### M1.4-b — Prompt `cozum-uyarla` [14]

> 🤖 Copilot prompt'u: `mercek-copilot-promptlari.md` → **M1.4-b**

- Girdi: yeni çağrı özeti + eşleşen 1–3 çözüm (kök neden, adımlar) + kaynak çağrı numaraları.
- Çıktı: `{adapted_steps[], why_it_matches, source_ids[], risk_notes}`.
- Kural: kaynakta olmayan adım uydurma; emin olunmayan yer `risk_notes`'a.
- Konsolda kaynak çağrılar tıklanabilir (güven için).

### M1.4-c — Kod analizi (eşleşme yoksa) [14]

> 🤖 Copilot prompt'u: `mercek-copilot-promptlari.md` → **M1.4-c**

- `docs/` değil `sample-codebase/` içinde küçük bir harita dosyası: `service_id → [dosya yolları]`.
- İlgili servisin 2–3 dosyası (toplam birkaç yüz satırı aşmayacak şekilde) satır numaralarıyla prompta verilir.
- Prompt `kod-analiz` çıktısı: `{suspected_file, line_range, root_cause, fix_suggestion_diff, test_suggestion, confidence}`.
- Konsolda dosya görünümünde ilgili satırlar vurgulanır, diff yan yana gösterilir.
- Önemli: Mercek **öneri** sunar; düzeltmeyi uygulamaz (kapsam dışı ve S-C'de güvence).

### M1.4-d — `sample-codebase/` [6]

> 🤖 Copilot prompt'u: `mercek-copilot-promptlari.md` → **M1.4-d**

- `FaturaOdemeService.cs` (veya .py) + `sp_FaturaTutarHesapla.sql` + `sp_FaturaListele.sql` + `IbanDogrulamaClient.cs` + 2–3 alakasız dosya.
- Gömülü hata: tutarı iki haneye **yuvarlamak yerine kesen** satır (ör. `ROUND(@Tutar, 2, 1)` — üçüncü parametre kesme yapar). Doğrusu `ROUND(@Tutar, 2)`.
- Dikkat dağıtıcı dosyalar makul görünmeli ama hatasız olmalı.
- Bu klasör kasıtlı hatalı kod içerir → **CodeQL'in bunu bulgu olarak işaretleyip işaretlemeyeceğini düşünün.** Mantık hatası (yuvarlama) güvenlik bulgusu değildir; ama SQL injection gibi güvenlik açığı **asla** gömülmez. Dosyanın başına "Demo amaçlı sentetik koddur" yorumu ekleyin.

### M1.4-e — Eşleşme ve kod analizi görünümü [10]

> 🤖 Copilot prompt'u: `mercek-copilot-promptlari.md` → **M1.4-e**

- Eşleşme varsa: skor çubuğu, kaynak çağrılar, uyarlanmış adımlar.
- Eşleşme yoksa: "Geçmişte benzer kayıt bulunamadı (en yüksek %41) → kod analizi" geçişi görsel olarak anlatılmalı (demo anı).

### M1.5-a — Prompt `joyride-adim` [14]

> 🤖 Copilot prompt'u: `mercek-copilot-promptlari.md` → **M1.5-a**

- Girdi: çözümün kullanıcıya dönük kısmı (`suggested_user_action`) + ilgili ekranın `screen_elements` listesi (id + etiket).
- Çıktı: `{steps: [{target: element_id, content: string}]}` (en fazla 5 adım).
- **Doğrulama kodda:** listede olmayan `target` atılır; adım kalmazsa tur gösterilmez.

### M1.5-b — Joyride turu [9]

> 🤖 Copilot prompt'u: `mercek-copilot-promptlari.md` → **M1.5-b**

- `react-joyride` ile adımları `#element_id` hedeflerine bağla, "Bana göster" ile başlat.
- Tur gerektiğinde ekranlar arası geçiş yapar (ör. Hesaplarım → Para Transferi → Havale sekmesi).
- React sürüm uyumluluğunu bugün pratikte kontrol edin; sorun çıkarsa `driver.js` aynı işi görür.

---

## M2 — Akıllı Talep Analizi, Maliyet ve Takvim Planlama

### M2.1-a — Prompt `talep-siniflandir` [15]

> 🤖 Copilot prompt'u: `mercek-copilot-promptlari.md` → **M2.1-a**

- Girdi: talep metni + ekran kataloğu (id, ad, kısa açıklama).
- Çıktı: `{type: "existing_change" | "new_screen", screen_id | null, confidence, rationale}`.
- `screen_id` yalnızca katalogdan; değilse null. Güven düşükse arayüz "Hangi ekranla ilgili?" diye sorar (kullanıcı onayı).

### M2.1-b — Talep Asistanı giriş ekranı [11]

> 🤖 Copilot prompt'u: `mercek-copilot-promptlari.md` → **M2.1-b**

- Serbest metin kutusu + örnek talepler (demo için tek tıkla doldurma).
- Sonuç kartı: tip rozeti, ekran adı, güven; sonra M2.4–M2.6 kartları sırayla.

### M2.2-a / b — Akış önerisi (Could) [15] [11]

> 🤖 Copilot prompt'u: `mercek-copilot-promptlari.md` → **M2.2-a, M2.2-b**

- `screens.flow_definition` (adım listesi) + talep → prompt `akis-oneri` → `{steps: [{name, status: "same" | "changed" | "new"}]}`.
- Arayüzde iki sütun: mevcut akış / önerilen akış, değişen adımlar renkli.

### M2.3-a — Soru bankası ve alan standartları [7]

> 🤖 Copilot prompt'u: `mercek-copilot-promptlari.md` → **M2.3-a**

- `data/seed/questions.json`: 10–15 soru; her biri `{id, text, purpose, answer_type, applies_when}`.
- `field_standards` tablosu: Müşteri No, IBAN, Tutar, Tarih, Döviz kodu, Kur, Telefon, E-posta… her biri format, doğrulama, maskeleme, örnek.
- Bu iş analistin uzmanlığı; bugün metin olarak hazırlanabilir.

### M2.3-b — Prompt `sonraki-soru` [15]

> 🤖 Copilot prompt'u: `mercek-copilot-promptlari.md` → **M2.3-b**

- Her turda girdi: talep + şimdiye kadarki soru-cevaplar + soru bankası.
- Çıktı: `{done: false, next_question_id, adapted_text}` veya `{done: true, scope_summary, fields: [{name, standard_ref, notes}]}`.
- En fazla 5 soru sınırı **kodda** (6. turda zorla `done`).
- Alan önerileri `field_standards`'ta olan alanlara bağlanır (`standard_ref`); olmayan alan "yeni standart gerekli" olarak işaretlenir.

### M2.3-c — Sihirbaz arayüzü [11]

> 🤖 Copilot prompt'u: `mercek-copilot-promptlari.md` → **M2.3-c**

- Adım adım soru kartları, ilerleme göstergesi, sonunda kapsam özeti + alan tablosu (alan, tip, format, doğrulama, maskeleme).
- "Kapsamı kopyala" butonu (talep dokümanına yapıştırılabilir).

### M2.4-a — Bağımlılık grafiği [15]

> 🤖 Copilot prompt'u: `mercek-copilot-promptlari.md` → **M2.4-a**

- SQL: `screen_services` → doğrudan servisler; `service_dependencies` ile 1 seviye bağımlılar (özyinelemeli CTE veya kodda BFS, derinlik ≤ 2).
- Çıktı: `{direct: [...], indirect: [...]}`.

### M2.4-b — AI ile filtreleme [15]

> 🤖 Copilot prompt'u: `mercek-copilot-promptlari.md` → **M2.4-b**

- Girdi: talep + aday servisler (açıklamalarıyla).
- Çıktı: `{affected: [{service_id, reason, impact: "high"|"medium"|"low"}]}` — **sadece aday listesinden**.

### M2.4-c — Etkilenen servis listesi [11]

> 🤖 Copilot prompt'u: `mercek-copilot-promptlari.md` → **M2.4-c**

- Servis adı, ekip, etki seviyesi rozeti, gerekçe. Zaman kalırsa küçük bir bağımlılık grafiği (Could).

### M2.5-a — Benzer talepler ve efor [15]

> 🤖 Copilot prompt'u: `mercek-copilot-promptlari.md` → **M2.5-a**

- AI Search `requests` indeksinde hibrit arama, `type` ve (varsa) `screen_id` filtresi/boost'u, ilk 5.
- Kodda: efor medyanı, min–max aralığı (aykırı tek değer varsa çeyrekler arası).
- Benzer talep bulunamazsa: "Yeterli geçmiş veri yok" — AI tahmin **üretmez** (S-C güvencesi).

### M2.5-b — Maliyet [15]

> 🤖 Copilot prompt'u: `mercek-copilot-promptlari.md` → **M2.5-b / c**

- `maliyet = medyan_efor × GUNLUK_MALIYET` — parametre config'de (ör. `DAILY_COST_TRY`), arayüzde "varsayım" etiketiyle görünür. Gerçek kurum rakamı kullanılmaz.

### M2.5-c — Takvim [15]

> 🤖 Copilot prompt'u: `mercek-copilot-promptlari.md` → **M2.5-b / c**

- Etkilenen servislerin ekiplerinden **ana ekip** (en yüksek etki) seçilir.
- `team_calendar`'dan ekibin doluluk aralıkları; bugünden itibaren boş kapasite gün gün hesaplanır (`(100 - allocation_pct) × daily_capacity`).
- İlk boş gün = başlangıç; efor kümülatif boş kapasiteyle karşılanınca = bitiş. Hafta sonu atlanır.
- Saf fonksiyon olarak yaz → birim testi kolay (Q1 ve LLM Judge'ın test puanı).

### M2.5-d — Prompt `tahmin-gerekce` [15]

> 🤖 Copilot prompt'u: `mercek-copilot-promptlari.md` → **M2.5-d**

- Girdi: hesap sonuçları (efor aralığı, benzer talepler, takvim) — **sayılar sabit**.
- Çıktı: `{explanation, assumptions[], risks[]}`. Prompt: "Sayıları değiştirme, sadece açıkla."

### M2.5-e — Tahmin kartı [11]

> 🤖 Copilot prompt'u: `mercek-copilot-promptlari.md` → **M2.5-e**

- Efor aralığı + medyan, maliyet (varsayım etiketi), başlangıç–bitiş, benzer talepler (tıklanabilir), gerekçe.
- Basit zaman çizelgesi (ekip doluluğu + yeni iş çubuğu).

### M2.6-a — Ekranın çağrı istatistikleri [15]

> 🤖 Copilot prompt'u: `mercek-copilot-promptlari.md` → **M2.6-a**

- SQL: son 30 gün `incidents` → `screen_id` için toplam, kategori dağılımı, en sık 3 `error_code` ve bağlı `solutions`.
- Her sorun için kalıcı çözüm eforu: ilgili çözümün kaydındaki tahmini düzeltme eforu (veride tanımlı, ör. IBN-504 için 3 adam-gün).

### M2.6-b — "Kapsama ekle" etkileşimi [11] [15]

> 🤖 Copilot prompt'u: `mercek-copilot-promptlari.md` → **M2.6-b**

- Tahmin kartının altında: "Bu ekran son 30 günde 312 çağrı aldı" + kategori dağılımı (küçük çubuk grafik) + seçilebilir sorunlar.
- Seçim → `POST /api/requests/{id}/recalculate` → efor ve takvim yeniden (M2.5-c fonksiyonu tekrar) → kart güncellenir, fark vurgulanır (+3 adam-gün, bitiş 4 Aralık → 9 Aralık).

---

## Q — Kalite, ölçüm ve teslim

### Q1 — Birim testleri [19]

> 🤖 Copilot prompt'u: `mercek-copilot-promptlari.md` → **Q1**

- Öncelikli test edilecekler (deterministik, değerli): log gruplama, servis/ekip kural ataması, eşik kararı, efor medyan/aralık, takvim hesaplama, soru limiti, Joyride hedef doğrulama, Pydantic şemaları.
- AI çağrıları sahte istemciyle; testler internet ve Azure gerektirmez (CI'da hızlı ve kararlı).
- Hedef: kritik iş mantığında anlamlı kapsam; LLM Judge test klasörünün varlığına ve kalitesine bakar.
- Frontend: en az birkaç bileşen testi (vitest + testing-library).

### Q2 — Senaryo testleri [8]

> 🤖 Copilot prompt'u: `mercek-copilot-promptlari.md` → **Q2**

- `docs/demo-scenarios.md`: S1–S4 için girdi ve **beklenen çıktı** (ekip, kategori, skor aralığı, efor aralığı, tarihler).
- Her büyük merge'den sonra canlı ortamda S1–S4 elle koşulur, sapmalar not edilir.
- AI çıktısının doğruluğu (yanlış ekip, uydurma adım) burada yakalanır → prompt düzeltilir.

### Q3 — Süre ölçümü [13] [15] → [3]

> 🤖 Copilot prompt'u: `mercek-copilot-promptlari.md` → **Q3**

- Her uç noktada toplam süre ve AI çağrı süresi loglanır (Application Insights varsa otomatik, yoksa `logs`/ayrı tablo).
- Sunuma girecek rakamlar: "Sorun tespiti X sn", "Çağrı zenginleştirme Y sn", "Efor tahmini Z sn", "Çağrı başına tahmini AI maliyeti".

### Q4 — Security sekmesi [17]

> 🤖 Copilot prompt'u: `mercek-copilot-promptlari.md` → **Q4 (bulgu düzeltme yardımı)**

- Her main merge sonrası GitHub → Security → Code scanning / Dependabot / Secret scanning kontrolü.
- Bulgu çıkarsa: hemen düzelt (puan kesildiyse geri gelmez, ama yenilerinin önüne geçilir) ve kök nedeni PR kontrol listesine ekle.
- Dependabot PR'larını ve uyarılarını gözden geçir; sabitlenmiş, güncel sürümler kullan.

### Q5 — Copilot bütçe takibi [4]

> Copilot prompt'u: yok (süreç görevi).

- Her durum kontrolünde herkes model seçicideki tüketimi söyler, toplam tabloya yazılır.
- Eşikler: toplam 12 $ → uyarı (pahalı modeller sadece onayla), 17 $ → sadece ucuz modeller, 20 $ → Copilot kullanımını minimuma indir.

### Q6 — Kod dondurma (2. gün 12:00) [17]

> Copilot prompt'u: yok (süreç görevi).

- 11:30: son PR'lar; 12:00: main'e merge durur.
- Son pipeline success mi, `/health` 200 mü, Foundry deploy erişilebilir mi, Security sekmesi temiz mi?
- 12:00 sonrası zorunlu düzeltme olursa: tek PR, pipeline'ın yeşil bittiğini görmeden ayrılma. **13:00 teknik değerlendirmeden önce her şey yeşil olmalı.**

### Q7 — Demo videosu ve ekran görüntüleri [2]

> Copilot prompt'u: yok (süreç görevi).

- 1. gün gece ham kayıt, 2. gün 12:00–13:30 son kayıt (S1–S3, ~2,5 dk; S4 ayrı kısa klip).
- Tarayıcıda adres çubuğu, portal ve terminalde **anahtar, connection string, e-posta** görünmesin.
- Ekran görüntüleri: her sahnenin kilit anı (olası neden kartı, önce/sonra çağrı kaydı, kod analizi diff'i, tahmin kartı + köprü).

### Q8 — Sunum ve prova [2]

> Copilot prompt'u: yok (süreç görevi).

- .pptx 16:9, kılavuzdaki 11 slayt akışı; mimari slaytında yalnızca gerçekten çalışan servisler.
- İki prova: ilki 13:30 civarı (süre ölçümü), ikincisi 14:45 civarı. 5 dakika sınırı sert.
- Canlı demo yedek planı: video hazır, sunum bilgisayarında açık sekmede.
