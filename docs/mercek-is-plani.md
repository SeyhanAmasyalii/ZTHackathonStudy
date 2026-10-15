# Mercek — İş Planı: Görevler, Sorumluluklar ve Demo Senaryosu

Bağlantılı dokümanlar: `mercek-kapsam.md` (kapsam, öncelik, zaman planı), `mercek-sentetik-veri-plani.md` (veri), `hackathon-teknik-kilavuz.md` (kurallar).

---

## 1. Varsayılan mimari (görevlerin dayandığı)

| Katman | Bileşen | Not |
|---|---|---|
| Arayüz | React (Vite) tek uygulama, 3 bölüm: **Banka Simülasyonu**, **Destek Konsolu** (M1), **Talep Asistanı** (M2) | Backend build'iyle birlikte tek App Service'ten sunulur |
| Backend | Tek API (FastAPI veya .NET — ekip yarın sabah karar verir) | `/health`, `/api/incidents/*`, `/api/requests/*` |
| AI | Azure AI Foundry: 1 sohbet modeli (küçük/ucuz) + 1 embedding modeli | Anahtarlar App Settings / Managed Identity'de, repoda asla |
| Veri | Azure SQL (serverless, en düşük tier) | Ekranlar, metadata, servisler, loglar, çağrılar, talepler, takvim |
| Arama | Azure AI Search (Free/Basic) | Çözüm bilgi bankası + geçmiş çağrılar + geçmiş talepler (hibrit arama) |
| CI/CD | GitHub Actions `ci-cd.yml` (CodeQL'den ayrı) | PR: lint + test + güvenlik taraması · main: build + deploy |

Repo yapısı: `frontend/`, `backend/`, `prompts/`, `data/` (üretim betiği + senaryo kayıtları), `sample-codebase/` (S2 için sentetik kod/SP), `tests/`, `docs/`, `README.md`.

**AI ile kuralın net ayrımı (jüri için):** Sınıflandırma, özetleme, eşleştirme gerekçesi, kod analizi → AI. Efor/maliyet/takvim hesabı, servis haritası, eşik kararları → deterministik kod. AI hesap yapmaz, hesabı açıklar.

---

## 2. Sorumluluklar (tek liste — isteyen istediğini seçer)

| # | Sorumluluk | Kapsadığı görevler | Üstlenen |
|---|---|---|---|
| 1 | **Ürün sahipliği:** kapsam, öncelik, kabul kriterleri, zaman kutuları, 2 saatlik durum kontrolleri | Tüm planın önceliklendirilmesi | |
| 2 | **Sunum ve demo:** senaryo metni, .pptx, demo videosu, provalar | Q7, Q8 | |
| 3 | **İş değeri ve soru-cevap hazırlığı:** önce/sonra rakamları, varsayımlar, S-C cevapları | İş değeri tablosu, Q3 yorumu | |
| 4 | **Copilot bütçe takibi** (hedef < 20 $) | Q5 | |
| 5 | **Veri sözlüğü ve sentetik veri üretimi** | A5 | |
| 6 | **Senaryo kayıtları ve `sample-codebase/`** (S1–S4 verisi, hatalı SP) | A5, M1.4-d | |
| 7 | **Soru bankası ve alan metadata standartları** | M2.3-a | |
| 8 | **Senaryo testleri ve AI çıktı doğruluk kontrolü** | Q2 | |
| 9 | **Banka simülasyonu ve Joyride turları** | M1.1 arayüz, M1.5 arayüz | |
| 10 | **Destek Konsolu arayüzü** | M1.2–M1.4 arayüz | |
| 11 | **Talep Asistanı arayüzü** | M2.1–M2.6 arayüz | |
| 12 | **LLM istemcisi ve prompt yönetimi** | A6, `prompts/` | |
| 13 | **M1 backend:** bağlam, log inceleme, zenginleştirme, servis tespiti | M1.1–M1.3 backend | |
| 14 | **RAG ve kod analizi:** AI Search indeksleri, eşleştirme, kod analiz akışı | M1.4, M1.5 prompt | |
| 15 | **M2 backend:** sınıflandırma, etki analizi, tahmin, takvim, köprü | M2.1–M2.6 backend | |
| 16 | **Repo iskeleti ve README** (Azure kaynak tablosu dahil) | A1, A4 | |
| 17 | **CI/CD, güvenlik taraması ve kod dondurma** | A2, Q4, Q6 | |
| 18 | **Azure kaynakları** (App Service, Foundry, SQL, AI Search) | A3 | |
| 19 | **Test altyapısı ve kod kalitesi:** test standardı, lint, PR inceleme düzeni | Q1 | |

### Seçim kuralları
- Her sorumluluğun **tek sahibi** olur. Sahiplik "tek başına yapmak" değil, "bitmesini sağlamak" demektir; sahip yardım isteyebilir.
- Herkes **2–4 sorumluluk** seçer. Seçimi bugün yaparız, 1. gün açılışta teyit ederiz.
- **Sahipsiz kalamayacaklar:** 1, 4, 17, 18. Bunlar boş kalırsa puan doğrudan kaybedilir.
- **Kritik yol:** 1. gün sabah 5, 16, 17, 18 aynı anda ilerlemeli. Bu dördü farklı kişilerde olursa altyapı öğlene yetişir.
- Durum kontrollerinde sorumluluklar yeniden dağıtılabilir (biri erken biterse boştaki işi çeker).
- Doğrudan main'e push yok; her iş **feature branch + PR**, PR'ı sahibi dışında biri onaylar.

---

## 3. Görev dökümü

Öncelik: **M** = Must · **S** = Should · **C** = Could · Köşeli parantez = ilgili sorumluluk numarası

### A — Altyapı (1. gün 10:30–13:30, öğle yemeğine kadar yeşil)

| # | Görev | Sorumluluk | Kabul kriteri |
|---|---|---|---|
| A1 | Repo iskeleti, klasör yapısı, `.gitignore`, `.env.example` (sadece placeholder), PR şablonu, `copilot-instructions.md` + kılavuz | [16] | İskelet main'de, CodeQL dosyası dokunulmamış |
| A2 | `ci-cd.yml`: PR'da lint + test + `npm audit` / `pip-audit` + gitleaks; main'de build + App Service deploy (OIDC) | [17] | İlk çalıştırma success |
| A3 | Azure: App Service + `/health` (200), Foundry projesi + sohbet ve embedding modeli deploy, Azure SQL, AI Search | [18] | Portal'da hepsi var, `/health` 200 |
| A4 | README: mimari, kurulum, **her Azure kaynağının amacı** tablosu | [16] | README main'de |
| A5 | Sentetik veri üretimi ve yükleme (SQL + AI Search indeksleri) | [5] [6] | Tablolar dolu, senaryo kayıtları sorgulanabilir |
| A6 | Ortak LLM istemcisi (Foundry), prompt yükleyici, testlerde mock | [12] | Birim testi geçiyor |

**Önemli:** CodeQL sadece main'de çalışıyor. Bu yüzden PR aşamasında kendi workflow'umuzda başka araçlarla (audit, gitleaks, linter) tarama yapıyoruz. İkinci bir CodeQL tanımlamıyoruz.

### M1 — Akıllı Problem Çözüm ve Çağrı Yönetimi

**Alt maddeler ve kabul kriterleri**

| Alt madde | Öncelik | Kabul kriteri |
|---|---|---|
| M1.1 Bağlamlı sorun bildirimi | M | Panel açıldığında "Para Transferi ekranındasınız" bilgisini gösteriyor |
| M1.2 Proaktif hata inceleme | M | S1'de 3 saniye içinde IBAN doğrulama zaman aşımı tespit ediliyor |
| M1.3 Talep zenginleştirme ve servis tespiti | M | S1 çağrısı doğru ekip ve kategoriyle otomatik oluşuyor |
| M1.4 Geçmiş çözüm eşleştirme ve öneri | M | S1'de eşleşme ≥ %90 ve kaynak çağrılar görünüyor; S2'de AI hatalı SP satırını buluyor |
| M1.5 Çözümün görsel anlatımı | S | S1'de kullanıcıya alternatif yol (havale) adım adım gösteriliyor |

**Görevler**

| Kod | Görev | Katman | Sorumluluk |
|---|---|---|---|
| M1.1-a | Banka simülasyonu, 4 ekran (Giriş, Hesaplarım, Para Transferi, Fatura Ödeme). Her ekranda `screen_id`, her etkileşimli öğede sabit `id` (Joyride için) | Arayüz | [9] |
| M1.1-b | Her ekranda "Sorun yaşıyorum" butonu → sohbet paneli. Bağlam: `screen_id`, `session_id`, son 5 kullanıcı adımı, zaman | Arayüz | [9] |
| M1.1-c | Para Transferi'nde gönder → simülasyon hatası **ve aynı anda SQL'e gerçek bir log satırı yazılır** ("anlık log kontrolü" sahici olsun) | Backend | [13] |
| M1.1-d | `POST /api/incidents/start` (bağlamı alır, oturum açar) | Backend | [13] |
| M1.2-a | Oturum + ekran için son 15 dakikanın loglarını getir, hata koduna göre grupla | Backend (kod) | [13] |
| M1.2-b | Prompt `log-ozet`: kullanıcı dili açıklama + teknik özet | AI | [12] |
| M1.2-c | "Olası neden" kartı (kullanıcı sorusunu yazmadan önce gösterilir) | Arayüz | [10] |
| M1.3-a | Prompt `cagri-zenginlestir`: serbest metin + log + ekran → yapılandırılmış JSON (başlık, kategori, öncelik, özet, tekrar adımları, log referansları) | AI | [12] [13] |
| M1.3-b | Servis/ekip tespiti: **önce kural** (hata kodu → servis, ekran → servis haritası); AI yalnızca belirsizlikte karar verir ve gerekçe yazar | Backend (kod + AI) | [13] |
| M1.3-c | Destek Konsolu'nda çağrı kartı (önce: kullanıcının tek cümlesi / sonra: zenginleştirilmiş kayıt) | Arayüz | [10] |
| M1.4-a | AI Search hibrit arama (vektör + anahtar kelime) → ilk 3 sonuç + skor; eşik (ör. 0,75) **kodda** | Backend (kod) | [14] |
| M1.4-b | Eşleşme varsa: prompt `cozum-uyarla` → geçmiş çözümü bu çağrıya uyarlar, kaynak çağrı numaralarını gösterir | AI | [14] |
| M1.4-c | Eşleşme yoksa: servis → `sample-codebase/` dosya haritası; ilgili 2–3 dosya prompt `kod-analiz`'e verilir → kök neden, dosya/satır, düzeltme önerisi (diff) | AI | [14] |
| M1.4-d | `sample-codebase/`: Fatura Ödeme servisi + `sp_FaturaTutarHesapla` (hatalı yuvarlama gömülü) + 4–5 dikkat dağıtıcı dosya | Veri | [6] |
| M1.4-e | Eşleşme sonuçları ve kod analizi görünümü | Arayüz | [10] |
| M1.5-a | Prompt `joyride-adim`: çözüm metni + ekranın izinli öğe listesi → `[{target, content}]` JSON; AI yalnızca listedeki `id`'leri kullanabilir (doğrulama kodda) | AI | [14] |
| M1.5-b | Joyride ile turu oynat, "Bana göster" butonu | Arayüz | [9] |

### M2 — Akıllı Talep Analizi, Maliyet ve Takvim Planlama

**Alt maddeler ve kabul kriterleri**

| Alt madde | Öncelik | Kabul kriteri |
|---|---|---|
| M2.1 Talep sınıflandırma | M | S3 "mevcut değişiklik / Para Transferi", S4 "yeni ekran" olarak sınıflanıyor |
| M2.2 Mevcut ekrana benzetme ve akış önerisi | C | S3 için önce/sonra akış adımları listeleniyor |
| M2.3 Yeni ekran için soru setiyle kapsam olgunlaştırma | S | S4'te 4–5 soruda kapsam özeti ve alan tablosu çıkıyor |
| M2.4 Etki analizi | M | S3'te 3 servis gerekçeleriyle listeleniyor |
| M2.5 Maliyet ve takvim | M | S3'te efor aralığı, maliyet, başlangıç–bitiş tarihi ve dayandığı benzer talepler görünüyor |
| M2.6 Çağrı verisiyle kapsam zenginleştirme | S | S3'te seçim yapılınca tahmin ve plan güncelleniyor |

**Görevler**

| Kod | Görev | Katman | Sorumluluk |
|---|---|---|---|
| M2.1-a | Prompt `talep-siniflandir` → `{tip: mevcut_degisiklik \| yeni_ekran, ekran_id?, güven}`; ekran eşleşmesi katalogdan | AI | [15] |
| M2.1-b | Talep Asistanı giriş ekranı (serbest metin) | Arayüz | [11] |
| M2.2-a | Ekranın mevcut akış tanımı (metadata) + talep → prompt `akis-oneri`: değişen/eklenen adımlar | AI | [15] |
| M2.2-b | Önce/sonra akış listesi | Arayüz | [11] |
| M2.3-a | Soru bankası (10–15 soru: amaç, kullanıcı, veri alanları, onay adımları, limitler, bildirim…) ve alan standartları (ör. Müşteri No: 9–11 hane, sadece rakam, maskeli) | Veri | [7] |
| M2.3-b | Prompt `sonraki-soru`: cevaplara göre bankadan en fazla 5 soru seçer/uyarlar; sonunda kapsam özeti + alan önerileri | AI | [15] |
| M2.3-c | Sihirbaz (wizard) arayüzü + alan önerisi tablosu | Arayüz | [11] |
| M2.4-a | Servis bağımlılık grafiği (SQL): ekran → doğrudan servisler → bağımlı servisler | Backend (kod) | [15] |
| M2.4-b | AI, talebe göre hangi servislerin **gerçekten** etkileneceğini gerekçesiyle filtreler | AI | [15] |
| M2.4-c | Etkilenen servis listesi | Arayüz | [11] |
| M2.5-a | Benzer geçmiş talepler (AI Search) → ilk 5 → efor **medyan ve aralık** | Backend (kod) | [15] |
| M2.5-b | Maliyet = adam-gün × günlük maliyet parametresi (varsayım, ekranda açıkça yazılı) | Backend (kod) | [15] |
| M2.5-c | Takvim: ilgili ekibin kapasitesi + mevcut işleri → ilk uygun başlangıç ve bitiş | Backend (kod) | [15] |
| M2.5-d | Prompt `tahmin-gerekce`: AI hesabı **açıklar**, değiştirmez | AI | [15] |
| M2.5-e | Tahmin kartı + basit zaman çizelgesi | Arayüz | [11] |
| M2.6-a | SQL: ekranın son 30 gün çağrı adedi, kategori dağılımı, en sık 3 sorun ve çözümü | Backend (kod) | [15] |
| M2.6-b | "Bu sorunları kapsama eklemek ister misiniz?" seçimi → efor ve takvim yeniden hesaplanır | Arayüz + Backend | [11] [15] |

### Q — Kalite, ölçüm ve teslim

| # | Görev | Sorumluluk | Ne zaman |
|---|---|---|---|
| Q1 | Birim testleri (kural/hesap fonksiyonları), AI çağrıları mock'lu | [19] + herkes kendi kodu için | Sürekli |
| Q2 | Senaryo testleri: S1–S4 uçtan uca, beklenen çıktılar | [8] | 1. gün gece, 2. gün sabah |
| Q3 | Süre ölçümü: tespit, zenginleştirme, tahmin uç süreleri loglanır (iş değeri kanıtı) | [13] [15] → yorum [3] | 1. gün |
| Q4 | Security sekmesi kontrolü, Dependabot uyarıları | [17] | Her merge sonrası |
| Q5 | Copilot harcama takibi (hedef < 20 $) | [4] | Her durum kontrolü |
| Q6 | **12:00 kod dondurma** → son pipeline success, `/health` 200 | [17] | 2. gün |
| Q7 | Demo videosu + ekran görüntüleri (gizli bilgi yok) | [2] | 2. gün 12:00–13:30 |
| Q8 | Sunum + iki prova | [2] (herkes katılır) | 2. gün 12:00–14:45 |

---

## 4. Zaman × odak (hangi saatte hangi sorumluluklar aktif)

| Zaman | Ön planda olan sorumluluklar | Çıktı |
|---|---|---|
| **Bugün (hazırlık, kod yok)** | [1] [2] [3] senaryo, iş değeri varsayımları, sunum iskeleti · [5] [6] [7] veri sözlüğü, hata kodları, çağrı kategorileri, soru bankası, S2 hatası tasarımı · [9] [10] [11] ekran taslakları, Joyride pratiği · [12] [14] prompt taslakları (metin), AI Search pratiği · [17] [18] Azure kaynak listesi, workflow taslağı (metin), deploy pratiği | Tasarım dokümanları, pratik deneyimi |
| **1. gün 10:30–13:30** | [16] [17] [18] altyapı · [5] veri üretimi · [12] LLM istemcisi · [9] simülasyon iskeleti · [1] görev panosu | Altyapı yeşil, veri yüklü |
| **1. gün 14:30–19:00** | [13] M1.2–1.3 · [15] M2.1, M2.4 · [9] [10] M1.1 + Destek Konsolu · [6] senaryo kayıtları, `sample-codebase/` | Must'ların ilk yarısı |
| **1. gün 20:00–gece** | [14] M1.4 · [15] M2.5 · [11] Talep Asistanı · [8] senaryo testleri · [3] iş değeri hesapları | Must'lar tamam |
| **2. gün 09:30–12:00** | [14] [9] M1.5 · [15] [11] [7] M2.3, M2.6 · [2] ham demo provası | Should'lar, entegrasyon |
| **2. gün 12:00** | [17] kod dondurma | Son pipeline success |
| **2. gün 12:00–14:45** | [2] video, sunum, prova · [3] S-C · [8] AI çıktı kontrolü · diğerleri hata bekleme | Sunuma hazır |

---

## 5. Demo senaryosu (zenginleştirilmiş)

### Karakterler
- **Ayşe** — Bireysel müşteri, mobil uygulamadan kirasını EFT ile göndermeye çalışıyor.
- **Mert** — L2 destek uzmanı, Destek Konsolu'nu kullanıyor.
- **Zeynep** — Dijital Kanallar iş analisti, Talep Asistanı'nı kullanıyor.

### 5 dakikalık sunum zamanlaması
| Süre | Bölüm |
|---|---|
| 0:00–0:20 | Kapak + takım |
| 0:20–0:50 | Problem (Ayşe'nin hikâyesi, bugünkü süreç ve süresi) |
| 0:50–1:20 | Çözüm + yenilik + mimari (tek slayt) |
| 1:20–3:50 | **Demo: Sahne 1 → 2 → 3** |
| 3:50–4:40 | İş değeri (önce/sonra) |
| 4:40–5:00 | Sonraki adımlar, kapanış ve slogan |

S4 (yeni ekran) canlı demoda yok; yedek videoda ve soru-cevapta gösterilir.

### Sahne 1 — "Para gönderemiyorum" (M1.1–M1.3, M1.5) · ~60 sn
1. Ayşe Para Transferi ekranında 2.500 TL EFT girer, gönder → "İşleminiz şu an gerçekleştirilemiyor."
2. "Sorun yaşıyorum" der. Panel o daha yazmadan açılır: *"Para Transferi ekranında son işleminizde IBAN doğrulama servisinde gecikme görüyoruz."*
3. Ayşe "kira ödemem lazım acil" yazar.
4. Mercek: *"Bu bilinen bir sorun, ekibimiz haberdar. Şu an Havale ile gönderebilirsiniz."* → **"Bana göster"** → Joyride ile havale yolu adım adım.
5. Arka planda çağrı kaydı oluşur: **CAG-1042** · Kategori: Para Transferi / Teknik · Öncelik: Yüksek · Ekip: Ödeme Sistemleri · Log referansı: `IBN-504`.

### Sahne 2 — Destek tarafı ve "AI kodu okur" (M1.4) · ~60 sn
1. Mert, Destek Konsolu'nda CAG-1042'yi açar: zenginleştirilmiş kayıt, **%93 eşleşme**, 6 geçmiş çağrı, uyarlanmış çözüm (IBAN servisinde bağlantı havuzu / timeout ayarı).
2. Mert ikinci bir çağrıyı açar: **CAG-1043** — "Fatura ödemede 100,005 TL'lik fatura 100,00 TL ödendi, eksik ödeme uyarısı geldi."
3. Eşleşme yok (en yüksek skor %41). Mercek kod analizine geçer: `sp_FaturaTutarHesapla` içinde yuvarlama yerine **kesme** yapan satırı gösterir, düzeltme önerisini diff olarak sunar.

### Sahne 3 — Talepten plana, çağrıdan kapsama (M2.1, M2.4, M2.5, M2.6) · ~30 sn
1. Zeynep: *"Para Transferi ekranında kayıtlı alıcıları favori olarak seçebilelim."*
2. Mercek: **Mevcut ekran değişikliği · Para Transferi** · Etkilenen servisler: Transfer API, Müşteri Profil Servisi, IBAN Doğrulama (gerekçeleriyle).
3. Tahmin: 4 benzer geçmiş talep → **15–22 adam-gün (medyan 18)** · maliyet = 18 × günlük maliyet varsayımı · Ödeme Sistemleri ekibi **9 Kasım'da** müsait → tahmini bitiş **4 Aralık**.
4. Köprü: *"Bu ekran son 30 günde 312 çağrı aldı; %41'i IBAN doğrulama zaman aşımı. Kalıcı çözümü kapsama eklemek ister misiniz?"* → **Evet** → +3 adam-gün, bitiş **9 Aralık**.

### Sahne 4 (yedek) — Yeni ekran: Döviz Alarmı (M2.3)
1. Talep: *"Müşteriler belirledikleri kura ulaşınca bildirim almak istiyor."* → yeni ekran.
2. Mercek 4–5 soru sorar (hangi dövizler, bildirim kanalı, alarm adedi limiti, geçerlilik süresi, giriş gerekli mi).
3. Çıktı: kapsam özeti + alan önerileri (ör. *Hedef kur: 4 ondalık, pozitif, mevcut kurun ±%20'si içinde*; *Müşteri No: 9–11 hane, maskeli*).

### Senaryonun veriye gömülmesi gerekenler [6]
| Sahne | Veride olması gereken |
|---|---|
| S1 | `IBN-504` hata kodu, IBAN Doğrulama → Ödeme Sistemleri eşlemesi, aynı hatalı 6 çözülmüş geçmiş çağrı, havale ekranı öğe id'leri |
| S2 | `sp_FaturaTutarHesapla` (kesme hatası) + dikkat dağıtıcı dosyalar; geçmişte benzeri olmayan çağrı metni |
| S3 | Para Transferi'nin 30 günde 312 çağrısı (%41 IBN-504), 4 benzer geçmiş talep (efor 15/17/19/22), ekip takvimi (9 Kasım'a kadar dolu), bağımlılık grafiği |
| S4 | Döviz ekranı metadata'sı yok (yeni), alan standartları tablosu, soru bankası |

Birebir değerler: `mercek-sentetik-veri-uretimi.md` §3–4.

### İş değeri [3] (varsayımlar netleştirilecek)
| Ölçü | Bugün (varsayım) | Mercek ile |
|---|---|---|
| Sorunun ilk tespiti | Müşteri çağrı merkezini arar → L1 → L2, saatler | Saniyeler, müşteri daha çağrı açmadan |
| Çağrı kaydının kalitesi | Tek cümle, sık sık geri dönüş | Log, ekran, adımlar ve ekip baştan dolu |
| Yanlış ekibe yönlendirme | %X (varsayım) | Kural + AI ile otomatik |
| Bilinen sorunun çözümü | Bilgi kişilerde | Geçmiş çözüm saniyeler içinde, kaynaklı |
| Talep efor tahmini | Analist + ekip toplantıları, günler | Dakikalar, geçmiş verilere dayalı ve gerekçeli |
| Kapsam kalitesi | Çağrı verisi talepten kopuk | Ekranın çağrı geçmişi kapsama giriyor |

### Soru-cevap hazırlığı [3]
- **AI yanlış önerirse?** Eşik altında öneri yok; kaynaklar gösteriliyor; kod düzeltmeleri öneri, uygulama insan onaylı; efor hesabı AI'da değil kodda.
- **Canlıya geçiş?** Kibana, çağrı sistemi ve kod reposu için okuma entegrasyonları; KVKK için log maskeleme.
- **Çalışma maliyeti?** Küçük model + önbellek; çağrı başına tahmini maliyet (Q3 ölçümlerinden).
- **Kim, ne sıklıkla?** Müşteriler (sorun anında), L1/L2 destek (her çağrıda), analistler (her talepte).
