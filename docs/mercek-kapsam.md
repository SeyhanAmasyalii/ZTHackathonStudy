# Mercek — Hackathon Kapsamı (taslak)

**Takım:** AI Overflow (5 kişi) · **Proje:** Mercek · **Tema:** 2
**Tarih:** 16–17 Ekim 2026 (Cuma–Cumartesi). Önceden kod yazılması istenmiyor; hazırlık günü yalnızca tasarım, pratik ve planlama.

**Tek cümle:** Mercek, banka uygulamalarında yaşanan sorunları kullanıcı daha çağrı açarken tespit eden, doğru ekibe yönlendirip çözüm öneren ve bu çağrı birikimini yeni geliştirme taleplerinin kapsamına, maliyetine ve takvimine dönüştüren yapay zekâ asistanıdır.

**Slogan:** "Soruna odaklanır, çözümü netleştirir."

**Hedef kullanıcılar:** Banka uygulaması kullanıcısı, destek/operasyon ekipleri, iş birimi ve analistler, takım liderleri.

## Modül 1 — Akıllı Problem Çözüm ve Çağrı Yönetimi Asistanı
1. **Bağlamlı sorun bildirimi:** Simüle banka uygulamasında "Sorun yaşıyorum" → ekran ve oturum bilgisi otomatik yakalanır.
2. **Proaktif hata inceleme:** O ekran/oturuma ait hata logları (Kibana benzeri sentetik log deposu) anlık taranır; olası neden çağrı açılmadan söylenir.
3. **Talep zenginleştirme ve servis tespiti:** Serbest metin + log + ekran bilgisi → düzenli çağrı kaydı; ilgili servise/ekibe otomatik yönlendirme.
4. **Geçmiş çözüm eşleştirme ve öneri:** Geçmiş çözümlerle anlamsal eşleştirme; eşleşme yoksa ilgili kod ve VT nesneleri (küçük sentetik set) AI ile incelenip çözüm tavsiyesi.
5. **Çözümün görsel anlatımı:** Simüle ekranda adım adım rehberli tur (React Joyride) / animasyonlu ekran görüntüleri; video opsiyonel.

## Modül 2 — Akıllı Talep Analizi, Maliyet ve Takvim Planlama
1. **Talep sınıflandırma:** Mevcut ekran değişikliği mi, yeni ekran mı?
2. **Mevcut ekran değişikliği:** Mevcut çalışan akışa benzetme ve akış önerisi.
3. **Yeni ekran:** Soru setleriyle kapsam olgunlaştırma; alan metadata'sına dayalı tasarım önerisi (ör. "Müşteri No alanı şu formatta/doğrulamayla olmalı").
4. **Etki analizi:** Etkilenecek servislerin tespiti.
5. **Maliyet ve takvim:** Benzer geçmiş taleplerden efor/maliyet tahmini; ekip takvimine göre plan önerisi.
6. **Çağrı verisiyle kapsam zenginleştirme (modüller arası köprü):** Ekranın aylık çağrı adedi ve kategorileri; bu sorunların çözümlerini kapsama ekleme önerisi.

## Ortak veri katmanı (tamamen sentetik)
Ekran kataloğu ve alan metadata'sı, servis haritası, hata logları, geçmiş çağrılar ve çözümleri, örnek kod ve VT nesneleri, geçmiş talepler ve maliyetleri, ekip takvimi. Ayrıntı: `mercek-sentetik-veri-plani.md` ve `mercek-sentetik-veri-uretimi.md`.

## Kapsam dışı
Gerçek Kibana/kod reposu/takvim entegrasyonları, gerçek müşteri verisi, önerilen çözümün otomatik uygulanması.

## Öncelik (MoSCoW)
| Öncelik | İçerik |
|---|---|
| Must | M1.1–1.4 uçtan uca · M2.1 · M2.4 · M2.5 (basit) |
| Should | M1.5 (Joyride) · M2.3 · M2.6 |
| Could | M2.2 · metadata ile görsel ekran tasarım önerisi · video ile çözüm anlatımı |
| Won't | Gerçek entegrasyonlar, gerçek veri |

## Teknik kararlar (öneri)
- Çözüm anlatımında video yerine Joyride (ucuz, hızlı, demo riski düşük).
- Azure SQL: yapısal veri (çağrılar, talepler, takvim, metadata). Azure AI Search: geçmiş çözüm eşleştirme. İkisi de gerçek iş yapan destek servisi.
- Demo hikâyesi tek ekran üzerinden ("Para Transferi"): M1 hatayı çözer → aynı ekrana değişiklik talebi → M2 çağrı geçmişini kapsama katar.

## Zaman planı (resmi takvime göre)
| Zaman | Hedef |
|---|---|
| 1. gün 08:00–10:30 | Kayıt, bilgilendirme, açılış (kod yok) — VDI/Azure/GitHub girişlerini bu arada test et |
| 1. gün 10:30–13:30 | Repo iskeleti, CI/CD, App Service + /health, Foundry model, Azure SQL, sentetik veri üretimi → altyapı puanları öğlene yeşil |
| 1. gün 14:30–19:00 | Must maddeleri, iki modül paralel |
| 1. gün 20:00–gece | Must tamamlama, Should'a başlangıç (çalışma ertesi güne kadar sürebilir) |
| 2. gün 09:30–12:00 | Should maddeleri, entegrasyon, hata düzeltme |
| **2. gün 12:00** | **Kod dondurma** — son pipeline success, Security sekmesi temiz |
| **2. gün 13:00–14:00** | **Teknik değerlendirme (AstreAI)** — bu saatten önce her şey main'de ve yeşil olmalı |
| 2. gün 12:00–14:45 | Demo videosu, ekran görüntüleri, sunum (.pptx), prova |
| 2. gün 15:00–17:20 | Sunumlar (5 dk, sıra bilinmiyor) · 17:45 jüri · 18:45 ödül |

## Açık konular
- Takım içi sorumluluk seçimi (`mercek-is-plani.md` §2)
- Backend teknolojisi kararı (1. gün 10:30)
