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

**Ana modüller (Faz 2):** Bankacılık · **Mercek** (sohbet arayüzü) · **Talep Yönlendirme** (talep analizi ve efor tahmini)

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
  - **Ayşe Kaya:** Kıdemli İş Analisti (teknoloji tarafı; iş biriminden gelen talepleri analiz eder).
- **Sentetik log üretici (Faz 5):** Her log kaydında ekran kodu, müşteri, `trace.id` ve hata kodu var. İş reddi kodları: `INSUFFICIENT_INCOME`, `AFFORDABILITY_EXCEEDED`, `INSTITUTION_TIMEOUT` vb. Teknik hata kodları: `CORE_BANKING_TIMEOUT`, `SERVICE_UNAVAILABLE`, `DB_CONNECTION_ERROR`. Mercek'in okuyacağı log kaynağı hazır.
- **Joyride senaryoları (Faz 7):** `krd-gelir-orani`, `odm-dogalgaz`, `krt-gold-onay` gibi senaryolar hazır. Mercek'in "Bana göster" çözümleri bunların üzerine kurulabilir.
- **Talep Yönlendirme (Faz 2):** Talep listesi ve `TLP-…` talepleri mevcut. Şu anki anahtar kelimeyle ekip önerme ve ücret hesabı yerine Mercek'in **servis bazlı etki analizi ve adam-gün tahmini** gelecek. Teknoloji tarafında ekip yerine **servis** dili kullanılır: Kredi Kullandırım Servisi, Kredi Takip Servisi, Müşteri Yönetim Servisi vb.

### Kullanıcılar ve Mercek'e giriş noktaları

| Kullanıcı | Nerede çalışır | Mercek'e nasıl ulaşır |
|---|---|---|
| **Elif** (şube müşteri temsilcisi) | Bankacılık işlem ekranları | Ekran kodu çubuğundaki **"Sorun yaşıyorum"** butonu. Mercek paneli ekran kodu, müşteri no, son `trace.id` ve ekrandaki hata mesajıyla açılır. |
| **Mehmet** (banka müşterisi) | İnternet şubesi (ODMTFATR) | Mercek'i kullanmaz; sorun yaşayınca çağrı merkezini arar. |
| **Zeynep** (çağrı merkezi temsilcisi) | Mercek sohbet | Müşterinin anlattığını serbest metinle yazar; Mercek logları, ana kaydı ve müşteriye söylenecekleri getirir. |
| **Eyüp** (Platform Yöneticisi / L2 destek) | Mercek sayfası | Sohbet + çağrı listesi: zenginleştirilmiş kayıtlar, loglar, eşleşmeler, kod analizi |
| **Fatma** (Kredi Tahsilatları Bölüm Başkanlığı, iş birimi) | Talep Yönlendirme | İhtiyacını kendi cümleleriyle yazar; Mercek'in analizini görür, kapsam önerisini onaylar. |
| **Ayşe** (Kıdemli İş Analisti, teknoloji) | Talep Yönlendirme | Mercek'in analizini gözden geçirir, açık soruları iş birimiyle netleştirir, köprü önerisini iş birimine sunar. |

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
   > *"Müşterinin ödemesi tamamlanmadı ve hesabından tahsilat yapılmadı. Neden müşteriyle ilgili değil: son 30 dakikada Başkentgaz'a giden 47 ödeme isteği tüm kanallarda `INSTITUTION_TIMEOUT` ile düştü. Konu Fatura Ödeme Servisi'nin kurum entegrasyonunda.*
   > *Müşteriye söyleyebileceğiniz: 'Ödemeniz alınmadı, hesabınızdan para çekilmedi. Kurum kaynaklı geçici bir sorun var; sorun giderilince SMS ile bilgilendirileceksiniz. Son ödeme tarihine kadar gecikme faizi oluşmaz.'"*
5. **Mükerrer çağrı birleştirme:** Aynı dakikalarda başka müşteriler de aynı sorun için çağrı merkezini arıyor ve başka temsilciler de Mercek'e yazıyor. Mercek ilk vakada **ana çağrı kaydını** (CAG-2051) açmış. Her yeni vakayı yeni çağrı açmadan bu kayda bağlıyor: müşteri no, abone no, `trace.id`. Zeynep'in ekranında *"Ana kayıt CAG-2051'e bağlandı · bağlı vaka: 12"* görünüyor; sayaç demo sırasında artmaya devam ediyor.
6. **Eyüp (L2)**, Mercek sayfasında CAG-2051'i açıyor:
   - Zenginleştirilmiş kayıt: ekran, kurum, hata kodu, ilk görülme zamanı, etkilenen müşteri sayısı, kanal dağılımı, örnek `trace.id`'ler, bağlı 12 vaka.
   - Servis ataması kuralla: `INSTITUTION_TIMEOUT` + ODMTFATR → Fatura Ödeme Servisi (kurum entegrasyonu).
   - **%93 eşleşme:** geçmişte 6 benzer kurum zaman aşımı olayı ve kaynaklarıyla birlikte uyarlanmış çözüm (kurum zaman aşımı eşiği, istek kuyruklama, kurumla iletişim adımları).
   - Sorun kapanınca bağlı 12 müşteriye toplu bilgilendirme (opsiyonel, Could).

**Kanıtladığı:**
- M1.1 bağlam yakalama: burada ekran kodundan değil, temsilcinin serbest metninden.
- M1.2 log inceleme: müşterinin kendi işlemi ve genel tablo.
- M1.3 zenginleştirme ve servis ataması.
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

**Senaryo tek cümleyle:** Bankanın bir iş birimi yeni bir özellik istiyor. Mercek talebi hangi ekranı ve hangi servisleri etkilediğine göre çözümlüyor, benzer geçmiş taleplerden adam-gün tahmini ve takvim çıkarıyor. Sonra aynı ekranın sorun geçmişine bakıp *"bu ekranda zaten şöyle bir sorun var, bunu da çözelim mi?"* diye kapsamı büyütmeyi öneriyor.

**Problem:** Bugün yeni geliştirme talepleri, aynı ekranda yaşanan sorunlardan habersiz kapsamlanıyor ve tahminleniyor. Talep sahibi neyin etkileneceğini bilmiyor, tahmin toplantılarda elle yapılıyor. Ekranın çağrı geçmişi kapsam konuşmasına hiç girmiyor.

**Akış**

**1. Talep girişi.** **Fatma (Kredi Tahsilatları Bölüm Başkanlığı)** Talep Yönlendirme ekranına kendi cümleleriyle yazıyor:
> *"Müşteriler ödeme planlarını tam bilmedikleri için ilk taksitlerde gecikmeler yaşıyoruz. Kredi kullandırıldığında ödeme planı müşteriye e-posta ile gönderilebilsin."*

Talep, teknoloji tarafında analizi yürüten **Ayşe (Kıdemli İş Analisti)**'nin listesine düşüyor. Mercek'in analizi hem Fatma'nın hem Ayşe'nin ekranında görünüyor.

**2. Mercek'in talep analizi** (ekranda kartlar halinde):

**a) Talep özeti** (Mercek talebi netleştirerek yeniden yazıyor)
> KRDTKULL'de kredi kullandırımı tamamlandığında, ödeme planının müşterinin kayıtlı e-posta adresine gönderilmesi. Gönderim yalnızca müşterinin e-posta iletişim izni varsa yapılır.

**b) Sınıflandırma**

| Alan | Değer |
|---|---|
| Talep tipi | Mevcut ekran değişikliği |
| Ekran | `KRDTKULL` · Bireysel Kredi Kullandırım |
| Güven | %92 |
| Gerekçe | Talepte "kredi kullandırım ekranı" ve "ödeme planı" geçiyor; KRDTKULL zaten ödeme planı üretiyor, ama ekran dışına aktarmıyor. |

**c) Mevcut akış ve önerilen değişiklik** (ekranın akış tanımından)

| # | Mevcut adım | Değişiklik |
|---|---|---|
| 1 | Tutar ve vade seçimi | — |
| 2 | Özet ve ödeme planı tablosu | — |
| 3 | Sözleşme onayı | — |
| 4 | Kullandır | — |
| 5 | Sonuç (referans, hesaba geçen tutar, ilk taksit tarihi) | **Yeni:** "Ödeme planını e-posta ile gönder" seçeneği ve gönderilecek adres. Müşterinin e-posta izni yoksa seçenek pasif olur ve "İzin için MUSTGUNC" yönlendirmesi gösterilir. |

**d) Etkilenen servisler**

| Servis | Rol | Neden etkileniyor |
|---|---|---|
| **Kredi Kullandırım Servisi** | Ana servis | Ödeme planı dokümanının (PDF) üretilmesi, gönderim talebinin oluşturulması, sonuç ekranındaki yeni seçenek |
| **Müşteri Yönetim Servisi** | Etkileşimli servis | Müşterinin kayıtlı e-posta adresi ve e-posta iletişim izni bu servisten okunuyor (MUSTGUNC'de güncellenen alanlar). Okuma yapılacak; servisin kendisinde değişiklik beklenmiyor. |

**e) Açık sorular** (Mercek'in netleşmesini istediği noktalar)
- Ödeme planı PDF'i şifreli mi gönderilmeli? Şifreliyse şifre müşteriye hangi kanalla iletilecek?
- Plan, kullandırım sonrası değişirse (erken kapama, yapılandırma) yeniden gönderilecek mi?
- E-posta gönderimini hangi altyapı yapacak? Mevcut bir gönderim servisi var mı?

**f) Efor tahmini (adam-gün)**

Dayandığı benzer geçmiş talepler:

| Talep | Başlık | Efor | Benzerlik |
|---|---|---|---|
| TLP-0871 | Kredi kartı ekstresini e-posta ile gönderme | 12 a/g | %88 |
| TLP-0915 | Vadesiz hesap sözleşmesini e-posta ile iletme (HSPTVDSZ) | 10 a/g | %84 |
| TLP-0962 | KRDTKULL ödeme planını PDF olarak indirme | 14 a/g | %81 |
| TLP-1004 | Fatura dekontunu e-posta ile gönderme (ODMTFATR) | 17 a/g | %77 |

**Tahmin: 13 a/g** (medyan; aralık 10–17 a/g)

| Servis | Pay |
|---|---|
| Kredi Kullandırım Servisi | 10 a/g |
| Müşteri Yönetim Servisi (entegrasyon ve izin kontrolü) | 3 a/g |

**g) Takvim**
- Kredi Kullandırım Servisi **8 Kasım'a kadar dolu** (yıl sonu regülasyon işi). Müşteri Yönetim Servisi müsait.
- **Plan: 9 Kasım → 25 Kasım.** Müşteri Yönetim Servisi işi ilk hafta paralel yürür.

**h) Gerekçe** (Mercek'in açıklaması)
> *"Tahmin, 4 benzer 'doküman gönderimi' talebinin gerçekleşen eforlarına dayanıyor. En yakın örnek TLP-0962; o talepte PDF üretimi zaten yapılmıştı, bu talepte e-posta gönderimi ve izin kontrolü ekleniyor. Hesap kurallarla yapıldı; ben yalnızca açıklıyorum."*

**3. Köprü: ekranın sorun geçmişi** (Mercek kendiliğinden ekliyor)

> **KRDTKULL · son 30 gün**
> - 1.184 kullandırım denemesi, bunların **312'si `AFFORDABILITY_EXCEEDED`** (taksit gelirin %50'sini aşıyor) ile reddedilmiş.
> - Bu retlerin **58'i çağrıya dönüşmüş.** Bu ekrandaki en sık çağrı nedeni bu.
> - Bu çağrılarda temsilciler uygun tutarı ve vadeyi elle hesaplamış; ortalama çözüm süresi 25 dakika.
>
> **Öneri:** Taksit gelir sınırını aştığında ekranın kendisi uygun tutarı ve vadeyi önersin. Bu, Senaryo A'da Mercek'in Elif için yaptığı hesap; ekrana kalıcı olarak ekleniyor.
> - Etkilenen servis: Kredi Kullandırım Servisi. Ödeme planı formülü zaten var, ters hesap eklenecek.
> - Ek efor: **+3 a/g**
> - Beklenen etki: ayda ~58 çağrı ve ~24 saat destek eforu.
>
> *Kapsama eklensin mi?*

Ayşe öneriyi Fatma'ya iletiyor. Uygun tutar önerisi tahsilat tarafının da işine yarıyor, çünkü taksit gücünü aşan kredi kullandırılmadığı sürece gecikme riski azalıyor. Fatma **"Evet"** diyor ve tahmin kartı güncelleniyor:
- **13 → 16 a/g** (Kredi Kullandırım 13, Müşteri Yönetim 3)
- **Bitiş: 25 Kasım → 30 Kasım**
- Talep kaydında "çağrı geçmişinden eklenen kapsam" olarak işaretleniyor; onaylayan: Fatma, analiz: Ayşe.

**Kanıtladığı:** M2.1 sınıflandırma, M2.2 akış önerisi, M2.4 servis bazlı etki analizi, M2.5 adam-gün tahmini ve takvim, M2.6 köprü.
**Hikâyenin kapanışı:** Demonun başında Elif'in şubede yaşadığı sorun, sonunda ürünün kalıcı bir iyileştirmesine dönüşüyor. Jüri döngünün kapandığını kendi gözüyle görüyor.
**Hesap ile AI ayrımı:**
- **Kod:** Medyan efor, servis payları, takvim ve köprüdeki sayılar.
- **AI:** Talep özeti, sınıflandırma gerekçesi, akış değişikliği, açık sorular ve açıklama metinleri.

---

### Senaryo E — Yeni ekran: "Kredi kartı limit artışı" (M2.3) · yedek

1. Kartlar iş biriminden bir talep: *"Müşteriler kart limit artışını şubeden talep edebilsin."* → **Yeni ekran.**
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
| 3 | **D** — Talepten plana + köprü (KRDTKULL) | Fatma (iş birimi) → Ayşe (analist) | ~45 sn | İş değeri, Yenilikçilik |
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
| Talep tahmini | Toplantıda elle; etkilenen servisler sonradan ortaya çıkıyor | Servis bazlı etki, benzer taleplerden adam-gün ve takvim; ekranın sorun geçmişi kapsamda |

---

## 4. Seçim yapılırsa diğer dokümanlara etkisi (onay sonrası yapılacak)

| Doküman | Değişecek |
|---|---|
| Kapsam | Hedef kullanıcı: banka çalışanı ve teknoloji ekipleri. M1.1 girişi: ekran kodu çubuğundaki "Sorun yaşıyorum". Yeni değer: çağrı önleme ve mükerrer çağrı birleştirme. |
| İş planı | Demo senaryosu (§5), karakterler (Elif, Mehmet, Zeynep, Eyüp, Fatma, Ayşe), kabul kriterleri |
| Veri planı ve üretim rehberi | Log kaynağı olarak **Faz 5 üreticisi** (kendi log üreticimize gerek kalmıyor). Senaryo kayıtları: Başkentgaz artışı, 14 Gold reddi, 312 AFFORDABILITY reddi, 58 çağrı, 4 benzer talep (adam-gün). Servis kataloğu (Kredi Kullandırım, Müşteri Yönetim, Fatura Ödeme, Kart Başvuru…) ve servis takvimleri; ücret/maliyet yok. |
| Uygulama rehberi ve prompt'lar | **Teknoloji:** Next.js 16 + FastAPI (uv) → React/Vite varsayımı güncellenir. Ekran kimlikleri → ekran kodları ve `data-tour` hedefleri. Mercek sohbet API'si (`/api/mercek/chat`). Joyride v3 hazır olduğu için M1.5 küçülür. **Dağıtım:** Next.js + FastAPI'nin App Service'e nasıl taşınacağına karar verilmeli. |
| Sunum ve taslak ekranlar | Problem slaytı, demo slaytı, mockup'lar (iç uygulama ekranlarıyla yeniden) |
| Takım anlatım cümleleri | 2. ve 3. cümle |

---

## 5. Onay gereken kararlar

1. **Senaryo seti:** Önerim A + B + C + D canlı, E ve F yedek. Değişiklik var mı?
2. **Sahne 2b'deki hata:** KRTTBASV sınır değer hatası (önerim, anlaşılması kolay) mı, HSPTVDSZ IBAN kontrol hanesi hatası mı?
3. **Mercek'in incelediği kod:** `sample-codebase/` altındaki kopya (önerim, uygulama doğru kalır) mı, uygulamanın kendi kodu mu?
4. **Mercek'e giriş:** Ekran kodu çubuğunda "Sorun yaşıyorum" butonu ile bağlamlı yan panel + ayrı Mercek sohbet sayfası (önerim) mi, yalnızca sohbet sayfası mı?
5. ~~Maliyet modeli~~ **Karar verildi:** Ücret hesaplanmaz; tahmin yalnızca **adam-gün** ve takvim. Teknoloji tarafı **servis** bazlı anlatılır (ana servis / etkileşimli servis).
6. **Demo kullanıcıları:** Faz 3'teki Mehmet (müşteri), Eyüp (L2) ve Ayşe (analist) kullanılır; sahte kullanıcı listesine üç kişi eklenir: **Elif** (şube müşteri temsilcisi, Senaryo A), **Zeynep** (çağrı merkezi temsilcisi, Senaryo B) ve **Fatma** (Kredi Tahsilatları Bölüm Başkanlığı, Senaryo D). Uygun mu?
