# Mercek — Hackathon Kapsamı

**Takım:** AI Overflow (5 kişi) · **Proje:** Mercek · **Tema:** 2
**Tarih:** 16–17 Ekim 2026 (Cuma–Cumartesi)
**Slogan:** "Soruna odaklanır, çözümü netleştirir."

**Tek cümle:** Mercek, banka çalışanlarının ve teknoloji ekiplerinin işlem ekranlarında yaşadığı sorunları loglardan, çağrı geçmişinden ve koddan besleyerek anında açıklayan, çağrıları doğru servise yönlendirip birleştiren ve iş birimlerinden gelen talepleri servis bazlı etki, adam-gün tahmini ve takvimle plana dönüştüren bir yapay zekâ asistanıdır.

**Senaryolar:** `mercek-demo-senaryo-onerileri.md` (A–F). Bu doküman, o senaryoları taşıyan kapsamı tanımlar.

---

## Hedef kullanıcılar

Mercek'i **banka çalışanları ve teknoloji ekipleri** kullanır; son kullanıcı (müşteri) Mercek'i doğrudan kullanmaz.

| Kullanıcı | Örnek karakter | Mercek'i nerede kullanır |
|---|---|---|
| Şube müşteri temsilcisi | Elif | İşlem ekranındaki "Sorun yaşıyorum" butonu (bağlamlı Mercek paneli) |
| Çağrı merkezi temsilcisi | Zeynep | Mercek sohbet sayfası |
| L2 destek / platform yöneticisi | Kerem | Mercek sohbet sayfası ve çağrı kayıtları |
| İş birimi (bölüm başkanlığı) | Fatma, Hakan | Talep Yönlendirme |
| İş analisti (teknoloji) | Ayşe | Talep Yönlendirme |
| Banka müşterisi (Mercek'i kullanmaz) | Mehmet | İnternet şubesi; sorun yaşayınca çağrı merkezini arar |

## Uygulama zemini

Simüle edilen iç bankacılık uygulaması `COPILOT_REBUILD_GUIDE.md`'ye göre kurulur:
- **Ana modüller:** Bankacılık · Mercek (sohbet) · Talep Yönlendirme
- **İşlem ekranları:** `KRTTBASV`, `KRDTKULL`, `ODMTFATR`, `MUSTGUNC`, `HSPTVDSZ`
- **Teknoloji:** Next.js 16 (frontend) + FastAPI (backend)
- **Hazır parçalar:** Sahte kimlik doğrulama, ekran kodu çubuğu, Joyride senaryoları, Kibana uyumlu sentetik log üretici

Mercek bu zeminin üzerine iki modül olarak eklenir.

---

## Modül 1 — Akıllı Problem Çözüm ve Çağrı Yönetimi

| # | Özellik | Ne yapar | Senaryo |
|---|---|---|---|
| M1.1 | Bağlamlı sorun bildirimi | Ekrandaki "Sorun yaşıyorum" butonu Mercek'i ekran kodu, müşteri no, son `trace.id` ve hata mesajıyla açar. Sohbet sayfasında serbest metinden ekran, kurum, abone no ve müşteri no çıkarılır. | A, B |
| M1.2 | Log inceleme ve örüntü analizi | İlgili işlemin logunu bulur. Hataları kurum, ekran, hata kodu, numara uzunluğu ve zamana göre gruplayıp olağan dışı örüntüyü gösterir. İş kuralı reddini teknik hatadan ayırır. | A, B, C, F |
| M1.3 | Çağrı zenginleştirme, servis ataması, ana kayıt | Çağrıyı yapılandırılmış kayda dönüştürür, kuralla ilgili servise atar. Aynı sorundaki vakaları yeni çağrı açmadan ana kayda bağlar. Temsilciye müşteriye söylenecek hazır açıklamayı verir. | B, C |
| M1.4 | Çözüm eşleştirme, duyuru araması, kod analizi | Geçmiş çözümlerle eşleştirir (eşik %75). Eşleşme yoksa kurum duyurularında arar ve ilgili kodu okuyup düzeltme önerir. | B, C |
| M1.5 | "Bana göster" | Mercek'in önerdiği değerlerle ekranı Joyride turuyla doldurur. | A |
| M1.6 | Etki ölçümü | Önlenen çağrı, birleştirilen vaka ve süre ölçümleri (iş değeri kanıtı). | A, B |
| M1.7 | Günlük durum özeti | Sohbetle "bugün en çok sorun yaşanan ekran" özeti. | F |

## Modül 2 — Akıllı Talep Analizi, Efor ve Takvim Planlama

| # | Özellik | Ne yapar | Senaryo |
|---|---|---|---|
| M2.1 | Talep analizi ve sınıflandırma | Talebi netleştirip bileşenlere ayırır. Tipini (mevcut ekran değişikliği, yeni ekran, batch işi, karma) ve ilgili ekranları ekran kataloğundan belirler. | D, E |
| M2.2 | Değişiklik önerisi ve netleştirilecek sorular | Mevcut ekranda neyin değişeceğini tarif eder. Netleştirilecek soruları benzer taleplerden gelen varsayılan önerilerle çıkarır. | D, E |
| M2.3 | Yeni ekran kapsamı | Kurala uygun ekran kodu önerir (`[A-Z]{3}[TR][A-Z0-9]{4}`, çakışma kontrolü). Mevcut bileşen ve standartlardan ekran taslağı türetir. | E |
| M2.4 | Servis bazlı etki analizi | Ana servisi ve etkileşimli servisleri gerekçeleriyle belirler. | D, E |
| M2.5 | Adam-gün tahmini ve takvim | Benzer geçmiş taleplerden bileşen bazlı medyan a/g; servis takvimine göre plan. Kapasite çatışmasını ve talepler arası bağımlılığı seçenekleriyle gösterir. | D, E |
| M2.6 | Köprü: veriden kapsam | Çağrı geçmişiyle talebin değerini kanıtlar; müşteri ve çağrı verisiyle eksik kapsamı yakalar (SMS kanalı, proaktif bilgilendirme). | D, E |

**Dil ve ölçü:** Teknoloji tarafı **servis** bazlı anlatılır (Kredi Kullandırım, Kredi Takip, Müşteri Yönetim, Fatura Ödeme, Hesap Yönetim, Kart Başvuru). Tahminler yalnızca **adam-gün** ve takvimdir; ücret hesaplanmaz.

## Ortak veri katmanı (tamamen sentetik)

İşlem logları, müşteri ve kredi portföyü, çağrı kayıtları, çözüm bilgi bankası, kurum duyuruları arşivi, geçmiş talepler, servis kataloğu ve takvimi, ekran kataloğu. Ayrıntı: `mercek-sentetik-veri-plani.md` ve `mercek-sentetik-veri-uretimi.md`.

## Kapsam dışı

- Gerçek Kibana, çağrı sistemi, kod reposu ve takvim entegrasyonları (sentetik veriyle simüle edilir)
- Gerçek müşteri verisi
- Önerilen kod düzeltmelerinin otomatik uygulanması (Mercek yalnızca önerir)
- E-posta ve SMS'in gerçekten gönderilmesi (gönderim kaydı simüle edilir)

## Öncelik (MoSCoW)

| Öncelik | İçerik | Taşıdığı senaryo |
|---|---|---|
| **Must** | Temel uygulama (rebuild Faz 1–5) · M1.1 · M1.2 · M1.3 · M1.4 (eşleştirme ve kod analizi) · M2.1 · M2.2 · M2.4 · M2.5 (tahmin ve takvim) · M2.6 | A, B, C, D |
| **Should** | Joyride (rebuild Faz 7) ve M1.5 · M1.6 · M1.4 kurum duyuruları araması | A'nın "Bana göster" anı, iş değeri ölçümü, C'nin proaktif bulgusu |
| **Could** | M2.3 yeni ekran · M2.5 kapasite çatışması ve bağımlılık · M1.7 | E, F |
| **Won't** | Gerçek entegrasyonlar, gerçek gönderim, gerçek veri | — |

## Sunum ve demo yaklaşımı

- **Sunumda tüm senaryolar (A–F)** bir "kullanım senaryoları" slaytında kısaca yer alır; Mercek'in kapsamı böylece eksiksiz görünür.
- **Canlı demoda yalnızca çalışır durumdakiler** gösterilir. Öncelik sırası: **A → B → D → C**. Hazır olmayanlar ekran görüntüsü veya kısa videoyla geçilir.
- Hangi senaryoların canlı gösterileceğine **2. gün 12:00 kod dondurmada** karar verilir.

## Teknik kararlar

- **Mimari:** Next.js 16 (frontend) ve FastAPI (backend) iki ayrı Azure App Service'te (aynı plan). LLM: Azure AI Foundry (sohbet + embedding modeli). Veri: Azure SQL. Arama: Azure AI Search (çözümler, talepler, duyurular).
- **Hesabı kod yapar, AI açıklar:** Uygun kredi tutarı, örüntü sayıları, eşik kararları, servis ataması, a/g medyanı, takvim ve kapasite hesabı deterministik koddadır. AI özetler, sınıflandırır, soruları ve açıklamaları yazar, kodu yorumlar.
- **Log kaynağı:** Rebuild Faz 5 log üreticisi (ECS uyumlu), senaryo kayıtlarıyla zenginleştirilir ve Azure SQL'e yüklenir. Kibana kurulmaz (Faz 6 yalnızca doküman).
- **Kod analizi:** Mercek uygulamanın kendi kodunu okur; kasıtlı hata gömülmez (C senaryosundaki 6–12 hane kuralı uygulamanın gerçek kuralıdır).

## Zaman planı (resmi takvime göre)

| Zaman | Hedef |
|---|---|
| 1. gün 08:00–10:30 | Kayıt, bilgilendirme, açılış (kod yok); VDI/Azure/GitHub girişleri |
| 1. gün 10:30–13:30 | Rebuild Faz 1 iskelet, CI/CD, Azure kaynakları, Faz 2–4 başlangıcı, veri üretimi → altyapı öğlene yeşil |
| 1. gün 14:30–19:00 | Faz 2–4 tamam, Faz 5 log üretici, Mercek backend temeli; A ve B'nin Must parçaları |
| 1. gün 20:00–gece | C ve D'nin Must parçaları, senaryo testleri |
| 2. gün 09:30–12:00 | Should'lar (Joyride, "Bana göster", duyuru araması, ölçüm), entegrasyon |
| **2. gün 12:00** | **Kod dondurma** ve canlı demoya girecek senaryoların seçimi |
| **2. gün 13:00–14:00** | **Teknik değerlendirme (AstreAI)** |
| 2. gün 12:00–14:45 | Ekran görüntüleri, demo videosu, sunum, prova |
| 2. gün 15:00–17:20 | Sunumlar (5 dk) |
