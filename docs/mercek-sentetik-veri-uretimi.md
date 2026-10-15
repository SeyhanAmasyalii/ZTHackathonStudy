# Mercek — Sentetik Veri Üretim Rehberi

`mercek-sentetik-veri-plani.md` **ne** üretileceğini, bu doküman **nasıl ve hangi değerlerle** üretileceğini anlatır. Tablolar ve alanlar `data/schema.sql` (görev A5-a) ile aynıdır.

---

## 1. Üretim yöntemi matrisi

| Varlık | Adet | Kaynak | Çıktı dosyası | Copilot prompt'u |
|---|---|---|---|---|
| Ekipler, servisler, bağımlılıklar | 5 / 12 / 10 | **Elle (bu doküman, §3)** | `data/seed/catalog.json` | A5-0 |
| Ekranlar, ekran–servis, ekran öğeleri | 8 / 13 / 19 | **Elle (§3)** | `data/seed/catalog.json` | A5-0 |
| Hata kodları | 15 | **Elle (§3)** | `data/seed/catalog.json` | A5-0 |
| Senaryo kayıtları (S1–S4) | ~30 kayıt | **Elle (§4)** | `data/seed/scenarios.json` | A5-0 |
| Alan standartları, soru bankası | 10 / 12 | **Elle** | `data/seed/field_standards.csv`, `questions.json` | M2.3-a |
| Sentetik kod (S2) | 6 dosya | **Elle (Copilot)** | `sample-codebase/` | M1.4-d |
| Doğal dil metinleri (çağrı, çözüm, talep) | ~200 / 60 / 100 | **Foundry modeli (§6)** | `data/seed/texts.json` | A5-c |
| Loglar, geçmiş çağrılar, talepler, takvim | 3000 / 400 / 100 / 3 ay | **Betik + Faker (§5)** | `data/out/*.csv` | A5-b |
| Embedding'ler + AI Search indeksleri | 3 indeks | **Betik (Foundry embedding)** | AI Search | A5-d |

**Akış (1. gün 10:30–13:30):**
```
A5-a şema → A5-0 catalog.json + scenarios.json → A5-c metinler (Foundry) → A5-b generate.py → A5-d load.py → §7 doğrulama
```

**Kurallar**
- Rastgele kısımlar `seed=42` ile tekrarlanabilir.
- Senaryo kayıtları rastgele üretimin **üzerine** yazılır ve betik onlarla çelişen kayıt üretmez (§5'teki "yasak" kurallar).
- Kişisel veri yok: ad soyad, TCKN, telefon, gerçek IBAN üretilmez. IBAN'lar her zaman maskeli: `TR** **** **** **** 4821`.
- Büyük veri Copilot'a ürettirilmez (maliyet). Copilot yalnızca betik yazar; metinleri Foundry modeli üretir.

---

## 2. Tarih referansı

- **"Bugün" = 17.10.2026** (demo günü). Betik `--today 2026-10-17` parametresi alır; "son 30 gün" ve takvim hesapları buna göre yapılır.
- Geçmiş çağrılar: 90 gün (19.07.2026–16.10.2026). Loglar: 45 gün. Geçmiş talepler: 18 ay.

---

## 3. Referans katalogları (elle — `catalog.json`)

### 3.1 Ekipler

| team_id | name | daily_capacity_md |
|---|---|---|
| ODEME | Ödeme Sistemleri | 1.0 |
| FATURA | Fatura Servisleri | 1.0 |
| KANAL | Dijital Kanallar | 1.0 |
| KIMLIK | Kimlik Yönetimi | 1.0 |
| KART | Kart Sistemleri | 1.0 |

> `daily_capacity_md = 1.0`: Takvim hesabı, yeni işe ekipten **bir geliştiricinin** ayrılacağını varsayar. Sunumda varsayım olarak söylenir.

### 3.2 Servisler

| service_id | name | team_id | description |
|---|---|---|---|
| TRANSFER_API | Transfer API | ODEME | EFT ve havale işlemlerini başlatır |
| IBAN_VALIDATION | IBAN Doğrulama | ODEME | Alıcı IBAN'ını ve ad uyumunu doğrular |
| EFT_GATEWAY | EFT Geçidi | ODEME | EFT mesajlarını dış sisteme iletir |
| CUSTOMER_PROFILE | Müşteri Profil Servisi | KANAL | Müşteri bilgileri ve kayıtlı alıcılar |
| ACCOUNT_SERVICE | Hesap Servisi | KANAL | Hesap listesi ve bakiye |
| NOTIFICATION | Bildirim Servisi | KANAL | SMS ve push bildirimleri |
| BILL_PAYMENT | Fatura Ödeme Servisi | FATURA | Fatura sorgulama ve ödeme |
| BILLER_INTEGRATION | Kurum Entegrasyonu | FATURA | Fatura kurumlarıyla bağlantı |
| AUTH_SERVICE | Kimlik Doğrulama | KIMLIK | Giriş ve oturum |
| OTP_SERVICE | Tek Kullanımlık Şifre | KIMLIK | SMS OTP üretimi |
| CARD_SERVICE | Kart Servisi | KART | Kart listesi ve limitler |
| INVEST_SERVICE | Yatırım Servisi | KANAL | Fon ve hisse işlemleri |

### 3.3 Servis bağımlılıkları

| service_id | depends_on |
|---|---|
| TRANSFER_API | IBAN_VALIDATION, EFT_GATEWAY, CUSTOMER_PROFILE, NOTIFICATION |
| BILL_PAYMENT | BILLER_INTEGRATION, ACCOUNT_SERVICE, NOTIFICATION |
| AUTH_SERVICE | OTP_SERVICE |
| ACCOUNT_SERVICE | CUSTOMER_PROFILE |
| CARD_SERVICE | ACCOUNT_SERVICE |

### 3.4 Ekranlar ve ekran–servis eşlemesi

| screen_id | name | module | servisler |
|---|---|---|---|
| LOGIN | Giriş | Kimlik | AUTH_SERVICE, OTP_SERVICE |
| ACCOUNTS | Hesaplarım | Hesap | ACCOUNT_SERVICE |
| TRANSFER | Para Transferi | Ödeme | TRANSFER_API, IBAN_VALIDATION, CUSTOMER_PROFILE |
| BILL | Fatura Ödeme | Ödeme | BILL_PAYMENT, BILLER_INTEGRATION |
| CARDS | Kartlarım | Kart | CARD_SERVICE |
| LOANS | Kredilerim | Hesap | ACCOUNT_SERVICE |
| INVEST | Yatırım | Yatırım | INVEST_SERVICE |
| PROFILE | Profil ve Ayarlar | Hesap | CUSTOMER_PROFILE, NOTIFICATION |

> **Bilerek döviz ekranı yok.** S4'teki "Döviz Alarmı" talebinin **yeni ekran** olarak sınıflanması buna bağlı. Kataloğa döviz ekranı eklenirse S4 bozulur.

**TRANSFER `flow_definition`** (M2.2 için):
```json
["Transfer türü seç (EFT/Havale)", "Alıcı IBAN gir", "Alıcı adı doğrula", "Tutar ve açıklama gir", "Özet ve onay", "Sonuç ve dekont"]
```
Diğer ekranlar için 3–5 adımlık benzer listeler.

### 3.5 Ekran öğeleri (Joyride hedefleri — `contracts.md` ile birebir)

| screen_id | element_id | label |
|---|---|---|
| LOGIN | login-username / login-password / login-submit | Kullanıcı adı / Şifre / Giriş |
| ACCOUNTS | accounts-list / accounts-goto-transfer / accounts-goto-bill | Hesap listesi / Para gönder / Fatura öde |
| TRANSFER | transfer-tab-eft / transfer-tab-havale | EFT sekmesi / Havale sekmesi |
| TRANSFER | transfer-iban-input / transfer-amount-input / transfer-desc-input / transfer-submit | Alıcı IBAN / Tutar / Açıklama / Gönder |
| BILL | bill-biller-select / bill-subscriber-input / bill-amount-input / bill-submit | Kurum / Abone no / Tutar / Öde |
| (ortak) | nav-accounts / nav-transfer / nav-bill | Alt menü |

### 3.6 Hata kodları

| error_code | service_id | description | severity |
|---|---|---|---|
| **IBN-504** | IBAN_VALIDATION | IBAN doğrulama zaman aşımı | HIGH |
| IBN-400 | IBAN_VALIDATION | Geçersiz IBAN biçimi | LOW |
| TRF-422 | IBAN_VALIDATION | Alıcı adı ile IBAN sahibi uyuşmuyor | MEDIUM |
| TRF-409 | TRANSFER_API | Günlük transfer limiti aşıldı | MEDIUM |
| EFT-503 | EFT_GATEWAY | EFT sistemi geçici olarak kapalı | MEDIUM |
| **BIL-221** | BILL_PAYMENT | Ödenen tutar fatura tutarından düşük | MEDIUM |
| BIL-404 | BILLER_INTEGRATION | Abone numarası bulunamadı | LOW |
| BIL-502 | BILLER_INTEGRATION | Fatura kurumundan yanıt alınamadı | HIGH |
| AUT-401 | AUTH_SERVICE | Hatalı şifre denemesi | LOW |
| OTP-408 | OTP_SERVICE | SMS şifresi gecikmeli iletildi | MEDIUM |
| ACC-500 | ACCOUNT_SERVICE | Bakiye bilgisi alınamadı | HIGH |
| CRD-500 | CARD_SERVICE | Kart limiti görüntülenemedi | MEDIUM |
| PRF-409 | CUSTOMER_PROFILE | Profil güncelleme çakışması | LOW |
| INV-503 | INVEST_SERVICE | Fiyat servisi yanıt vermiyor | MEDIUM |
| NTF-500 | NOTIFICATION | Bildirim gönderilemedi | LOW |

### 3.7 Çağrı kategorileri ve öncelikler (enum — prompt şemalarıyla aynı)

- Kategori: `PARA_TRANSFERI`, `FATURA`, `GIRIS`, `HESAP`, `KART`, `DIGER`
- Öncelik: `DUSUK`, `ORTA`, `YUKSEK`, `KRITIK` (severity HIGH → YUKSEK, MEDIUM → ORTA, LOW → DUSUK; müşteri işlemi tamamlayamıyorsa bir üst seviye)

---

## 4. Senaryo kayıtları (elle — `scenarios.json`)

Bu değerler demo ve sunumdaki rakamların kaynağıdır. **Değiştirilirse sunum ve mockup'lar da güncellenmeli.**

### S1 — Eşleşmeli çağrı (IBN-504)

**Çözüm kaydı**

| alan | değer |
|---|---|
| solution_id | SOL-014 |
| error_code | IBN-504 |
| symptom | EFT gönderiminde "İşleminiz şu an gerçekleştirilemiyor" hatası, IBAN doğrulama zaman aşımı |
| root_cause | IBAN doğrulama istemcisinin bağlantı havuzu yoğun saatlerde doluyor; 5 sn zaman aşımı aşılıyor |
| steps | 1) Son 15 dk havuz doluluğunu kontrol et 2) Havuz limitini 20 → 60, zaman aşımını 5 → 8 sn yap 3) Kalıcı çözüm: istemciye yeniden deneme politikası |
| fix_effort_md | 3.0 |

**6 çözülmüş geçmiş çağrı:** CAG-0871, CAG-0912, CAG-0955, CAG-0978, CAG-1003, CAG-1021 — hepsi `screen_id=TRANSFER`, `error_code=IBN-504`, `solution_id=SOL-014`, `team_id=ODEME`, `status=closed`, `resolution_minutes` 35–90. Metinleri §6.1 ile üretilir ama elle gözden geçirilir; hepsi "EFT gönderemedim / IBAN hatası / zaman aşımı" anlamında olmalı.

**Demo anı:** CAG-1042 demoda canlı oluşur, veride önceden yoktur. Çağrı numarası sayacı 1042'den başlar.

### S2 — Eşleşmesiz çağrı (BIL-221)

- CAG-1043 demoda canlı oluşur (Fatura Ödeme, 100,005 TL).
- **Yasak kural:** Geçmiş çağrılarda `BIL-221` kodlu veya "eksik ödeme / kuruş / yuvarlama" içerikli **hiçbir kayıt olmayacak**. Ayrıca `solutions` içinde BIL-221 çözümü yok. Aksi halde eşleşme çıkar ve kod analizi demosu bozulur.
- `sample-codebase/` içeriği: görev M1.4-d.

### S3 — Para Transferi'ne değişiklik talebi

**Son 30 gündeki TRANSFER çağrıları (18.09–17.10.2026): toplam 312**

| error_code / kategori | adet | oran |
|---|---|---|
| IBN-504 | 128 | %41 |
| TRF-422 | 72 | %23 |
| TRF-409 | 44 | %14 |
| EFT-503 | 34 | %11 |
| kodsuz (DIGER) | 34 | %11 |

> 6 S1 çağrısı bu 128'in içinde olabilir (tarihleri son 30 gün içindeyse) — sayım toplamı 312'yi bozmamalı.

**4 benzer geçmiş talep**

| request_id | type | screen_id | title | effort_md |
|---|---|---|---|---|
| TLP-0142 | existing_change | BILL | Fatura ödemede kayıtlı faturaları listeleme | 15 |
| TLP-0156 | existing_change | TRANSFER | Havale ekranında son alıcılar listesi | 17 |
| TLP-0171 | existing_change | TRANSFER | EFT'de alıcıyı kaydetme seçeneği | 19 |
| TLP-0188 | existing_change | ACCOUNTS | Hesaplarım'da favori hesap sıralama | 22 |

→ medyan 18, aralık 15–22.

- **Yasak kural:** Diğer 96 geçmiş talepte "favori / kayıtlı alıcı / son alıcılar" içeren başka talep olmayacak; olursa ilk 5 değişir.

**ODEME ekip takvimi**

| team_id | date_from | date_to | allocation_pct | note |
|---|---|---|---|---|
| ODEME | 2026-10-12 | 2026-11-08 | 100 | Yıl sonu regülasyon projesi |
| ODEME | 2026-11-09 | 2027-01-31 | 8 | Rutin destek |

**Doğrulama hesabı** (bir geliştirici × %92 boş = 0,92 adam-gün/iş günü, hafta sonu hariç):
- 18 adam-gün → 20. iş günü → **9 Kasım – 4 Aralık 2026** ✔
- 18 + 3 (IBN-504 kalıcı çözümü) = 21 adam-gün → 23. iş günü → **bitiş 9 Aralık 2026** ✔

**Etki analizi beklentisi:** Transfer API (yüksek), Müşteri Profil Servisi (orta), IBAN Doğrulama (düşük).

### S4 — Yeni ekran: Döviz Alarmı

- Katalogda döviz ekranı yok (§3.4).
- `field_standards` içinde **Kur**, **Döviz Kodu**, **Müşteri No**, **Alarm Geçerlilik** mutlaka olacak (M2.3-a).
- Geçmiş taleplerde "döviz alarmı" yok.

---

## 5. Betikle üretilecek veriler (`generate.py` — Faker tr_TR, seed 42)

### 5.1 Loglar (~3000, son 45 gün)
- Seviye dağılımı: INFO %80, WARN %12, ERROR %8.
- Her satır: rastgele `session_id` (uuid), ekran (ağırlık: TRANSFER %30, ACCOUNTS %25, BILL %15, LOGIN %15, diğerleri %15), ekranın servislerinden biri.
- WARN/ERROR satırlarında hata kodu, servisle uyumlu (§3.6); INFO'da kod yok.
- Mesaj şablonları kodda: `"{service} timeout after {ms}ms"`, `"{service} returned {code}"`, `"Request completed in {ms}ms"`.
- Son 30 günde TRANSFER için IBN-504 ERROR logları yoğun olsun (S3 hikâyesiyle tutarlı).
- **Yasak:** BIL-221 log satırı üretme (demo sırasında canlı oluşacak).

### 5.2 Geçmiş çağrılar (~400, son 90 gün)
- Önce S3'ün 312 TRANSFER çağrısı (son 30 gün, §4 dağılımıyla), sonra S1'in 6 kaydı (sabit numaralar), sonra kalan ~80 çağrı diğer ekranlara.
- Her çağrı: `user_text` (texts.json'dan, kategori ve hata koduna uygun olanı seç), `category`, `priority`, `service_id`, `team_id`, `error_code`, `solution_id` (varsa), `resolution_minutes` (lognormal, 20–600), `status=closed`.
- `incident_id`: CAG-0001'den başlayıp tarih sırasıyla; S1 numaralarını koru; son numara < 1042.
- **Yasak:** BIL-221 veya yuvarlama/kuruş içerikli çağrı.

### 5.3 Çözüm bilgi bankası (~60)
- SOL-014 sabit (S1). Diğerleri her hata kodu için 2–5 çözüm, metinler texts.json'dan.
- `fix_effort_md`: 1–8 arası.
- BIL-221 için çözüm **yok**.

### 5.4 Geçmiş talepler (~100, son 18 ay)
- S3'ün 4 talebi sabit. Diğer 96: tip dağılımı existing_change %70 / new_screen %30; ekranlar katalogdan; efor 3–60 adam-gün (lognormal, medyan ~15); `affected_services` ekranın servislerinden 1–3'ü; başlangıç/bitiş tarihleri tutarlı.
- **Yasak:** favori/kayıtlı alıcı ve döviz alarmı içerikli talep.

### 5.5 Ekip takvimi (bugünden itibaren 3 ay)
- ODEME §4'teki gibi sabit.
- Diğer ekipler: 2–4 dönem, %20–%100 arası doluluk, rastgele.

---

## 6. Foundry ile metin üretimi (`generate_texts.py`)

**Ayarlar:** Foundry'deki `chat` deploy'u · temperature 0.8 (çeşitlilik için; uygulamadaki 0.1'den farklı) · JSON şemalı çıktı · 20'şerli partiler · sonuç `data/seed/texts.json` (commit'lenir, tekrar üretilmez).

**Tahmini maliyet:** ~360 metin, birkaç bin token/parti → ihmal edilebilir; Copilot bütçesine yazılmaz.

### 6.1 Prompt: `gen-cagri-metni` (müşteri ağzından çağrı metinleri)

```
## system
Sen bir bankanın mobil uygulama destek kayıtları için sentetik test verisi üreten bir yardımcısın.
Üreteceğin metinler gerçek kişi, kurum, telefon, TCKN, IBAN, kart numarası veya adres İÇERMEZ.
Metinler müşterinin "Sorun yaşıyorum" ekranına yazdığı kısa, doğal Türkçe cümlelerdir:
- 3–20 kelime, günlük dil, bazen yazım hatası, bazen büyük harf/ünlem, bazen aciliyet ("acil", "maaşım yattı mı").
- Teknik terim kullanmaz (IBAN hariç), hata kodunu bilmez.
- Aynı partideki metinler birbirini tekrar etmez; farklı durum ve tonlar kullan.

## user
Ekran: {{screen_name}}
Sorunun teknik karşılığı (müşteri bunu bilmez): {{error_description}}
Kategori: {{category}}
Adet: {{count}}
Örnekler (bu tarzda ama bunları tekrar etme):
- "para gönderemiyorum sürekli hata veriyor"
- "eft yaptım işlem gerçekleştirilemiyor diyor acil kira ödemem lazım"

Çıktı şeması: {"items": [{"text": string}]}
```

**Çağırma planı:** Her (ekran, hata kodu) çifti için 8–15 metin; kodsuz kategoriler (DIGER) için genel şikâyetler. Toplam ~200 farklı metin; betik bunları 400 çağrıya tekrar dağıtır.
**Hariç:** BIL-221 için metin üretme.

### 6.2 Prompt: `gen-cozum-metni` (çözüm bilgi bankası)

```
## system
Bankacılık uygulaması için sentetik bir çözüm bilgi bankası kaydı üretiyorsun.
Kayıtlar L2 destek ve geliştirme ekipleri içindir; kısa, teknik ve uygulanabilir olmalıdır.
Gerçek ürün, kurum veya kişi adı kullanma. Sunucu adı, IP, şifre gibi bilgiler uydurma; genel ifade kullan
("ilgili servis", "uygulama sunucusu").

## user
Hata kodu: {{error_code}} — {{error_description}}
Servis: {{service_name}} ({{service_description}})
Farklı kök nedenlere dayanan {{count}} çözüm kaydı üret.

Çıktı şeması:
{"items": [{"symptom": string (≤ 25 kelime),
            "root_cause": string (≤ 30 kelime),
            "steps": [string] (2–4 adım, her biri ≤ 20 kelime),
            "fix_effort_md": number (1–8, kalıcı çözüm eforu)}]}
```

**Çağırma planı:** Her hata kodu için 2–5 kayıt (IBN-504 için 2 ek kayıt; ana kayıt SOL-014 elle). **Hariç:** BIL-221.

### 6.3 Prompt: `gen-talep-metni` (geçmiş geliştirme talepleri)

```
## system
Bir bankanın dijital kanallar birimi için sentetik geliştirme talepleri üretiyorsun.
Talepler iş biriminin ağzından, 1–2 cümle, net bir ihtiyaç tarif eder.
Gerçek ürün/kurum/kişi adı kullanma. Aşağıdaki konularda talep ÜRETME:
favori alıcı, kayıtlı alıcı, son alıcılar listesi, döviz alarmı, kur alarmı.

## user
Ekran: {{screen_name}} (yoksa "Yeni ekran")
Talep türü: {{type}}  (existing_change: mevcut ekranda değişiklik / new_screen: yeni ekran)
Adet: {{count}}

Çıktı şeması: {"items": [{"title": string (≤ 10 kelime), "description": string (1–2 cümle)}]}
```

**Çağırma planı:** Her ekran için 8–10 existing_change, ek olarak 25–30 new_screen talebi. Toplam ~100.

### 6.4 Üretim sonrası kontrol (betik içinde, otomatik)
- Yasak kelime listesi (`favori`, `kayıtlı alıcı`, `son alıcı`, `döviz alarm`, `kur alarm`, `kuruş`, `yuvarla`, `eksik ödeme`) geçen metinler atılır ve loglanır.
- Rakam dizisi 10+ hane (IBAN/TCKN benzeri), `@` (e-posta) veya `+90` içeren metinler atılır.
- Aynı metnin tekrarı atılır.
- Atılan metin sayısı > %20 ise partiyi yeniden üret.

---

## 7. Doğrulama (yükleme sonrası, 1. gün öğle öncesi)

| Kontrol | Sorgu / yöntem | Beklenen |
|---|---|---|
| Hacimler | `SELECT COUNT(*)` her tablo | logs ~3000, incidents ~400, solutions ~60, requests ~100 |
| S1 kaynakları | `incidents WHERE solution_id='SOL-014'` | 6 kayıt (CAG-0871…1021) |
| S2 temizliği | `incidents/solutions/logs WHERE error_code='BIL-221'` | 0 kayıt |
| S3 çağrı sayısı | TRANSFER, son 30 gün, `GROUP BY error_code` | 312 = 128/72/44/34/34 |
| S3 talepler | AI Search `requests`: "Para Transferi ekranında kayıtlı alıcıları favori olarak seçebilelim" | ilk 4: TLP-0171, 0156, 0142, 0188 (sıra değişebilir) |
| S3 takvim | `schedule(18, …)` ve `schedule(21, …)` | 09.11–04.12 ve bitiş 09.12 |
| S4 | `screens` içinde döviz ekranı | yok |
| Eşleşme kalibrasyonu | M1.4-a ile S1 ve S2 sorguları | S1 ≥ 0,90 · S2 < 0,75 |
| Kişisel veri | `texts.json` üzerinde regex taraması | 0 eşleşme |

Bu tablo `docs/demo-scenarios.md` (Q2) ile birlikte senaryo testi olarak kullanılır.

---

## 8. Bugün (kod yazmadan) yapılabilecekler

- §3 ve §4 tablolarını analist gözüyle gözden geçirmek: isimler, hata kodları, kategoriler gerçekçi mi?
- §6 prompt'larını Foundry yerine herhangi bir sohbet aracında **2–3 örnekle** denemek (çıktı tarzını görmek için; üretilen metinler yarın kullanılmaz, yarın Foundry ile yeniden üretilir).
- Soru bankası ve alan standartlarını (M2.3-a) metin olarak hazırlamak.
