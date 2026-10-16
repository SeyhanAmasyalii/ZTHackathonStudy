# Mercek — Takıma Anlatım Cümleleri

Açılışta dokümanları tek tek okumak yerine bu dokuz cümleyle ilerleyin. Her cümle bir dokümanın ana fikrini taşır; ayrıntı için yanındaki dokümana bakılır.

| # | Konu | Takıma anlatırken tek cümle | Doküman |
|---|---|---|---|
| 1 | Oyunun kuralları | Puanın üçte biri robotlardan gelir ve onu sabah altyapıyı düzgün kurarak kazanırız; üçte ikisi jüriden gelir ve onu somut önce/sonra rakamlarıyla kazanırız. | [Teknik kılavuz özeti](hackathon-teknik-kilavuz.md) |
| 2 | Ne yapıyoruz | Banka çalışanlarının ekranlarda yaşadığı sorunu loglardan, kurum duyurularından ve koddan açıklıyoruz, çağrıları birleştiriyoruz; iş birimlerinin taleplerini de servis bazlı adam-gün ve takvimle plana çeviriyoruz. | [Kapsam](mercek-kapsam.md) |
| 3 | Senaryolar | Altı senaryomuz var: Mercek A'da çağrıyı önlüyor, B'de mükerrer çağrıları birleştiriyor, C'de sorunu koda bağlıyor, D'de bir talebi gerekçelendirip kapsamını düzeltiyor; E ve F yedek. | [Demo senaryoları](mercek-demo-senaryo-onerileri.md) |
| 4 | Kim, ne, ne zaman | Görev atamıyoruz, sorumluluk seçiyoruz: herkes 19 maddeden 3–4 tanesini sahiplenir, kritik dört madde boş kalmaz, her iş PR ile ve başka birinin onayıyla main'e girer. | [İş planı §2–4](mercek-is-plani.md) |
| 5 | Temel uygulama | Bankacılık ekranları, giriş ve Joyride için tekerleği yeniden icat etmiyoruz: rebuild rehberini faz faz uygular, Mercek'i onun üstüne iki modül olarak ekleriz. | [Rebuild rehberi](COPILOT_REBUILD_GUIDE.md) |
| 6 | Nasıl yapacağız | Ne yapacağını rehberden okursun, Copilot'a ne yazacağını prompt dosyasından kopyalarsın; aynı görev kodu ikisini bağlar, önerilen ucuz modeli seçer ve her görev için yeni sohbet açarsın. | [Uygulama rehberi](mercek-uygulama-rehberi.md), [Copilot prompt'ları](mercek-copilot-promptlari.md) |
| 7 | Demo verisi | Rastgele veri değil, senaryoyu taşıyan veri üretiyoruz: demoda göreceğimiz her rakam veride var ama Mercek onu sorguyla kendisi hesaplıyor; demoyu bozacak kayıtlar bilerek yasak. | [Veri planı](mercek-sentetik-veri-plani.md), [Veri üretim rehberi](mercek-sentetik-veri-uretimi.md) |
| 8 | Jüriye nasıl anlatacağız | Altı senaryonun hepsi sunumda bir slaytta görünür; canlıda yalnızca 2. gün 12:00'de çalışır durumda olanları gösteririz, diğerleri ekran görüntüsü veya videoyla geçer. | [İş planı §5](mercek-is-plani.md), [Sunum taslağı](../presentation/Mercek_AI_Overflow_Sunum.pptx) |
| 9 | Bugünün kritik yolu | İlk üç saatte tek hedef her şeyin yeşil olması: repo, pipeline, iki App Service, model ve veri öğle yemeğinden önce ayakta olursa puanın kolay yarısı cepte. | [README](../README.md), [Uygulama rehberi A](mercek-uygulama-rehberi.md) |

## Akılda kalacak rakamlar

| Rakam | Anlamı |
|---|---|
| %30 / %70 | Otomatik değerlendirme / jüri |
| 20 $ | Takımın toplam Copilot harcaması için tam puan sınırı |
| 12:00 → 13:00 | 2. gün kod dondurma ve canlı demo kararı → teknik değerlendirme |
| 5 dk | Sunum süresi; canlı demo yaklaşık 3 dakika |
| A → B → D → C | Hazırlık önceliği (canlı demoya girme sırası) |
| 144.186 / 19.000 / ~334.000 | A: 3 ay taksit / gelirin yarısı / 36 ayda en yüksek tutar |
| 47 · CAG-2051 · 12 · %93 | B: son 30 dk istek · ana kayıt · bağlı vaka · eşleşme |
| 412 · %97 · 13 hane · %35 | C: hata · İSKİ payı · numara uzunluğu · eşleşme (eşik %75) |
| 18 → 20 a/g · %58 → %89 | D: tahmin · SMS ile erişim |
| 9 Kasım → 2 / 4 Aralık | D: başlangıç → bitiş (SMS ile) |
