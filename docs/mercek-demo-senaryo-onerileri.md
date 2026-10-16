# Mercek — Demo Senaryo Önerileri (taslak, onay bekliyor)

> Bu doküman **öneridir**. Senaryolar onaylandıktan sonra kapsam, iş planı, veri, uygulama rehberi, prompt'lar ve sunum bu seçime göre güncellenecek. Son bölümde onay gereken kararlar listeli.

---

## 1. Değişen çerçeve

| Önceki varsayım | Yeni çerçeve |
|---|---|
| Mercek'i son kullanıcı (müşteri) kullanıyor | Mercek'i **banka çalışanları ve teknoloji ekipleri** kullanıyor |
| Mobil banka simülasyonu (Giriş, Transfer, Fatura) | `COPILOT_REBUILD_GUIDE.md` Faz 2 ve Faz 4'teki **iç bankacılık uygulaması** ve 5 işlem ekranı |
| "Ayşe EFT yapamıyor" | **Şube personeli işlem ekranında takılıyor**, Mercek'e soruyor |

### Simüle edilen uygulama (rebuild rehberinden)

**Ana modüller (Faz 2):** Bankacılık · **Mercek** (sohbet arayüzü) · **Talep Yönlendirme** (ekip önerisi ve maliyet tahmini)

**İşlem ekranları (Faz 4):**

| Kod | Ekran | Senaryoda kullanılan iş kuralı |
|---|---|---|
| `KRTTBASV` | Kredi Kartı Başvurusu | Gold için gelir ≥ 20.000; onay limiti = min(talep, gelir × 3, kart tavanı) |
| `KRDTKULL` | Bireysel Kredi Kullandırım | Taksit gelirin %50'sini aşarsa uyarı, buton kapalı |
| `ODMTFATR` | Fatura Ödeme | Kurum entegrasyonu (Başkentgaz, İSKİ…), abone sorgu |
| `MUSTGUNC` | Müşteri Bilgi Güncelleme | İletişim izinleri (SMS, e-posta, telefon) |
| `HSPTVDSZ` | Vadesiz Hesap Açılışı | Döviz cinsi, şube, IBAN üretimi |

**Hazır olan ve bize zaman kazandıracaklar:**
- **Sahte kullanıcılar (Faz 3)** demonun karakterleri olabilir:
  - **Mehmet Yılmaz:** Faz 3'te Müşteri Temsilcisi; bu demoda **banka müşterisi** olarak kullanılır (işlem ekranları giriş yapan kullanıcının bilgileriyle dolduğu için doğal).
  - **Eyüp Dalan:** Platform Yöneticisi.
  - **Ayşe Kaya:** Kıdemli İş Analisti.
- **Sentetik log üretici (Faz 5):** Her log kaydında ekran kodu, müşteri, `trace.id` ve hata kodu var. İş reddi kodları: `INSUFFICIENT_INCOME`, `AFFORDABILITY_EXCEEDED`, `INSTITUTION_TIMEOUT` vb. Teknik hata kodları: `CORE_BANKING_TIMEOUT`, `SERVICE_UNAVAILABLE`, `DB_CONNECTION_ERROR`. Mercek'in okuyacağı log kaynağı hazır.
- **Joyride senaryoları (Faz 7):** `krd-gelir-orani`, `odm-dogalgaz`, `krt-gold-onay` gibi senaryolar hazır. Mercek'in "Bana göster" çözümleri bunların üzerine kurulabilir.
- **Talep Yönlendirme (Faz 2):** Ekip ve saatlik ücret tablosu (Altyapı 1.450 ₺, Yazılım Geliştirme 1.650 ₺, Veri & Analitik 1.800 ₺, Güvenlik 2.100 ₺, Destek 950 ₺), öncelik katsayısı ve `TLP-…` talepleri mevcut. Şu anki anahtar kelime tabanlı yönlendirmenin yerine Mercek'in AI tabanlı analizi gelecek.

### Kullanıcılar ve Mercek'e giriş noktaları

| Kullanıcı | Nerede çalışır | Mercek'e nasıl ulaşır |
|---|---|---|
| **Elif** (şube müşteri temsilcisi) | Bankacılık işlem ekranları | Ekran kodu çubuğundaki **"Sorun yaşıyorum"** butonu. Mercek paneli ekran kodu, müşteri no, son `trace.id` ve ekrandaki hata mesajıyla açılır. |
| **Mehmet** (banka müşterisi) | İnternet şubesi (ODMTFATR) | Mercek'i kullanmaz; sorun yaşayınca çağrı merkezini arar. |
| **Zeynep** (çağrı merkezi temsilcisi) | Mercek sohbet | Müşterinin anlattığını serbest metinle yazar; Mercek logları, ana kaydı ve müşteriye söylenecekleri getirir. |
| **Eyüp** (Platform Yöneticisi / L2 destek) | Mercek sayfası | Sohbet + çağrı listesi: zenginleştirilmiş kayıtlar, loglar, eşleşmeler, kod analizi |
| **Ayşe** (Kıdemli İş Analisti) | Talep Yönlendirme | Talep metni → sınıflandırma, etki, maliyet, takvim, köprü |

---

## 2. Önerilen senaryolar

### Senaryo A — "Hata mı, kural mı?" (KRDTKULL · iş kuralı reddi) ⭐ önerilen açılış

**Problem:** Şube personeli ekranda "işlem yapılamıyor" gördüğünde bunun sistem hatası mı yoksa iş kuralı reddi mi olduğunu çoğu zaman ayırt edemiyor ve çağrı açıyor. Oysa log üreticisinin dağılımına göre iş kuralı retleri teknik hatalardan çok daha sık.

**Akış**
1. Şube temsilcisi Elif, KRDTKULL'de müşteriye **400.000 TL, 3 ay** kredi kullandırmaya çalışıyor (gelir 38.000 TL). Uyarı çıkıyor, "Kullandır" butonu kapalı.
2. "Sorun yaşıyorum" butonuna basıyor. Mercek, Elif bir şey yazmadan ekran kodu ve `trace.id` üzerinden logu buluyor: `AFFORDABILITY_EXCEEDED`.
3. Mercek'in cevabı:
   > *"Bu bir sistem hatası değil, iş kuralı. Taksit 144.186 TL, müşterinin gelirinin %50'si olan 19.000 TL'yi aşıyor. En uzun vade olan 36 ayda bile taksit 22.754 TL. 36 ayda kullandırılabilecek en yüksek tutar yaklaşık 334.000 TL."*
4. Elif **"Bana göster"** diyor. Joyride turu tutarı 330.000 TL ve vadeyi 36 ay olarak dolduruyor. Taksit 18.772 TL, uyarı kalkıyor, ödeme planı görünüyor.
5. **Çağrı açılmıyor.** Mercek bunu "önlenen çağrı" olarak sayıyor (iş değeri ölçümü).

**Kanıtladığı:** M1.1 bağlam yakalama, M1.2 log inceleme, M1.5 görsel anlatım, ve **çağrı önleme**.
**Hesap kurallardan:** Taksit ve uygun tutarı `loanPlan` formülü hesaplıyor (kod). Mercek açıklıyor (AI).
**Mevcut altyapı:** `krd-gelir-orani` Joyride senaryosu ve `loanPlan` fonksiyonu hazır.

---

### Senaryo B — "Yaygın teknik sorun, bilinen çözüm" (ODMTFATR · kurum zaman aşımı · çağrı merkezi) ⭐

**Problem:** Bir kurum entegrasyonu yavaşladığında çok sayıda müşteri aynı anda çağrı merkezini arıyor. Her temsilci ayrı çağrı açıyor ve aynı sorun için onlarca kayıt oluşuyor. Temsilci müşteriye ne söyleyeceğini bilmiyor, L2 de kayıtlara tek tek bakıyor.

**Akış**
1. **Mehmet (banka müşterisi)**, internet şubesinde ODMTFATR ekranından doğalgaz faturası ödüyor (Başkentgaz, abone 4012345678). Sorgula → *"Kurumdan yanıt alınamadı."* Arka planda log yazılıyor: ekran `ODMTFATR`, `INSTITUTION_TIMEOUT`, Mehmet'in müşteri no'su, `trace.id`, kanal "İnternet Şube".
2. Mehmet **çağrı merkezini arıyor.**
3. **Çağrı merkezi temsilcisi Zeynep**, Mercek'e yazıyor:
   > *"Doğalgaz Başkentgaz, abone 4012345678, fatura ödemede sorun yaşıyor."*
4. Mercek serbest metinden ekran (`ODMTFATR`), kurum (Başkentgaz) ve abone no'yu çıkarıyor. Loglarda Mehmet'in 3 dakika önceki başarısız işlemini buluyor ve genel tabloyu görüyor:
   > *"Müşterinin ödemesi tamamlanmadı ve hesabından tahsilat yapılmadı. Neden müşteriyle ilgili değil: son 30 dakikada Başkentgaz'a giden 47 ödeme isteği tüm kanallarda `INSTITUTION_TIMEOUT` ile düştü. Konu Altyapı ekibinde.*
   > *Müşteriye söyleyebileceğiniz: 'Ödemeniz alınmadı, hesabınızdan para çekilmedi. Kurum kaynaklı geçici bir sorun var; sorun giderilince SMS ile bilgilendirileceksiniz. Son ödeme tarihine kadar gecikme faizi oluşmaz.'"*
5. **Mükerrer çağrı birleştirme:** Aynı dakikalarda başka müşteriler de aynı sorun için çağrı merkezini arıyor ve başka temsilciler de Mercek'e yazıyor. Mercek ilk vakada **ana çağrı kaydını** (CAG-2051) açmış. Her yeni vakayı yeni çağrı açmadan bu kayda bağlıyor: müşteri no, abone no, `trace.id`. Zeynep'in ekranında *"Ana kayıt CAG-2051'e bağlandı · bağlı vaka: 12"* görünüyor; sayaç demo sırasında artmaya devam ediyor.
6. **Eyüp (L2)**, Mercek sayfasında CAG-2051'i açıyor:
   - Zenginleştirilmiş kayıt: ekran, kurum, hata kodu, ilk görülme zamanı, etkilenen müşteri sayısı, kanal dağılımı, örnek `trace.id`'ler, bağlı 12 vaka.
   - Ekip ataması kuralla: kurum entegrasyonu hatası → Altyapı.
   - **%93 eşleşme:** geçmişte 6 benzer kurum zaman aşımı olayı ve kaynaklarıyla birlikte uyarlanmış çözüm (kurum zaman aşımı eşiği, istek kuyruklama, kurumla iletişim adımları).
   - Sorun kapanınca bağlı 12 müşteriye toplu bilgilendirme (opsiyonel, Could).

**Kanıtladığı:**
- M1.1 bağlam yakalama: burada ekran kodundan değil, temsilcinin serbest metninden.
- M1.2 log inceleme: müşterinin kendi işlemi ve genel tablo.
- M1.3 zenginleştirme ve ekip ataması.
- M1.4 geçmiş çözüm eşleştirme.
- Ek değerler: **mükerrer çağrı birleştirme** ve **temsilciye hazır müşteri açıklaması**.

**Mevcut altyapı:** Mehmet'in adımı `odm-dogalgaz` Joyride senaryosuyla otomatik oynatılabilir (demoda zaman kazandırır). Log üreticisinde `INSTITUTION_TIMEOUT` var. Demo modunda Başkentgaz ödemesi bilerek hata döner ve log yazar.
**Veride hazır olacaklar:** Son 30 dakikaya düşen yaklaşık 46 başarısız Başkentgaz isteği, CAG-2051 ana kaydı ve ona bağlı 11 vaka. Mehmet'in vakası canlıda 12. olarak eklenir.

---

### Senaryo C — "AI kodu okur" (KRTTBASV · sınır değer hatası) ⭐

**Problem:** Geçmişte örneği olmayan yeni bir hata. L2 kodu baştan incelemek zorunda kalıyor.

**Akış**
1. Başka bir şubeden çağrı geliyor: *"Geliri tam 20.000 TL olan müşteriye Gold kart verilemiyor, gelir yetersiz diyor."*
2. Eyüp çağrıyı açıyor. Geçmiş çözümlerle eşleşme **%38**, eşiğin (%75) altında. Mercek kod analizine geçiyor.
3. Mercek logları ve kodu birleştiriyor:
   > *"Son 30 günde geliri tam 20.000 TL olan 14 Gold başvurusu `INSUFFICIENT_INCOME` ile reddedilmiş. Ürün kuralı gelir ≥ 20.000 diyor, ama `KartBasvuruKarar` içinde koşul `gelir > 20000` yazılmış."*
   Satırı ve düzeltme önerisini (`>` → `>=`) diff olarak, test önerisiyle birlikte gösteriyor. Etiket: "Öneridir, uygulanmadı".

**Kanıtladığı:** M1.4 eşleşme yoksa kod analizi, logla kodu ilişkilendirme ve dürüst eşik (uydurma eşleşme yok).
**Neden bu hata:** Kural ekranda görünür (Gold kartında "gelir ≥ 20.000" yazıyor). Jüri çelişkiyi bir saniyede anlar.
**Önemli:** Hatalı kod **uygulamanın kendisinde değil**, `sample-codebase/` altındaki "kart karar servisi" kopyasında durur. Böylece hem uygulama doğru çalışır, hem kod kalitesi puanı zarar görmez. Loglara bu hatayı destekleyen 14 kayıt eklenir.

**Alternatif hata (seçenek):** HSPTVDSZ'de IBAN kontrol hanesi 10'dan küçük çıktığında başına sıfır eklenmiyor (`padStart(2,"0")` eksik), bu yüzden IBAN'ların yaklaşık %8'i diğer bankalarda geçersiz sayılıyor. Teknik olarak daha etkileyici, ama jürinin anlaması biraz daha uzun sürer.

---

### Senaryo D — "Talepten plana, sorundan kapsama" (Talep Yönlendirme · KRDTKULL) ⭐ önerilen kapanış

**Problem:** Yeni geliştirme talepleri, aynı ekranda yaşanan sorunlardan habersiz kapsamlanıyor ve tahminleniyor.

**Akış**
1. Ayşe, Talep Yönlendirme'ye yazıyor: *"Kredi kullandırım ekranından ödeme planını müşteriye e-posta ile gönderebilelim."*
2. Mercek'in çıktısı:
   - **Tip:** Mevcut ekran değişikliği, ekran KRDTKULL.
   - **Etki:** KRDTKULL ekranı, bildirim/e-posta servisi, müşteri iletişim izinleri (MUSTGUNC'deki e-posta izni kontrol edilmeli). Ana ekip: Yazılım Geliştirme.
   - **Tahmin:** 4 benzer geçmiş talep (96 / 112 / 120 / 144 saat) → **medyan 116 saat** → 116 × 1.650 ₺ × 1,15 (Orta öncelik) = **220.110 ₺**, ekip takvimine göre başlangıç ve bitiş tarihi.
3. **Köprü:**
   > *"Bu ekranda son 30 günde 312 `AFFORDABILITY_EXCEEDED` reddi var ve bunların 58'i çağrıya dönüşmüş. Mercek'in Senaryo A'da yaptığı 'uygun tutar/vade önerisi' ekrana kalıcı olarak eklensin mi?"*
   Ayşe "Evet" diyor → +24 saat, **265.650 ₺**, bitiş tarihi güncelleniyor.

**Kanıtladığı:** M2.1 sınıflandırma, M2.4 etki analizi, M2.5 maliyet ve takvim, M2.6 köprü.
**Hikâyenin kapanışı:** Demonun başında Elif'in şubede yaşadığı sorun, sonunda ürünün kalıcı bir iyileştirmesine dönüşüyor. Jüri döngünün kapandığını kendi gözüyle görüyor.
**Mevcut altyapı:** Maliyet formülü (saatlik ücret × saat × öncelik katsayısı) ve `TLP-…` talepleri Talep Yönlendirme modülünde zaten var.

---

### Senaryo E — Yeni ekran: "Kredi kartı limit artışı" (M2.3) · yedek

1. Ayşe: *"Müşteriler kart limit artışını şubeden talep edebilsin."* → **Yeni ekran.**
2. Mercek 4–5 soru soruyor: hangi kart tipleri, gelir belgesi gerekli mi, onay yetkisi, SMS bildirimi, rapor ihtiyacı.
3. Çıktılar:
   - **Ekran kodu önerisi:** `KRTTLMAR`. Kural `[A-Z]{3}[TR][A-Z0-9]{4}` ile doğrulanmış, mevcut kodlarla çakışmıyor.
   - **Alanlar:** KRTTBASV'deki standartlardan (gelir, limit, kesim günü) ve aynı karar kuralından (limit ≤ gelir × 3, kart tavanı).
   - **Joyride için önerilen `data-tour` hedefleri.**

**Kanıtladığı:** Mercek kurumun kendi standartlarını (ekran kodu kuralı, alan kuralları) biliyor ve yeni talebi bunlara uygun kapsamlıyor.

---

### Senaryo F — Yönetici özeti (Mercek sohbet) · yedek

Eyüp Mercek'e soruyor: *"Bugün en çok sorun yaşanan ekran hangisi?"* Loglardan cevap: ODMTFATR, Başkentgaz zaman aşımı artışı, etkilenen şube ve işlem sayısı, açık ana kayıt. Kibana'ya girmeden sohbetle durum özeti alınıyor.

---

## 3. Önerilen demo kurgusu (≈ 2,5 dakika)

| Sahne | Senaryo | Kim | Süre | Jüri kriteri |
|---|---|---|---|---|
| 1 | **A** — Hata mı, kural mı? (KRDTKULL) | Elif | ~45 sn | Probleme uygunluk, Kullanıcı deneyimi, İş değeri (çağrı önleme) |
| 2a | **B** — Yaygın sorun, bilinen çözüm (ODMTFATR) | Mehmet (müşteri) → Zeynep (çağrı merkezi) → Eyüp | ~50 sn | Ürün çalışırlığı, İş değeri (mükerrer çağrı) |
| 2b | **C** — AI kodu okur (KRTTBASV) | Eyüp | ~30 sn | Yenilikçilik |
| 3 | **D** — Talepten plana + köprü (KRDTKULL) | Ayşe | ~45 sn | İş değeri, Yenilikçilik |
| Yedek | E, F | — | video / S-C | — |

**Hikâye ipi:** KRDTKULL'deki sorun Sahne 1'de açılır, Sahne 3'te ürün iyileştirmesine dönüşür. Ekran kodları her sahnede görünür ve Mercek'in "ekran bağlamını" bildiğini sürekli hatırlatır.

**Problem slaytı da buna göre değişir:** *"Şube personeli işlem yapamadığında hata mı kural mı bilemiyor, çağrı açıyor. L1 ve L2 Kibana'da log arıyor, aynı sorun için onlarca çağrı açılıyor, bilinen çözümler kişilerde kalıyor. Yeni talepler bu sorunlardan habersiz planlanıyor."*

### İş değeri anlatımı (rakamlar veride sabitlenecek)

| Ölçü | Bugün | Mercek ile |
|---|---|---|
| İş kuralı reddi | Çağrı açılır, L1 kuralı açıklar | Ekranda anında açıklanır, uygun alternatif önerilir: **çağrı hiç açılmaz** |
| Yaygın teknik sorun | Her şubeden ayrı çağrı | Tek ana kayıt, şubelere anında bilgi |
| Bilinen sorun | L2 log arar, çözüm kişide | %93 eşleşme, kaynaklı çözüm, saniyeler |
| Yeni hata | Kod baştan incelenir | Log + kod ilişkilendirilip satır düzeyinde öneri |
| Talep tahmini | Anahtar kelimeyle ekip, elle saat | Benzer taleplerden saat, maliyet, takvim; ekranın sorun geçmişi kapsamda |

---

## 4. Seçim yapılırsa diğer dokümanlara etkisi (onay sonrası yapılacak)

| Doküman | Değişecek |
|---|---|
| Kapsam | Hedef kullanıcı: banka çalışanı ve teknoloji ekipleri. M1.1 girişi: ekran kodu çubuğundaki "Sorun yaşıyorum". Yeni değer: çağrı önleme ve mükerrer çağrı birleştirme. |
| İş planı | Demo senaryosu (§5), karakterler (Elif, Mehmet, Zeynep, Eyüp, Ayşe), kabul kriterleri |
| Veri planı ve üretim rehberi | Log kaynağı olarak **Faz 5 üreticisi** (kendi log üreticimize gerek kalmıyor). Senaryo kayıtları: Başkentgaz artışı, 14 Gold reddi, 312 AFFORDABILITY reddi, 58 çağrı, 4 benzer talep (saat bazlı). Ekipler ve ücretler mock-data'dan. Adam-gün yerine saat. |
| Uygulama rehberi ve prompt'lar | **Teknoloji:** Next.js 16 + FastAPI (uv) → React/Vite varsayımı güncellenir. Ekran kimlikleri → ekran kodları ve `data-tour` hedefleri. Mercek sohbet API'si (`/api/mercek/chat`). Joyride v3 hazır olduğu için M1.5 küçülür. **Dağıtım:** Next.js + FastAPI'nin App Service'e nasıl taşınacağına karar verilmeli. |
| Sunum ve taslak ekranlar | Problem slaytı, demo slaytı, mockup'lar (iç uygulama ekranlarıyla yeniden) |
| Takım anlatım cümleleri | 2. ve 3. cümle |

---

## 5. Onay gereken kararlar

1. **Senaryo seti:** Önerim A + B + C + D canlı, E ve F yedek. Değişiklik var mı?
2. **Sahne 2b'deki hata:** KRTTBASV sınır değer hatası (önerim, anlaşılması kolay) mı, HSPTVDSZ IBAN kontrol hanesi hatası mı?
3. **Mercek'in incelediği kod:** `sample-codebase/` altındaki kopya (önerim, uygulama doğru kalır) mı, uygulamanın kendi kodu mu?
4. **Mercek'e giriş:** Ekran kodu çubuğunda "Sorun yaşıyorum" butonu ile bağlamlı yan panel + ayrı Mercek sohbet sayfası (önerim) mi, yalnızca sohbet sayfası mı?
5. **Maliyet modeli:** Mevcut Talep Yönlendirme formülü olan saat × saatlik ücret × öncelik katsayısı (önerim) mı, adam-gün mü?
6. **Demo kullanıcıları:** Faz 3'teki Mehmet (müşteri), Eyüp (L2) ve Ayşe (analist) kullanılır; sahte kullanıcı listesine iki kişi eklenir: **Elif** (şube müşteri temsilcisi, Senaryo A) ve **Zeynep** (çağrı merkezi temsilcisi, Senaryo B). Uygun mu?
