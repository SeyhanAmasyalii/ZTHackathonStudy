# Mercek — Sentetik Veri Planı

> **Nasıl üretileceği** (katalog değerleri, senaryo rakamları, Faker kuralları, Foundry metin prompt'ları, doğrulama sorguları): `mercek-sentetik-veri-uretimi.md`.

## Temel ilke: senaryo güdümlü veri
Önce demo senaryoları yazılır, veri bu senaryoları "taşıyacak" şekilde üretilir. Rastgele veri demoda hiçbir şey kanıtlamaz; hikâyeye gömülü kayıtlar (eşleşen geçmiş çağrı, hatalı SP, yoğun çağrı alan ekran) demonun kalbidir.

## Demo senaryoları
- **S1 – Eşleşmeli çağrı:** Para Transferi ekranında EFT gönderiminde zaman aşımı. Loglarda IBAN doğrulama servisinde timeout (IBN-504). Geçmişte aynı hata koduyla çözülmüş 6 çağrı var → Mercek eşleşen çözümü önerir.
- **S2 – Eşleşmesiz çağrı:** Fatura Ödeme ekranında tutar yanlış yuvarlanıyor (BIL-221). Geçmişte benzeri yok → Mercek ilgili servis kodu + SP'yi inceler, SP'deki hatalı yuvarlama satırını işaret eder.
- **S3 – Mevcut ekran değişikliği:** "Para Transferi ekranında kayıtlı alıcıları favori olarak seçebilelim" talebi → 4 benzer geçmiş talep (15–22 adam-gün), etkilenen servisler, maliyet ve takvim (9 Kasım–4 Aralık); ekranın 30 günlük 312 çağrısı gösterilip IBN-504 kalıcı çözümünü kapsama ekleme önerilir (+3 adam-gün, bitiş 9 Aralık).
- **S4 – Yeni ekran:** "Döviz alarmı" talebi → soru setiyle kapsam olgunlaştırma, alan standartlarına göre tasarım önerisi. (Katalogda döviz ekranı bilerek yok.)

## Varlıklar ve hacimler
| Varlık | Adet | Önemli alanlar | Kullanıldığı yer |
|---|---|---|---|
| Ekranlar ve öğeleri | 8 ekran, 19 öğe | ekran_id, ad, modül, servisler, akış, öğe id'leri | M1.1, M1.5, M2.1–2.4 |
| Alan standartları | 10 | alan, tip, format, doğrulama, maskeleme, örnek | M2.3 |
| Servisler ve ekipler | 12 servis, 5 ekip | servis, ekip, bağımlılıklar | M1.3, M2.4 |
| Hata kodları | 15 | kod, servis, açıklama, önem | M1.2, M1.3 |
| Hata logları | ~3.000 | zaman, oturum, ekran, servis, seviye, hata_kodu, mesaj | M1.2 |
| Geçmiş çağrılar | ~400 | ekran, kategori, açıklama, servis, çözüm_id, çözüm_süresi | M1.4, M2.6 |
| Çözüm bilgi bankası | ~60 | hata_kodu, belirti, kök neden, çözüm adımları, düzeltme eforu | M1.4 (AI Search) |
| Kod / VT nesneleri | 6 dosya | servis kodu, SP'ler (S2 hatası gömülü) | M1.4 |
| Geçmiş talepler | ~100 | tip, ekran, açıklama, etkilenen servisler, efor | M2.5 |
| Ekip takvimi | 3 ay | ekip, doluluk dönemleri | M2.5 |
| Soru bankası | 12 soru | soru, amaç, cevap tipi | M2.3 |

Ekranlar: Giriş, Hesaplarım, Para Transferi (EFT/Havale), Fatura Ödeme, Kartlarım, Kredilerim, Yatırım, Profil ve Ayarlar.

## Üretim yöntemi (yarın, VDI'de)
1. **Katalog ve senaryo kayıtları → elle:** `catalog.json` ve `scenarios.json`, `mercek-sentetik-veri-uretimi.md` §3–4'teki tablolardan.
2. **Doğal dil alanları → Foundry'deki model:** Çağrı, çözüm ve talep metinleri, §6'daki prompt'larla. Bu maliyet Copilot bütçesine yazılmaz.
3. **Yapısal veri → Python + Faker (tr_TR) betiği:** Loglar, geçmiş çağrılar, talepler, takvim. Sabit seed, tekrar çalıştırılabilir, repoda durur → Repo Kodu puanına da katkı.
4. **Yükleme:** Yapısal veri Azure SQL'e, çözüm/çağrı/talep metinleri AI Search indekslerine, kod/VT nesneleri repoda `sample-codebase/` altında.
5. **Doğrulama:** §7'deki sorgularla senaryo rakamlarının tuttuğu kontrol edilir.

**Dikkat:** Büyük veri setlerini Copilot'a ürettirmeyin — çıktı token'ı bütçeyi hızla tüketir. Copilot'tan yalnızca üreten betiği yazmasını isteyin.

## Bugün (kod yazmadan) yapılabilecekler
- Katalog ve senaryo tablolarını analist gözüyle gözden geçirmek
- Foundry metin prompt'larını bir sohbet aracında 2–3 örnekle denemek
- Soru bankası ve alan standartlarını metin olarak hazırlamak
