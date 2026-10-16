# Mercek — Sentetik Veri Planı

> **Nasıl ve hangi değerlerle üretileceği** (tablolar, alanlar, senaryo rakamları, betikler, Foundry metin prompt'ları, doğrulama sorguları): `mercek-sentetik-veri-uretimi.md`.

## Temel ilke: senaryo güdümlü veri

Önce demo senaryoları yazıldı (`mercek-demo-senaryo-onerileri.md`), veri bu senaryoları taşıyacak şekilde üretilir. Rastgele veri demoda hiçbir şey kanıtlamaz. Mercek'in her sahnede gösterdiği rakam (47 istek, 412 hata, 186 çağrı, %58 e-posta izni, 4.870 müşteri…) veride önceden vardır. Mercek bu rakamları **SQL ve arama sorgularıyla kendisi hesaplar**; rakamlar ekrana elle yazılmaz.

## Veri setleri ve senaryolarla ilişkisi

| Veri seti | Hacim | Kaynak | Kullanan senaryo | Mercek'in kullanımı |
|---|---|---|---|---|
| **İşlem logları** (ECS, Kibana uyumlu) | ~10.000 + senaryo kayıtları | Rebuild Faz 5 log üreticisi + senaryo enjeksiyonu | A, B, C, F | Tek işlemin logunu bulma, örüntü analizi, durum özeti |
| **Ekran kataloğu** | 5 simüle + 15 yalnızca katalogda | Elle | A–E | Bağlam, sınıflandırma, ekran kodu çakışma kontrolü, bileşen yeniden kullanımı, kod dosya haritası |
| **Servis kataloğu ve hata–servis kuralları** | 7 servis, 17 kural | Elle | B, C, D, E | Servis ataması, etki analizi |
| **Servis takvimi** | 3 ay | Elle | D, E | Takvim ve kapasite çatışması |
| **Müşteri ve kredi portföyü** | 40.000 müşteri, 33.000 kredi | Betik (Faker) + senaryo kısıtları | D, E | Hedef grup ve izin dağılımı; etkilenen bölge müşterileri |
| **Müşteri temasları** | ~8.300 (90 gün) | Betik + Foundry metinleri | D, E | Köprü sayıları (konu temasları, bölgesel artış) |
| **Teknoloji çağrı kayıtları** | 1.400 (90 gün, CAG-0651…2050) + demo anında oluşanlar | Betik + Foundry metinleri | B, C | Ana kayıt, eşleşme, benzer geçmiş olaylar |
| **Çözüm bilgi bankası** | ~40 | Foundry + elle | B (C'de eşleşme olmaması için) | Geçmiş çözüm eşleştirme |
| **Kurum duyuruları arşivi** | 20 | Elle | C | Kök nedenin dış kaynağı, proaktif bulgu |
| **Geçmiş talepler** | ~100 | Betik + Foundry metinleri | D, E | Benzer talepler, a/g tahmini |
| **Değerlendirme seti** | 30 vaka (10 eşleşmeli, 10 eşleşmesiz, 10 talep) | Betik + Foundry taslağı, elle gözden geçirme | Kalibrasyon, jüri | Eşik ve arama kalitesini demo cümlelerinden bağımsız ölçme; indekse yüklenmez |
| **Demo kullanıcıları** | 8 | Elle (fake auth) | Hepsi | Elif, Mehmet, Zeynep, Kerem, Fatma, Hakan, Ayşe ve mevcut kullanıcılar |

## Senaryoların veride taşıması gerekenler (özet)

| Senaryo | Veride olması gereken |
|---|---|
| **A** · KRDTKULL | Elif kullanıcısının gelir alanı 38.000 TL; KRDTKULL uyarısı anında `AFFORDABILITY_EXCEEDED` olay logu (canlı); arka planda normal dağılımlı iş kuralı retleri |
| **B** · ODMTFATR Başkentgaz | Demo anından önceki 30 dakikada 46 Başkentgaz `INSTITUTION_TIMEOUT`; CAG-2051 ana kaydı ve ona bağlı 11 vaka; geçmişte çözülmüş 6 kurum zaman aşımı olayı ve çözümü (SOL-031); Mehmet'in işlemi canlıda 47. istek |
| **C** · ODMTFATR İSKİ | 1 Ekim'den beri 412 abone no doğrulama hatası (400'ü İSKİ, hepsi 13 hane; 187 farklı müşteri); 1 Ekim öncesi 13 haneli İSKİ numarası yok; 23 çağrı; İSKİ ve ASKİ duyuruları; bu konuda hiçbir geçmiş çözüm yok |
| **D** · Taksit hatırlatma | Son 90 günde 186 "gecikme / taksit tarihi" müşteri teması (71'i "hatırlatma almadım / tarihi unuttum"); 2.340 müşterilik hedef grup ve izin dağılımı (%58 e-posta, %81 SMS, %89 en az biri); 5 benzer talep; Kredi Takip Servisi 8 Kasım'a kadar dolu; `KRDRTKSR` katalogda |
| **E** · Afet erteleme | 3 il "etkilenen bölge" işaretli; orada 4.870 kredili müşteri, 6.215 kredi, 612 gecikmede; afet tarihinden sonra adresi değişen 37 müşteri; son 5 günde bu illerden 497 çağrı (418'i erteleme), önceki 30 günün günlük ortalaması 16; 3 benzer talep; D'nin talebi Kredi Takip takviminde planlı |
| **F** · Durum özeti | Bugünün logları; en sorunlu ekran ODMTFATR (B'nin artışı) |

## Üretim yöntemi (1. gün, VDI'de)

1. **Elle:** Ekran ve servis katalogları, hata–servis kuralları, servis takvimi, kurum duyuruları, demo kullanıcıları. Değerler üretim rehberinde birebir verili.
2. **Log üreticisi (rebuild Faz 5):** 10.000 kayıt, 30 gün, seed 42. Ardından senaryo enjeksiyonu (C'nin 412 kaydı vb.).
3. **Betikler (Python, seed 42):** Portföy, çağrılar ve talepler; senaryo sayıları kesin, gerisi dağılımla.
4. **Foundry modeli:** Çağrı notu, çözüm ve talep metinleri (doğal dil). Maliyeti Copilot bütçesine yazılmaz.
5. **Yükleme:** Azure SQL (tüm yapısal veri ve loglar), Azure AI Search (çözümler, talepler, duyurular).
6. **Demo öncesi sıfırlama:** `demo_reset.py`, B'nin "son 30 dakika" kayıtlarını demo saatine göre yeniden yazar, önceki provaların oluşturduğu kayıtları temizler.
7. **Doğrulama:** `validate_scenarios.py` senaryo rakamlarını sorgularla kontrol eder; `--eval` ile 30 vakalık değerlendirme setinde doğruluk özeti çıkarır.

**Dikkat:** Büyük veri setlerini Copilot'a ürettirmeyin; çıktı token'ı bütçeyi hızla tüketir. Copilot'tan yalnızca üreten betikleri yazmasını isteyin.
