# Mercek — İş Planı: Sorumluluklar, Görevler ve Demo Planı

Bağlantılı dokümanlar:
- `mercek-kapsam.md`: kapsam, öncelik, zaman planı
- `mercek-demo-senaryo-onerileri.md`: senaryolar A–F
- `mercek-sentetik-veri-plani.md` ve `mercek-sentetik-veri-uretimi.md`: veri
- `mercek-uygulama-rehberi.md`: her görevin nasıl yapılacağı
- `COPILOT_REBUILD_GUIDE.md`: temel uygulama
- `hackathon-teknik-kilavuz.md`: kurallar

---

## 1. Mimari (görevlerin dayandığı)

| Katman | Bileşen | Not |
|---|---|---|
| Arayüz | **Next.js 16** (rebuild Faz 1–4, 7): Bankacılık ekranları, Mercek sayfası, Talep Yönlendirme | App Service #1 (`node server.js`, standalone build) |
| Backend | **FastAPI** (uv): `/api/health`, `/api/logs`, `/api/mercek/*`, `/api/requests/*`, `/api/odm/*` | App Service #2 (gunicorn + uvicorn worker), aynı App Service Plan |
| AI | **Azure AI Foundry:** bir sohbet modeli (küçük/ucuz) ve bir embedding modeli | Kimlik: Managed Identity; yetki yoksa App Settings. Repoda anahtar yok. |
| Veri | **Azure SQL** (serverless, en düşük tier) | Loglar, katalog, servisler, takvim, portföy, çağrılar, talepler |
| Arama | **Azure AI Search** (Free/Basic) | `solutions`, `requests`, `announcements` indeksleri (hibrit arama) |
| CI/CD | GitHub Actions `ci-cd.yml` (CodeQL'den ayrı) | PR: lint, test, audit, gitleaks · main: build ve iki deploy |

**Hesabı kod yapar, AI açıklar:**
- **Kod:** uygun kredi tutarı, log örüntü sayıları, eşleşme eşiği, servis ataması, ana kayıt bağlama, a/g medyanı, takvim ve kapasite, köprü sayıları, ekran kodu doğrulaması.
- **AI:** serbest metinden bilgi çıkarma, açıklama metinleri, çağrı zenginleştirme, çözüm uyarlama, kod analizi, talep bileşenleri ve sorular, gerekçeler.

---

## 2. Sorumluluklar (tek liste, isteyen istediğini seçer)

| # | Sorumluluk | Kapsadığı görevler | Üstlenen |
|---|---|---|---|
| 1 | **Ürün sahipliği:** kapsam, öncelik, kabul kriterleri, 2 saatlik durum kontrolleri, 12:00 canlı demo kararı | Tüm plan, Q9 | |
| 2 | **Sunum ve demo:** senaryo slaytı, .pptx, ekran görüntüleri, videolar, provalar | Q7, Q8 | |
| 3 | **İş değeri ve soru-cevap hazırlığı** | İş değeri tablosu, Q3 yorumu | |
| 4 | **Copilot bütçe takibi** (hedef < 20 $) | Q5 | |
| 5 | **Sentetik veri üretimi:** log enjeksiyonu, portföy, çağrılar, talepler, Foundry metinleri | V3–V6 | |
| 6 | **Katalog ve senaryo verisi:** şema, ekran ve servis kataloğu, hata–servis kuralları, takvim, duyurular, yükleme, `demo_reset`, `validate_scenarios` | V1, V2, V7, V8 | |
| 7 | **Senaryo testleri ve AI çıktı doğruluk kontrolü** | Q2 | |
| 8 | **Temel uygulama:** rebuild Faz 2–4 ve 7, demo kullanıcıları | A5–A8 | |
| 9 | **Bankacılık–Mercek bağlantısı:** "Sorun yaşıyorum" butonu, işlem bağlamı, canlı olay logları, "Bana göster" | M1.1-a, M1.1-b, M1.5 | |
| 10 | **Mercek arayüzü:** panel, sohbet, çağrı listesi ve detayı, eşleşme/kod görünümü | M1.2-e, M1.3-e, M1.4-e, M1.6-b | |
| 11 | **Talep Yönlendirme arayüzü** | M2.1-b, M2.2-b, M2.5-e, M2.6-b | |
| 12 | **LLM istemcisi ve prompt yönetimi** | A9, `prompts/` | |
| 13 | **M1 backend:** log sorgusu, örüntü analizi, kredi hesabı, zenginleştirme, servis ataması, ana kayıt, ölçüm | M1.1-c … M1.3-d, M1.6-a, M1.7 | |
| 14 | **RAG ve kod analizi:** AI Search indeksleri, çözüm eşleştirme, duyuru araması, kod analizi | M1.4-a … d | |
| 15 | **M2 backend:** talep analizi, servis etki, tahmin, takvim, köprü | M2.1-a … M2.6-c | |
| 16 | **Repo iskeleti ve README** (rebuild Faz 1, Azure kaynak tablosu) | A1, A4 | |
| 17 | **CI/CD, güvenlik taraması ve kod dondurma** | A2, Q4, Q6 | |
| 18 | **Azure kaynakları** (2 App Service, Foundry, SQL, AI Search) | A3 | |
| 19 | **Test altyapısı ve kod kalitesi:** test standardı, lint, PR inceleme düzeni | Q1 | |

### Seçim kuralları
- Her sorumluluğun **tek sahibi** olur. Sahiplik "tek başına yapmak" değil, "bitmesini sağlamak" demektir.
- Herkes **3–4 sorumluluk** seçer. Seçim 1. gün 10:30'da, kodlamaya başlamadan önce ilk 15 dakikada yapılır.
- **Sahipsiz kalamayacaklar:** 1, 4, 17, 18. Boş kalırlarsa puan doğrudan kaybedilir.
- **Kritik yol (1. gün sabah):** 6, 8, 16, 17, 18 aynı anda ilerler. Farklı kişilerdeyse altyapı öğlene yetişir.
- Durum kontrollerinde sorumluluklar yeniden dağıtılabilir.
- Doğrudan main'e push yok. Her iş **feature branch + PR** ile gider ve PR'ı sahibi dışında biri onaylar.

---

## 3. Görev dökümü

Öncelik: **M** = Must · **S** = Should · **C** = Could · Köşeli parantez: sorumluluk numarası.
Nasıl yapılacağı: `mercek-uygulama-rehberi.md` (aynı görev kodlarıyla).

### A — Altyapı ve temel uygulama (1. gün 10:30–13:30, öğlene yeşil)

| # | Görev | Öncelik | Sorumluluk | Kabul kriteri |
|---|---|---|---|---|
| A1 | Rebuild **Faz 1**: monorepo iskeleti; `.gitignore`, `.env.example` (yalnızca placeholder), PR şablonu, `copilot-instructions.md` | M | [16] | Faz 1 doğrulaması geçer; CodeQL dosyası dokunulmamış |
| A2 | `ci-cd.yml`: PR'da lint, test, `npm audit`, `pip-audit`, gitleaks; main'de build ve **iki deploy** (frontend, backend) | M | [17] | İlk çalıştırma success |
| A3 | Azure: App Service Plan + 2 App Service, Foundry projesi (sohbet + embedding deploy), Azure SQL, AI Search | M | [18] | `https://<backend>/api/health` → 200; frontend açılıyor |
| A4 | README: mimari, kurulum, **her Azure kaynağının amacı** tablosu | M | [16] | README main'de |
| A5 | Rebuild **Faz 2**: dashboard ve 3 modül | M | [8] | Faz 2 kabul kriterleri |
| A6 | Rebuild **Faz 3**: sahte kimlik doğrulama, **demo kullanıcıları** (Elif, Zeynep, Kerem, Fatma, Hakan; Elif geliri 38.000) | M | [8] | Her kullanıcıyla giriş yapılıyor |
| A7 | Rebuild **Faz 4**: 5 işlem ekranı ve ekran kodları | M | [8] | Faz 4 kabul kriterleri; `loanPlan` testi |
| A8 | Rebuild **Faz 7**: Joyride senaryoları | S | [8] | `krd-gelir-orani`, `odm-dogalgaz` çalışıyor |
| A9 | Ortak LLM istemcisi (Foundry), prompt yükleyici, testlerde mock | M | [12] | Birim testi geçiyor |

Rebuild **Faz 5** (log üretici) V3'ün parçasıdır. **Faz 6** (Kibana yol haritası) uygulanmaz; README'de "canlıya geçiş" bölümüne referans olur.

**CodeQL notu:** CodeQL yalnızca main'de çalışır. PR aşamasında kendi workflow'umuzda başka araçlarla (audit, gitleaks, linter) tarama yapılır. İkinci bir CodeQL tanımlanmaz.

### V — Sentetik veri (1. gün 10:30–13:30)

| # | Görev | Sorumluluk | Kabul kriteri |
|---|---|---|---|
| V1 | `data/schema.sql` (14 tablo) | [6] | Azure SQL'de tablolar var |
| V2 | `catalog.json` (kullanıcılar, ekranlar, servisler, kurallar, takvim) ve `announcements.json` | [6] | Değerler üretim rehberi §3 ile birebir |
| V3 | Faz 5 log üreticisi + `inject_log_scenarios.py` | [5] | C'nin 412 kaydı; 01.10 öncesi 13 hane yok |
| V4 | `generate_texts.py` (Foundry): çağrı notları, çözümler, talep metinleri → `texts.json` | [5] | Yasak kurallar ihlal edilmiyor |
| V5 | `generate_portfolio.py` | [5] | D ve E rakamları kesin |
| V6 | `generate_incidents.py`, `generate_requests.py` | [5] | B, C, D, E çağrı ve talep kayıtları |
| V7 | `load_all.py`: SQL ve 3 AI Search indeksi | [6] | İndeksler sorgulanabilir |
| V8 | `demo_reset.py`, `validate_scenarios.py` | [6] | Doğrulama raporu yeşil (üretim rehberi §12) |

### M1 — Akıllı Problem Çözüm ve Çağrı Yönetimi

**Alt maddeler ve kabul kriterleri**

| Alt madde | Öncelik | Kabul kriteri |
|---|---|---|
| M1.1 Bağlamlı sorun bildirimi | M | A: Panel açıldığında Elif yazmadan "KRDTKULL · son işlem: AFFORDABILITY_EXCEEDED" görünüyor. B: Zeynep'in metninden ODMTFATR, Başkentgaz ve 4012345678 çıkarılıyor. |
| M1.2 Log inceleme ve örüntü analizi | M | A: iş kuralı olarak açıklanıyor, 144.186 / 19.000 / 22.754 / ~334.000 doğru. B: "son 30 dk 47 istek". C: 412, %97 İSKİ, hepsi 13 hane, 1 Ekim. |
| M1.3 Zenginleştirme, servis ataması, ana kayıt | M | A'da çağrı açılmıyor. B: vaka CAG-2051'e bağlanıyor, sayaç 12. C: çağrı Fatura Ödeme Servisi'ne atanıyor. |
| M1.4 Eşleştirme, duyuru, kod analizi | M (duyuru S) | B: %93, 6 benzer olay, SOL-031 uyarlanmış. C: eşleşme %35 → duyuru DUY-0412, kodda 2 yer, diff, kalıcı öneri, ASKİ uyarısı. |
| M1.5 "Bana göster" | S | A: tur 330.000 / 36 ay dolduruyor, uyarı kalkıyor. |
| M1.6 Etki ölçümü | S | Önlenen çağrı ve bağlı vaka sayaçları ekranda artıyor. |
| M1.7 Günlük durum özeti | C | F: "bugün en çok sorun yaşanan ekran" → ODMTFATR, Başkentgaz, CAG-2051. |

**Görevler**

| Kod | Görev | Katman | Sorumluluk |
|---|---|---|---|
| M1.1-a | Ekran kodu çubuğuna **"Sorun yaşıyorum"** butonu, sağdan açılan Mercek paneli. Bağlam: ekran kodu, müşteri no, son `trace.id`, ekrandaki hata mesajı (`TransactionContext`) | Arayüz | [9] |
| M1.1-b | Ekranlar işlem sonucunu `POST /api/logs` ile ECS formatında yazar: KRDTKULL uyarısı, ODMTFATR sorgu/ödeme. **Demo modu:** Başkentgaz `INSTITUTION_TIMEOUT` döner; İSKİ 13 hane → `VALIDATION_ERROR` | Arayüz + Backend | [9] [13] |
| M1.1-c | Serbest metinden bilgi çıkarma: prompt `varlik-cikar` (ekran, kurum, abone no, müşteri no) + kodla doğrulama (ekran kataloğu, kurum listesi) | AI + kod | [12] [13] |
| M1.2-a | Tek işlem: `trace_id` veya müşteri no + ekran + son 15 dk ile log bulma | Backend | [13] |
| M1.2-b | Örüntü analizi: hata kodu/alanına göre kurum, numara uzunluğu, kanal ve ilk görülme gruplaması; son 30 dk ile önceki 30 günün ortalamasını karşılaştırma | Backend | [13] |
| M1.2-c | `loanPlan` Python portu ve **uygun tutar hesabı** (36 ayda gelir × 0,5'i aşmayan en yüksek tutar) | Backend | [13] |
| M1.2-d | Prompt `log-acikla`: iş kuralı / teknik ayrımı, temsilci dili, **müşteriye söylenecek metin** | AI | [12] |
| M1.2-e | Panelde ve sohbette cevap kartları: açıklama, rakamlar, müşteriye söylenecek metin, kaynak loglar | Arayüz | [10] |
| M1.3-a | Prompt `cagri-zenginlestir`: metin + log + örüntü → yapılandırılmış kayıt (başlık, kategori, özet, etkilenen müşteri, kanal dağılımı) | AI | [12] [13] |
| M1.3-b | Servis ataması kural tablosundan (`error_rules`); `open_incident = 0` ise çağrı açılmaz ve "önlenen çağrı" sayılır | Backend | [13] |
| M1.3-c | Ana kayıt: aynı ekran + kurum + hata kodu için son 60 dk içinde açık ana kayıt varsa vaka ona bağlanır, yoksa yeni ana kayıt açılır | Backend | [13] |
| M1.3-d | Çağrı API'leri: liste, detay, bağlı vakalar | Backend | [13] |
| M1.3-e | Mercek sayfasında çağrı listesi ve detay; "Ana kayıt CAG-2051'e bağlandı · bağlı vaka: N" bildirimi | Arayüz | [10] |
| M1.4-a | AI Search hibrit arama (`solutions`) → ilk 3 sonuç ve skor; **eşik 0,75 kodda** | Backend | [14] |
| M1.4-b | Eşleşme varsa prompt `cozum-uyarla`: geçmiş çözümü bu olaya uyarlar, kaynak çağrıları gösterir | AI | [14] |
| M1.4-c | Eşleşme yoksa duyuru araması (`announcements`, kurum filtresi, geçerlilik tarihi) | Backend | [14] |
| M1.4-d | Kod analizi: ekranın dosya haritasındaki dosyalar (CI'da backend paketine kopyalanır) + prompt `kod-analiz` → kök neden, dosya/satır, diff, kalıcı öneri, test önerisi. **Ön koşul:** backend'de ODMTFATR abone no doğrulaması (`/api/odm`) | AI + kod | [14] |
| M1.4-e | Eşleşme, duyuru ve kod/diff görünümü; "Öneridir, uygulanmadı" etiketi | Arayüz | [10] |
| M1.5-a | "Bana göster": Mercek'in hesapladığı değerlerden çalışma anında Joyride senaryosu üretilir (`krd-gelir-orani` temel alınır; hedef `id`'ler sabit listeden) | Arayüz | [9] |
| M1.6-a | `mercek_events` kaydı: önlenen çağrı, bağlanan vaka, analiz süresi | Backend | [13] |
| M1.6-b | Sayaçlar Genel Bakış'ta ve Mercek sayfasında | Arayüz | [10] |
| M1.7 | Durum özeti: bugünün logları SQL'de gruplanır, prompt `durum-ozeti` | Backend + AI | [13] [12] |

### M2 — Akıllı Talep Analizi, Efor ve Takvim Planlama

**Alt maddeler ve kabul kriterleri**

| Alt madde | Öncelik | Kabul kriteri |
|---|---|---|
| M2.1 Talep analizi ve sınıflandırma | M | D: iki bileşen; "batch işi + mevcut ekran değişikliği"; ekran KRDRTKSR. E: "yeni ekran". |
| M2.2 Değişiklik önerisi ve sorular | M | D: buton tarifi ve 5 soru, varsayılanlarıyla; tek tıkla kabul. |
| M2.3 Yeni ekran kapsamı | C | E: `KRDTERTL` kurala uygun ve çakışmasız; taslak tablosu KRDTKULL'den yeniden kullanım gösteriyor. |
| M2.4 Servis bazlı etki | M | D: Kredi Takip (ana), Müşteri Yönetim (etkileşimli), gerekçeleriyle. |
| M2.5 Tahmin ve takvim | M (çatışma C) | D: 5 benzer talep, 18 a/g (11 + 7; 15 / 3), 9 Kasım → 2 Aralık. E: iki seçenek ve yan etkileri. |
| M2.6 Köprü | M | D: 186 / 71 çağrı, 2.340 kişi, %58 → %89, +2 a/g → 20 a/g, 4 Aralık. E: 6 kat artış, 418 çağrı, +2 a/g → 17 a/g. |

**Görevler**

| Kod | Görev | Katman | Sorumluluk |
|---|---|---|---|
| M2.1-a | Prompt `talep-analiz`: talep + ekran kataloğu özeti → bileşenler, tip, ilgili ekranlar, güven, gerekçe; ekran kodları kodla katalogda doğrulanır | AI + kod | [15] [12] |
| M2.1-b | Talep Yönlendirme'de "Yeni talep" girişi; analiz kartları. Faz 2'deki **ücret hesabı kaldırılır**, yerine a/g ve takvim | Arayüz | [11] |
| M2.2-a | Prompt `talep-sorular`: değişiklik önerisi + netleştirilecek sorular, benzer taleplerden varsayılan öneriler | AI | [15] |
| M2.2-b | Soru kartı: varsayılanları kabul et / değiştir | Arayüz | [11] |
| M2.3-a | Ekran kodu önerisi: AI önerir, kod regex ve katalog çakışmasıyla doğrular, gerekirse alternatif ister | AI + kod | [15] |
| M2.3-b | Ekran taslağı: katalogdaki bileşenlerden yeniden kullanım tablosu | AI | [15] |
| M2.4-a | Servis etkisi: ekran–servis ilişkisinden aday servisler (kod), AI rol ve gerekçe yazar | Kod + AI | [15] |
| M2.5-a | Benzer talepler (`requests` indeksi) → bileşen bazlı **medyan ve aralık**, servis payları | Backend | [15] |
| M2.5-b | Takvim: servis takvimi + iş günü hesabı → başlangıç–bitiş; dolu servis için "öncelik ver / sıraya koy" seçenekleri ve kayan planlı talepler | Backend | [15] |
| M2.5-c | Prompt `tahmin-gerekce`: AI hesabı **açıklar**, değiştirmez | AI | [15] |
| M2.5-d | Talep kaydı: TLP-1043 (D) / TLP-1044 (E); onaylayan, analist, "veriden eklenen kapsam" işareti | Backend | [15] |
| M2.5-e | Tahmin kartı, bileşen/servis tabloları, zaman çizelgesi, seçenek tablosu | Arayüz | [11] |
| M2.6-a | Köprü sorguları: talep konusuyla ilgili çağrı alt kategorileri; hedef grup ve iletişim izinleri; bölgesel çağrı artışı | Backend | [15] |
| M2.6-b | Prompt `kopru-oneri` + "Kapsama eklensin mi?" → efor ve takvim yeniden hesaplanır | AI + Arayüz | [15] [11] |

### Q — Kalite, ölçüm ve teslim

| # | Görev | Sorumluluk | Ne zaman |
|---|---|---|---|
| Q1 | Birim testleri: `loanPlan`, uygun tutar, örüntü sorguları, eşik, ana kayıt, medyan, takvim; AI çağrıları mock'lu | [19] + herkes kendi kodu için | Sürekli |
| Q2 | Senaryo testleri: A–D uçtan uca (E, F varsa), beklenen değerler `validate_scenarios` ile aynı | [7] | 1. gün gece, 2. gün sabah |
| Q3 | Süre ölçümü (analiz, eşleştirme, tahmin) ve token sayısı loglanır | [13] [15] → yorum [3] | 1. gün |
| Q4 | Security sekmesi, Dependabot uyarıları | [17] | Her merge sonrası |
| Q5 | Copilot harcama takibi (hedef < 20 $) | [4] | Her durum kontrolü |
| Q6 | **12:00 kod dondurma:** son pipeline success, iki uygulama da ayakta | [17] | 2. gün |
| Q7 | Her senaryo için ekran görüntüleri ve kısa video (canlıda gösterilmeyecekler ve yedek) | [2] | 2. gün 09:30'dan itibaren |
| Q8 | Sunum ve iki prova | [2] (herkes katılır) | 2. gün 12:00–14:45 |
| Q9 | **12:00 canlı demo kararı** (§5.3) | [1] [2] [7] | 2. gün 12:00 |

---

## 4. Zaman × odak

| Zaman | Ön plandaki sorumluluklar | Çıktı |
|---|---|---|
| **1. gün 08:00–10:30** (kod yok) | Kayıt, açılış; VDI, Azure ve GitHub girişleri; herkes kendi sorumluluğunun rehber bölümünü okur | Erişimler tamam |
| **1. gün 10:30–13:30** | [1] sorumluluk seçimi (ilk 15 dk) · [16] [17] [18] A1–A4 · [8] A5–A7 · [6] V1–V2 · [5] V3–V6 · [12] A9 | Altyapı yeşil, veri yüklü |
| **1. gün 14:30–19:00** | [9] M1.1 · [13] M1.2, M1.3 · [10] panel ve sohbet · [15] M2.1, M2.4 · [14] indeksler, M1.4-a/b · [6] V7–V8 | **A ve B** uçtan uca |
| **1. gün 20:00–gece** | [14] M1.4-c/d · [15] M2.2, M2.5, M2.6 · [11] Talep Yönlendirme · [7] senaryo testleri | **D ve C** uçtan uca |
| **2. gün 09:30–12:00** | [8] [9] A8, M1.5 · [13] [10] M1.6 · [15] M2.3, çatışma (E) · [13] M1.7 (F) · [2] ekran görüntüleri ve videolar · ham prova | Should ve Could'lar |
| **2. gün 12:00** | [17] kod dondurma · [1] [2] [7] canlı demo kararı | Son pipeline success |
| **2. gün 12:00–14:45** | [2] sunum, video, prova · [3] S-C · [7] AI çıktı kontrolü · diğerleri hata bekleme | Sunuma hazır |

---

## 5. Sunum ve demo planı

### 5.1 İlke

- **Sunumda tüm senaryolar (A–F)** tek bir "Kullanım senaryoları" slaytında yer alır. Jüri Mercek'in kapsamını eksiksiz görür.
- **Canlı demoda yalnızca çalışır durumdakiler** gösterilir. Hazır olmayanlar, aynı slayt sırasında ekran görüntüsü veya kısa videoyla anlatılır.
- Canlıda bir şey bozulursa o senaryonun videosuna geçilir; her canlı senaryonun da yedek videosu vardır.

### 5.2 Akış (5 dakika)

| Süre | Bölüm | İçerik |
|---|---|---|
| 0:00–0:20 | Kapak ve takım | AI Overflow · Mercek · "Soruna odaklanır, çözümü netleştirir." |
| 0:20–0:40 | Problem | Hata mı kural mı bilinmiyor; aynı sorun için onlarca çağrı; çözümler kişilerde; talepler sorunlardan habersiz planlanıyor |
| 0:40–1:05 | Çözüm ve mimari | İki modül, tek veri katmanı; "hesabı kod yapar, AI açıklar"; Azure mimarisi |
| 1:05–1:20 | **Kullanım senaryoları (A–F)** | Tek slayt: altı senaryo, her biri bir satır; canlı gösterilecekler işaretli |
| 1:20–4:15 | **Canlı demo** | A → B → C → D sırasıyla, çalışır olanlar (§5.3) |
| 4:15–4:45 | İş değeri | Önce / sonra tablosu, demo sırasında artan sayaçlar |
| 4:45–5:00 | Kapanış | Canlıya geçiş adımları, slogan |

**Canlı demo süreleri:** A ~45 sn · B ~50 sn · C ~35 sn · D ~45 sn (toplam ~2:55). E ve F yalnızca senaryo slaytında ve soru-cevapta.

### 5.3 12:00 canlı demo kararı (Q9)

**Bir senaryonun canlıya girme koşulu:**
1. Deploy edilmiş ortamda (yerel değil) çalışıyor.
2. `validate_scenarios.py` o senaryo için yeşil.
3. Son 3 prova üst üste hatasız ve süre içinde.

**Öncelik sırası:** A → B → D → C (hazırlık önceliği; sunumdaki sıra A → B → C → D'dir).

| Durum | Canlı demo | Hazır olmayanlar |
|---|---|---|
| Hepsi hazır | A, B, C, D (~2:55) | — |
| C hazır değil | A, B, D (~2:20) | C: 15 sn ekran görüntüsü (örüntü kartı, duyuru, diff). Kalan süre iş değerine |
| C ve D hazır değil | A, B (~1:35) | D: 30 sn video; C: 15 sn ekran görüntüsü |
| Yalnızca A hazır | A | B, C, D videoyla; iş değeri bölümü uzar |

**Demo öncesi kontrol listesi (her prova ve gerçek sunumdan önce):**
- `demo_reset.py --now` çalıştırıldı (B'nin son 30 dakikası, CAG-2051).
- Tarayıcıda sekmeler açık: Elif (KRDTKULL), Mehmet (ODMTFATR), Zeynep ve Kerem (Mercek), Fatma (Talep Yönlendirme).
- Joyride "Otomatik oynat" açık.
- Videolar sunum bilgisayarında yerel olarak var.

Senaryoların ayrıntısı: `mercek-demo-senaryo-onerileri.md`. Sahne sahne konuşma metni: `mercek-takim-anlatim-cumleleri.md`.

---

## 6. İş değeri [3]

| Ölçü | Bugün | Mercek ile | Demoda nereden görünür |
|---|---|---|---|
| İş kuralı reddi | Çağrı açılır, L1 kuralı açıklar | Ekranda açıklanır, uygun alternatif hesaplanır, **çağrı açılmaz** | A · "önlenen çağrı" sayacı |
| Yaygın kurum sorunu | Her arama ayrı çağrı, temsilci ne diyeceğini bilmez | Tek ana kayıt, temsilciye hazır müşteri açıklaması | B · bağlı vaka sayacı (12) |
| Bilinen sorun | L2 log arar, çözüm kişide | %93 eşleşme, kaynaklı çözüm | B |
| Yeni sorun | Kök neden günlerce aranır | Log + duyuru + kod ilişkilendirilir, satır düzeyinde öneri; sonraki olay önceden görülür | C · 187 müşteri, ASKİ uyarısı |
| Talep analizi | Toplantıda elle; servisler ve erişim sorunu geç fark edilir | Servis bazlı etki, benzer taleplerden a/g ve takvim; kapsam veriyle düzeltilir | D · %58 → %89 erişim |
| Acil talep | Kapasite çatışması geliştirme sırasında ortaya çıkar | Çatışma ilk gün, seçenekleriyle | E |

## 7. Soru-cevap hazırlığı [3]

- **AI yanlış önerirse?** Eşik altında çözüm önerilmez (C'de %35). Kaynaklar her zaman gösterilir. Kod düzeltmeleri yalnızca öneridir. Rakamları AI değil kod hesaplar.
- **Canlıya geçiş?** Log kaynağı Kibana/Elasticsearch (rebuild Faz 6 yol haritası), çağrı sistemi ve kod reposu için okuma entegrasyonları; KVKK için log maskeleme.
- **Çalışma maliyeti?** Küçük model, kısa bağlam (rakamlar SQL'den özet olarak gelir), analiz başına token Q3'te ölçülür.
- **Kim kullanır?** Şube ve çağrı merkezi temsilcileri (sorun anında), L2 ve platform ekipleri (her çağrıda), iş birimleri ve analistler (her talepte).
- **Veriler gerçek mi?** Tamamen sentetik; senaryolar gerçekçi rakamlarla kurgulandı, Mercek rakamları canlı sorgularla hesaplıyor.
