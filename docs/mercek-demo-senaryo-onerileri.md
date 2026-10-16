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

### Senaryolar bir bakışta

| Senaryo | Problem | Mercek'in katkısı | Sonuç |
|---|---|---|---|
| **A** · KRDTKULL | Temsilci hata mı kural mı bilemiyor | Logdan iş kuralını açıklıyor, uygun tutarı hesaplayıp ekranı dolduruyor | Çağrı hiç açılmıyor |
| **B** · ODMTFATR | Kurum sorunu; her müşteri ayrı çağrı | Müşteriye hazır açıklama, ana kayda bağlama, %93 eşleşen çözüm | Onlarca çağrı tek kayıtta |
| **C** · ODMTFATR | Kurum numara formatını değiştirdi, ekran eskide kaldı | Log örüntüsü + kurum duyurusu + kod; düzeltme ve kalıcı öneri | 187 müşteri bulundu, sonraki olay önlendi |
| **D** · Talep Yönlendirme | İş birimi taksit hatırlatması istiyor (otomatik + ekrandan manuel); servis, efor ve erişim geç fark ediliyor | Bileşen ve servis analizi, a/g tahmini, çağrı ve izin verisiyle kapsam düzeltme | Gerekçeli plan: 20 a/g |
| E · yedek | Hesap kapama için yeni ekran isteniyor; kapamada bağlı ürünler gözden kaçıyor | Kurala uygun ekran kodu, mevcut bileşenlerden taslak; çağrı geçmişinden bağlı ürün kontrolü | Bağımlılıkları baştan görülmüş plan: 16 a/g |
| F · yedek | Durum görmek Kibana bilgisi istiyor | Sohbetle günlük özet | Herkes için durum görünürlüğü |

### Senaryo A — "Hata mı, kural mı?" (KRDTKULL · iş kuralı reddi) ⭐ önerilen açılış

> **Yönetici özeti**
> - **Problem:** Şube temsilcisi müşteriye kredi kullandıramıyor. Ekrandaki uyarının sistem hatası mı yoksa iş kuralı mı olduğunu ayırt edemiyor ve çağrı açmaya yöneliyor.
> - **Kim:** Elif (şube müşteri temsilcisi)
> - **Mercek nasıl yönlendirdi:** Ekran kodu ve son işlem üzerinden logu buldu. Durumun hata değil iş kuralı olduğunu açıkladı (taksit gelirin %50'sini aşıyor). Kullandırılabilecek en yüksek tutarı hesapladı (36 ay, ~334.000 TL) ve "Bana göster" ile ekranı doğru değerlerle doldurdu.
> - **Sonuç:** İşlem şubede tamamlandı, **çağrı hiç açılmadı.**

**Ayrıntılar**

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

> **Yönetici özeti**
> - **Problem:** Bir kurumun (Başkentgaz) entegrasyonu yavaşladı, müşteriler fatura ödeyemiyor ve çağrı merkezini arıyor. Her aramada ayrı çağrı açılıyor, temsilci müşteriye ne söyleyeceğini bilmiyor.
> - **Kim:** Mehmet (müşteri) → Zeynep (çağrı merkezi) → Eyüp (L2)
> - **Mercek nasıl yönlendirdi:**
>   - Temsilcinin serbest metninden ekranı, kurumu ve abone no'yu çıkardı; loglarda müşterinin başarısız işlemini ve yaygın kurum sorununu buldu.
>   - Temsilciye müşteriye söylenecek hazır açıklamayı verdi.
>   - Yeni çağrı açmak yerine vakayı mevcut ana kayda bağladı.
>   - L2'ye %93 eşleşen geçmiş çözümü getirdi.
> - **Sonuç:** Müşteri doğru bilgilendirildi, onlarca arama **tek kayıtta toplandı**, L2 bilinen çözümü dakikalar içinde uyguladı.

**Ayrıntılar**

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

### Senaryo C — "Dış dünya değişti, ekran değişmedi" (ODMTFATR · İSKİ abone numarası formatı) ⭐

> **Yönetici özeti**
> - **Problem:** İSKİ yeni abonelere 13 haneli numara vermeye başladı, ama ekranımız 6–12 hane kabul ediyor. Müşteriler su faturasını ödeyemiyor ve kimse nedenini bilmiyor.
> - **Kim:** Elif (şube) → Eyüp (L2)
> - **Mercek nasıl yönlendirdi:**
>   - Log örüntüsünü buldu: hatalar yalnızca İSKİ'de, yalnızca 13 haneli numaralarda ve 1 Ekim'den beri görülüyor.
>   - Kurum duyuruları arşivinde İSKİ'nin geçiş duyurusunu buldu.
>   - Kuralın kodda iki yerde sabit yazıldığını gösterdi; düzeltmeyi ve kalıcı öneriyi (kurum bazlı parametre) sundu.
>   - ASKİ'nin Ocak'taki benzer geçişini önceden haber verdi.
> - **Sonuç:** Kök neden dakikalar içinde bulundu, **187 etkilenen müşteri** belirlendi, bir sonraki benzer olay önlendi.

**Ayrıntılar**

**Olay sırası (basitçe):**
1. İSKİ, 12 Eylül'de kurumlara bir duyuru gönderiyor: *"1 Ekim 2026 itibarıyla yeni abonelere 13 haneli abone numarası verilecektir."*
2. Duyuru ilgili birimde kalıyor ve ekrandaki kurala yansımıyor. ODMTFATR abone numarası olarak hâlâ yalnızca **6–12 hane** kabul ediyor (`^\d{6,12}$`).
3. 1 Ekim'den sonra İSKİ'ye yeni abone olan müşteriler (örneğin yeni taşınanlar) su faturasını ödemeye çalışıyor. Ekran *"Abone numarası 6–12 haneli olmalıdır"* deyip işlemi yapmıyor. Müşteri numarayı faturasından doğru okumuş; hata bizim kuralımızda.

Kimse hata yapmamış: kural yazıldığı gün doğruydu, sonra dış dünya değişti.

**Akış**

**1. Çağrı.** Bir müşteri şubeye geliyor. **Elif (şube temsilcisi)** Mercek'e yazıyor:
> *"Müşteri İSKİ su faturasını ödeyemiyor. Abone numarası 13 haneli, faturada da öyle yazıyor, ama ekran 6–12 hane olmalı diyor."*

**2. Mercek'in ilk analizi (Elif'e):**
> *"Sorun müşterinin numarasında değil. 1 Ekim'den beri ODMTFATR'de abone numarası doğrulama hatası **412 kez** görülmüş. Bunların **%97'si İSKİ'de** ve **hepsi 13 haneli** numaralar. 1 Ekim'den önce İSKİ'de 13 haneli numara hiç yok. Kurum duyuruları arşivinde İSKİ'nin 12 Eylül tarihli 13 hane geçiş duyurusu var. Yani İSKİ yeni abonelere 13 haneli numara vermeye başlamış, ekranımız henüz kabul etmiyor. Çağrı açıldı; şimdilik müşteri faturasını İSKİ'nin kendi kanallarından ödeyebilir."*

Mercek çağrıyı **Fatura Ödeme Servisi**'ne atıyor (kural: ODMTFATR + kurum doğrulaması).

**3. Eyüp (L2) çağrıyı açıyor.** Geçmiş çözümlerle eşleşme **%35**, eşiğin (%75) altında; bu yeni bir sorun. Mercek koda geçiyor.

**4. Kod analizi:** Mercek abone numarası kuralının **iki yerde** tanımlı olduğunu buluyor: ekranda (ODMTFATR formu) ve Fatura Ödeme Servisi'nde. İkisi de aynı sabit kuralı kullanıyor:

```diff
- const ABONE_NO_PATTERN = /^\d{6,12}$/;
+ const ABONE_NO_PATTERN = /^\d{6,13}$/;
```

> *"Kök neden: Abone numarası uzunluğu kodda sabit yazılmış ve İSKİ'nin 1 Ekim'deki format değişikliğine güncellenmemiş.*
> *Kısa vadeli düzeltme: Üst sınırı iki yerde de 13'e çıkar.*
> *Kalıcı öneri: Abone numarası uzunluğu kurum bazında parametre olsun (kurum tablosunda en az/en çok hane). Bir sonraki format değişikliği kod değişikliği gerektirmesin.*
> *Test önerisi: İSKİ 13 hane geçer, 14 hane reddedilir; diğer kurumların kuralları değişmez.*
> *Etki: 1 Ekim'den beri 187 farklı müşteri 412 kez denemiş, 23 çağrı açılmış. Bu müşterilerin faturaları son ödeme tarihine yaklaşıyor."*

Etiket: **"Öneridir, uygulanmadı."**

**5. Proaktif ek bulgu:**
> *"Kurum duyuruları arşivinde ASKİ'nin de Ocak 2027'de 13 haneli numaraya geçeceğine dair bir duyuru var. Kalıcı öneri uygulanırsa o geçiş sorunsuz olur; uygulanmazsa aynı olay Ocak'ta ASKİ için tekrarlanır."*

**Kanıtladığı:**
- **M1.2 log örüntüsü:** Hata yalnızca bir kurumda, yalnızca bir numara uzunluğunda ve belli bir tarihten sonra görülüyor.
- **M1.4 eşleşme yoksa analiz:** Kurum duyurularında arama ve kod analizi birlikte. Uydurma eşleşme yok.
- **Üç kaynağı ilişkilendirme:** Log (ne oluyor), kurum duyurusu (neden oluyor), kod (nerede düzeltilir).
- **Proaktiflik:** Henüz yaşanmamış bir sorunu (ASKİ, Ocak) önceden haber veriyor.

**Jüriye tek cümleyle:** *"Kurum numarayı uzattı, bizim ekran hâlâ eski uzunluğu bekliyor; Mercek bunu loglardan, kurumun duyurusundan ve koddan birlikte çıkarıyor."*

**Uygulama notları:**
- Bu sefer kasıtlı bir hata gömülmüyor. Rebuild rehberinde ODMTFATR abone numarası kuralı zaten **6–12 hane** olarak tanımlı. Mercek **uygulamanın kendi kodunu** okuyabilir; `sample-codebase/` kopyasına gerek yok.
- Demo modunda ekrandaki doğrulama hatası backend'e log olarak yazılır (gerçekte Fatura Ödeme Servisi'nin `VALIDATION_ERROR` kaydı).
- **Veride hazır olacaklar:** 1 Ekim'den beri İSKİ için 13 haneli 412 doğrulama hatası (187 müşteri), 23 çağrı ve kurum duyuruları arşivi (İSKİ 12 Eylül, ASKİ Ocak 2027 ve birkaç ilgisiz duyuru). Arşiv AI Search'te ayrı bir indeks olur.

**Yedek senaryo:** Faiz parametresi güncellendiğinde 24 saat boyunca eski oranı kullanan önbellek. Daha etkileyici, ama anlatımı daha uzun.

---

### Senaryo D — "Talepten plana, sorundan kapsama" (Talep Yönlendirme · taksit hatırlatma) ⭐ önerilen kapanış

> **Yönetici özeti**
> - **Problem:** İş birimlerinin talepleri teknolojiye düz metin olarak geliyor. Etkilenen servisler, efor tahmini ve talebin hedefine gerçekten ulaşıp ulaşmayacağı geç fark ediliyor.
> - **Kim:** Fatma (Kredi Tahsilatları Bölüm Başkanlığı) → Ayşe (iş analisti)
> - **Fatma'nın talebi:** Taksit gecikmelerini azaltmak için iki şey istiyor:
>   1. Daha önce gecikme yapmış müşterilere, taksit ödeme tarihinden birkaç gün önce **otomatik hatırlatma e-postası** gönderilsin.
>   2. Temsilciler, ilgili ekrandan seçtikleri bir müşteriye o taksit için **anında hatırlatma e-postası** gönderebilsin.
> - **Mercek nasıl yönlendirdi:**
>   - Talebi iki bileşene ayırdı: günlük çalışan bir **batch işi** ve mevcut Kredi Taksit Sorgulama ekranına (`KRDRTKSR`) eklenecek bir **"Hatırlatma gönder" butonu**.
>   - Ana ve etkileşimli servisleri belirledi; benzer taleplerden 18 a/g ve takvim çıkardı.
>   - Çağrı verisiyle talebin değerini gösterdi (71 "hatırlatma almadım" çağrısı).
>   - Hedef grubun %42'sine e-postayla ulaşılamayacağını fark edip SMS'i kapsama önerdi.
> - **Sonuç:** Talep dakikalar içinde gerekçesi kanıtlanmış, kapsamı veriyle düzeltilmiş bir plana dönüştü: **20 a/g, 9 Kasım – 4 Aralık.**

**Ayrıntılar**

**Problem:** İş birimlerinin talepleri teknolojiye düz metin olarak geliyor. Hangi servislerin etkileneceği, hangi verinin hazır olduğu ve talebin hedeflenen müşteriye gerçekten ulaşıp ulaşmayacağı genellikle geliştirme başladıktan sonra fark ediliyor. Tahmin toplantılarda elle yapılıyor.

**Akış**

**1. Talep girişi.** **Fatma (Kredi Tahsilatları Bölüm Başkanlığı)** Talep Yönlendirme ekranına yazıyor:
> *"Taksit ödemelerindeki gecikmeleri azaltmak istiyoruz. Daha önce gecikme yapmış müşterilere, taksit ödeme tarihinden birkaç gün önce otomatik hatırlatma e-postası gönderilsin. Ayrıca temsilcilerimiz gerektiğinde ilgili ekrandan seçtikleri bir müşteriye o taksit için anında hatırlatma e-postası gönderebilsin."*

Talep, teknoloji tarafında analizi yürüten **Ayşe (Kıdemli İş Analisti)**'nin listesine düşüyor. Mercek'in analizi hem Fatma'nın hem Ayşe'nin ekranında görünüyor.

**2. Mercek'in talep analizi** (ekranda kartlar halinde)

**a) Talep özeti** (Mercek talebi iki bileşene ayırıyor)
1. **Otomatik hatırlatma (batch):** Her gün çalışan bir iş, ödeme tarihine X gün kalan taksitleri bulur. Bunlardan "daha önce gecikme yapmış" müşterilere ait olanlara hatırlatma e-postası gönderir.
2. **Manuel hatırlatma:** Şube veya çağrı merkezi temsilcisi, müşterinin kredi taksitlerini zaten görüntülediği **Kredi Taksit Sorgulama** ekranından (`KRDRTKSR`), seçtiği taksit için bir butonla anında hatırlatma gönderir.

Her iki durumda da gönderim yalnızca müşterinin e-posta iletişim izni varsa yapılır ve kaydı tutulur.

**b) Sınıflandırma**

| Alan | Değer |
|---|---|
| Talep tipi | **Yeni batch işi + mevcut ekran değişikliği** |
| Değişecek ekran | `KRDRTKSR` · Kredi Taksit Sorgulama ("Hatırlatma gönder" butonu) |
| İlgili ekran | `MUSTGUNC` (e-posta adresi ve iletişim izinlerinin kaynağı; değişmiyor) |
| Güven | %90 |
| Gerekçe | Temsilciler müşterinin taksitlerini zaten Kredi Taksit Sorgulama ekranında görüyor; manuel gönderim bu ekrana eklenecek bir buton. Otomatik gönderim ekran gerektirmiyor, günlük çalışan bir batch işi. |

**c) Değişiklik önerisi**

*Batch işi (otomatik hatırlatma)*
- Her gün sabah çalışır, ödeme tarihine X gün kalan ve henüz ödenmemiş taksitleri bulur.
- Yalnızca hedef gruptaki müşterileri seçer ("daha önce gecikme yapmış").
- E-posta izni olan müşterilere gönderir; aynı taksit için ikinci kez otomatik gönderim yapmaz.
- Her gönderimi kaydeder (taksit, müşteri, kanal, zaman, sonuç).

*Ekran değişikliği: `KRDRTKSR` · Kredi Taksit Sorgulama*
- Bekleyen veya gecikmedeki her taksit satırına **"Hatırlatma gönder"** butonu eklenir.
- Müşterinin e-posta izni yoksa buton pasif olur ve "İletişim izni için MUSTGUNC" yönlendirmesi gösterilir.
- Satırda o taksit için son gönderilen hatırlatma görünür (otomatik/manuel, tarih, gönderen); mükerrer gönderimin önüne geçer.

**d) Etkilenen servisler**

| Servis | Rol | Neden etkileniyor |
|---|---|---|
| **Kredi Takip Servisi** | Ana servis | Taksit vade bilgisi ve gecikme geçmişi buradan geliyor. Hedef müşteri sorgusu, günlük zamanlanmış iş, manuel gönderim uç noktası ve gönderim kaydı bu serviste. |
| **Müşteri Yönetim Servisi** | Etkileşimli servis | Müşterinin e-posta adresi ve iletişim izinleri bu servisten okunuyor (MUSTGUNC'de güncellenen alanlar). Okuma yapılacak; servisin kendisinde değişiklik beklenmiyor. |

**e) Netleştirilecek sorular** (Mercek, benzer taleplere bakarak varsayılan öneriler sunuyor)

| Soru | Mercek'in önerisi |
|---|---|
| Ödeme tarihine kaç gün kala gönderilsin? | 3 gün (benzer talep TLP-0871'de 3 gün kullanılmış) |
| "Daha önce gecikme yapmış" tanımı nedir? | Son 12 ayda en az bir taksiti 1 gün veya daha fazla gecikmiş müşteri |
| Aynı taksit için en fazla kaç hatırlatma? | 1 otomatik + 1 manuel |
| Manuel gönderimi kimler yapabilir? | Şube ve çağrı merkezi temsilcileri |
| E-postada taksit tutarı yer alsın mı? | Hayır; tutar yerine "… tarihli taksitiniz" ifadesi (e-posta güvenliği) |

Fatma önerilen varsayılanları tek tıkla kabul ediyor.

**f) Efor tahmini (adam-gün)**

Dayandığı benzer geçmiş talepler:

| Talep | Başlık | Efor | Benzerlik | Bileşen |
|---|---|---|---|---|
| TLP-0871 | Kredi kartı son ödeme tarihi SMS hatırlatması (segment bazlı, otomatik) | 14 a/g | %90 | Otomatik |
| TLP-0915 | Fatura son ödeme tarihi hatırlatma e-postası | 11 a/g | %84 | Otomatik |
| TLP-0962 | Vadeli hesap vade sonu bildirim işi | 9 a/g | %79 | Otomatik |
| TLP-1004 | Kart ekstresini ekrandan müşteriye manuel gönderme | 6 a/g | %76 | Manuel / ekran |
| TLP-1019 | Hesap hareket dökümünü şube ekranından e-posta ile iletme | 8 a/g | %74 | Manuel / ekran |

**Tahmin: 18 a/g**

| Bileşen | Tahmin |
|---|---|
| Otomatik hatırlatma (batch işi) | 11 a/g (medyan; aralık 9–14) |
| Ekrana buton ve manuel gönderim (`KRDRTKSR`) | 7 a/g (medyan; aralık 6–8) |

| Servis | Pay |
|---|---|
| Kredi Takip Servisi | 15 a/g |
| Müşteri Yönetim Servisi (adres ve izin entegrasyonu) | 3 a/g |

**g) Takvim**
- Kredi Takip Servisi **8 Kasım'a kadar dolu** (yıl sonu regülasyon işi). Müşteri Yönetim Servisi müsait.
- **Plan: 9 Kasım → 2 Aralık.** Müşteri Yönetim Servisi işi ilk hafta paralel yürür.

**h) Gerekçe** (Mercek'in açıklaması)
> *"Otomatik bileşen için en yakın örnek TLP-0871: o talepte de segment bazlı, zamanlanmış bir hatırlatma yapılmıştı, ama kanal SMS'ti. Manuel bileşen, mevcut bir ekrana gönderim butonu ekleyen iki taleple (TLP-1004, TLP-1019) neredeyse aynı. Hesap kurallarla yapıldı; ben yalnızca açıklıyorum."*

**3. Köprü: çağrı ve müşteri verisi** (Mercek kendiliğinden ekliyor)

> **Talebin değeri: çağrı geçmişi**
> - Son 90 günde "gecikme faizi / taksit tarihi" konulu **186 çağrı** var.
> - Bunların **71'inde** müşteri "ödeme tarihini unuttum / hatırlatma almadım" diyor.
> - Bu çağrılar talebin doğrudan hedeflediği sorun: ayda yaklaşık 24 çağrı önlenebilir.
>
> **Kapsam riski: hedef kitleye erişim**
> - Hedef grup (son 12 ayda gecikme yapmış, aktif bireysel kredisi olan müşteri): **2.340 müşteri.**
> - Bunların yalnızca **%58'inin e-posta iletişim izni var.** Sadece e-posta ile **983 müşteriye ulaşılamaz.**
> - Hedef grubun **%81'inin SMS izni var.** E-postaya SMS eklenirse erişim **%58 → %89** olur.
>
> **Öneri:** Hatırlatmayı e-posta izni olmayan ama SMS izni olan müşterilere SMS ile gönder (otomatik ve manuel).
> - Etkilenen servisler: Kredi Takip Servisi (kanal seçimi), Müşteri Yönetim Servisi (SMS izni ve telefon).
> - Ek efor: **+2 a/g**
>
> *Kapsama eklensin mi?*

Ayşe öneriyi Fatma'ya iletiyor. Gecikme yapan müşterilerin önemli bir kısmına e-posta ile hiç ulaşılamayacağını gören Fatma **"Evet"** diyor. Tahmin kartı güncelleniyor:
- **18 → 20 a/g** (Kredi Takip 16, Müşteri Yönetim 4)
- **Bitiş: 2 Aralık → 4 Aralık**
- Talep kaydında "veriden eklenen kapsam" olarak işaretleniyor; onaylayan: Fatma, analiz: Ayşe.

**Kanıtladığı:**
- M2.1 sınıflandırma: karma talebi (batch işi + mevcut ekran değişikliği) ayırıyor ve doğru ekranı buluyor.
- M2.2 mevcut ekrana değişiklik önerisi ve netleştirilecek sorular.
- M2.4 servis bazlı etki analizi.
- M2.5 bileşen ve servis bazlı adam-gün tahmini ve takvim.
- M2.6 köprü: çağrı verisiyle talebin değerini kanıtlıyor, müşteri verisiyle kapsam riskini yakalıyor.

**Hikâyenin kapanışı:** Bir iş biriminin düz metin talebi, beş dakika içinde gerekçesi rakamla kanıtlanmış, kapsamı veriyle düzeltilmiş, servis bazlı tahmini ve takvimi çıkmış bir geliştirme planına dönüşüyor. Talep sahibi, eksik kapsamı geliştirme bittikten sonra değil, talep anında görüyor.

**Hesap ile AI ayrımı:**
- **Kod:** Benzer talep eforlarının medyanı, servis payları, takvim, hedef grup büyüklüğü ve izin oranları, çağrı sayıları.
- **AI:** Talebi bileşenlere ayırma, sınıflandırma gerekçesi, değişiklik önerisi, netleştirilecek sorular ve açıklama metinleri.

---

### Senaryo E — Yeni ekran: "Vadesiz hesap kapama" (HSP · yeni ekran) · yedek

> **Yönetici özeti**
> - **Problem:** Şubelerde vadesiz hesap kapama talepleri bugün kâğıt formla operasyona gönderiliyor ve 2–3 gün sürüyor. Kapamadan sonra o hesaba bağlı ürünlerde (kredi taksit tahsilatı, fatura ödeme talimatı, banka kartı) sorunlar çıkıyor.
> - **Kim:** Serkan (Mevduat ve Hesap Ürünleri Bölüm Başkanlığı) → Ayşe (iş analisti)
> - **Serkan'ın talebi:** Şubeler vadesiz hesap kapama işlemini kâğıt form yerine sistem üzerinden, tek ekrandan yapabilsin.
> - **Mercek nasıl yönlendirdi:**
>   - Katalogda kapama ekranı olmadığını tespit edip talebi **yeni ekran** olarak sınıflandırdı; kurala uygun kod önerdi (`HSPTKAPA`).
>   - Ekran taslağını mevcut HSPTVDSZ ekranının bileşenlerinden ve alan standartlarından türetti; netleştirilecek soruları varsayılan önerileriyle çıkardı.
>   - Servisleri ve benzer taleplerden 12 a/g tahmini çıkardı.
>   - Çağrı geçmişinden "hesabımı kapattım, sonra taksitim/faturam ödenmedi" sorunlarını bulup **bağlı ürün kontrolünü** kapsama önerdi; etkilenen servis sayısı 2'den 5'e çıktı.
> - **Sonuç:** Kurum standartlarına uygun, bağımlılıkları baştan görülmüş bir ekran planı: **16 a/g, 2 Kasım – 23 Kasım.**

**Ayrıntılar**

**1. Talep girişi.** **Serkan (Mevduat ve Hesap Ürünleri Bölüm Başkanlığı)** Talep Yönlendirme'ye yazıyor:
> *"Şubelerimiz vadesiz hesap kapama taleplerini hâlâ kâğıt formla operasyona gönderiyor, işlem 2–3 gün sürüyor. Hesap kapama şubeden sistem üzerinden, tek ekranda yapılabilsin."*

**2. Mercek'in talep analizi**

**a) Sınıflandırma**

| Alan | Değer |
|---|---|
| Talep tipi | **Yeni ekran** |
| Gerekçe | Ekran kataloğunda hesap kapama ekranı yok. En yakın mevcut ekran `HSPTVDSZ` (Vadesiz Hesap Açılışı); aynı modülde, aynı müşteri ve hesap bileşenleri. |
| Ekran kodu önerisi | **`HSPTKAPA`** · Vadesiz Hesap Kapama (HSP = Hesaplar, T = İşlem, KAPA = kapama). `[A-Z]{3}[TR][A-Z0-9]{4}` kuralına uygun, mevcut kodlarla çakışmıyor. |
| Güven | %93 |

**b) Ekran taslağı** (mevcut bileşen ve standartlardan)

| Bölüm | İçerik | Kaynak |
|---|---|---|
| Müşteri özeti | Ad soyad, müşteri no, şube | HSPTVDSZ'deki müşteri özeti kartı (yeniden kullanım) |
| Kapatılacak hesap | Müşterinin vadesiz hesapları: hesap no, IBAN, döviz, bakiye | HSPTVDSZ hesap ve döviz alanları |
| Kalan bakiye | Başka bir hesaba aktarım (IBAN) veya şubeden nakit | IBAN alanı ve doğrulaması (mevcut standart) |
| Kapama nedeni | Liste: taşınma, başka banka, kullanmıyorum, diğer | Yeni |
| Onaylar | Sözleşme feshi bilgilendirmesi | HSPTVDSZ onay bileşeni |
| Sonuç | Referans no, kapama tarihi | Ortak `ResultPanel` |

Mercek ayrıca Joyride senaryoları için `data-tour` hedeflerini öneriyor: `hsp-kapa-account`, `hsp-kapa-balance`, `hsp-kapa-reason`, `hsp-kapa-submit`, `hsp-kapa-result`.

**c) Netleştirilecek sorular** (Mercek'in varsayılan önerileriyle)

| Soru | Mercek'in önerisi |
|---|---|
| Bakiyesi olan hesap kapanabilir mi? | Evet, ama kalan bakiyenin aktarımı ya da nakit ödemesi zorunlu |
| Döviz ve altın hesapları kapsamda mı? | İlk fazda yalnızca TRY; döviz ve altın ikinci fazda |
| Kapamayı kim onaylar? | Şube yetkilisinin ikinci onayı (dört göz) |
| Dijital kanallardan da yapılabilsin mi? | İlk fazda yalnızca şube |

**d) Etkilenen servisler (ilk analiz)**

| Servis | Rol | Neden etkileniyor |
|---|---|---|
| **Hesap Yönetim Servisi** | Ana servis | Hesap kapama işlemi, bakiye aktarımı, kapama kaydı |
| **Müşteri Yönetim Servisi** | Etkileşimli servis | Müşteri özeti için okuma; değişiklik yok |

**e) Efor tahmini (adam-gün)**

| Talep | Başlık | Efor | Benzerlik |
|---|---|---|---|
| TLP-0734 | Vadeli hesap kapama ekranı | 12 a/g | %86 |
| TLP-0899 | Vadesiz hesap açılış ekranı yenileme (HSPTVDSZ) | 14 a/g | %78 |
| TLP-0655 | Kredi kartı iptal ekranı | 11 a/g | %74 |

**Tahmin: 12 a/g** (medyan; aralık 11–14). Hesap Yönetim 10, Müşteri Yönetim 2. Hesap Yönetim Servisi 2 Kasım'da müsait; **plan: 2 Kasım → 17 Kasım.**

**3. Köprü: çağrı geçmişi**

> **Hesap kapama ile ilgili çağrılar · son 6 ay**
> - **64 çağrı:** "Hesabımı kapattım, sonra kredi taksitim tahsil edilmedi / fatura talimatım çalışmadı / kartım kullanılamaz oldu."
> - Bunların **29'unda** müşteri gecikmeye düşmüş. Ortalama çözüm süresi 2 gün.
> - Ortak neden: Kapatılan hesap, başka ürünlerin tahsilat veya bağlı hesabıymış ve bu kâğıt formda kontrol edilmemiş.
>
> **Öneri:** Ekrana **bağlı ürün kontrolü** eklensin. Kapatılacak hesaptan tahsil edilen kredi taksitleri, fatura ödeme talimatları ve bağlı banka kartı listelensin. Her biri için "başka hesaba taşı" veya "iptal et" kararı verilmeden kapama tamamlanamasın.
> - Yeni etkilenen servisler: **Kredi Takip Servisi** (taksit tahsil hesabı), **Fatura Ödeme Servisi** (talimatlar), **Kart Servisi** (bağlı kart).
> - Ek efor: **+4 a/g** (Kredi Takip 2, Fatura Ödeme 1, Kart 1)
>
> *Kapsama eklensin mi?*

Ayşe öneriyi Serkan'a iletiyor, Serkan **"Evet"** diyor. Tahmin kartı güncelleniyor:
- **12 → 16 a/g**
- **Etkilenen servis: 2 → 5**
- **Bitiş: 17 Kasım → 23 Kasım**

**Kanıtladığı:**
- M2.1 yeni ekran tespiti ve kurala uygun ekran kodu önerisi.
- M2.3 kapsam olgunlaştırma: mevcut bileşenlerin yeniden kullanımı, alan standartları, netleştirilecek sorular.
- M2.4 etki analizi: köprüyle 2'den 5 servise genişliyor.
- M2.5 adam-gün tahmini ve takvim; M2.6 çağrı verisinden kapsam.

**Neden gerçekçi:** Hesap kapama bankalarda sık yapılan, çoğu yerde hâlâ form ve operasyon onayıyla yürüyen bir işlem. "Kapatılan hesaba bağlı ürünlerin unutulması" da bilinen, can sıkıcı bir sonuç. Jüri bunu kolayca tanır.

---

### Senaryo F — Günlük durum özeti (Mercek sohbet) · yedek

> **Yönetici özeti**
> - **Problem:** Ekranların günlük durumunu görmek için Kibana'da panel taramak gerekiyor; bu herkesin yapabileceği bir iş değil.
> - **Kim:** Eyüp (platform yöneticisi)
> - **Mercek nasıl yönlendirdi:** "Bugün en çok sorun yaşanan ekran hangisi?" sorusuna loglardan özet çıkardı: ekran, sorun, etkilenen şube ve işlem sayısı, açık ana kayıt.
> - **Sonuç:** Kibana bilgisi gerektirmeden, sohbetle durum özeti.

**Ayrıntılar**

Eyüp Mercek'e soruyor: *"Bugün en çok sorun yaşanan ekran hangisi?"* Loglardan cevap: ODMTFATR, Başkentgaz zaman aşımı artışı, etkilenen şube ve işlem sayısı, açık ana kayıt. Kibana'ya girmeden sohbetle durum özeti alınıyor.

---

## 3. Önerilen demo kurgusu (≈ 2,5 dakika)

| Sahne | Senaryo | Kim | Süre | Jüri kriteri |
|---|---|---|---|---|
| 1 | **A** — Hata mı, kural mı? (KRDTKULL) | Elif | ~45 sn | Probleme uygunluk, Kullanıcı deneyimi, İş değeri (çağrı önleme) |
| 2a | **B** — Yaygın sorun, bilinen çözüm (ODMTFATR) | Mehmet (müşteri) → Zeynep (çağrı merkezi) → Eyüp | ~50 sn | Ürün çalışırlığı, İş değeri (mükerrer çağrı) |
| 2b | **C** — Dış dünya değişti (ODMTFATR · İSKİ) | Elif → Eyüp | ~35 sn | Yenilikçilik, Ürün çalışırlığı |
| 3 | **D** — Talepten plana + köprü (taksit hatırlatma) | Fatma (iş birimi) → Ayşe (analist) | ~45 sn | İş değeri, Yenilikçilik |
| Yedek | E, F | — | video / S-C | — |

**Hikâye ipi:** Mercek her sahnede aynı veriyi (loglar ve çağrı geçmişi) farklı bir işe koşuyor. Sahne 1'de çağrıyı **önlüyor**, Sahne 2a'da mükerrer çağrıları **birleştiriyor**, Sahne 2b'de çağrıyı **koda bağlıyor**, Sahne 3'te bir iş biriminin talebini **gerekçelendirip kapsamını düzeltiyor**. Ekran kodları her sahnede görünür ve Mercek'in ekran bağlamını bildiğini sürekli hatırlatır.

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
| Veri planı ve üretim rehberi | Log kaynağı olarak **Faz 5 üreticisi** (kendi log üreticimize gerek kalmıyor). Senaryo kayıtları: Başkentgaz artışı, İSKİ 13 haneli abone no doğrulama hataları (1 Ekim'den beri 412 deneme, 187 müşteri, 23 çağrı), kurum duyuruları arşivi, gecikme konulu 186 çağrı (71'i hatırlatma), 2.340 müşterilik hedef grup ve iletişim izin dağılımı (%58 e-posta, %81 SMS), 5 benzer talep (adam-gün). Servis kataloğu (Kredi Kullandırım, Kredi Takip, Müşteri Yönetim, Fatura Ödeme, Kart Başvuru…) ve servis takvimleri; ücret/maliyet yok. |
| Uygulama rehberi ve prompt'lar | **Teknoloji:** Next.js 16 + FastAPI (uv) → React/Vite varsayımı güncellenir. Ekran kimlikleri → ekran kodları ve `data-tour` hedefleri. Mercek sohbet API'si (`/api/mercek/chat`). Joyride v3 hazır olduğu için M1.5 küçülür. **Dağıtım:** Next.js + FastAPI'nin App Service'e nasıl taşınacağına karar verilmeli. |
| Sunum ve taslak ekranlar | Problem slaytı, demo slaytı, mockup'lar (iç uygulama ekranlarıyla yeniden) |
| Takım anlatım cümleleri | 2. ve 3. cümle |

---

## 5. Onay gereken kararlar

1. **Senaryo seti:** Önerim A + B + C + D canlı, E ve F yedek. Değişiklik var mı?
2. ~~Sahne 2b'deki hata~~ **Karar verildi:** ODMTFATR · İSKİ abone numarası formatı değişikliği. Yedek: faiz parametresi önbellek senaryosu.
3. ~~Mercek'in incelediği kod~~ **Karar verildi (senaryodan doğdu):** Mercek uygulamanın kendi kodunu okur. Kasıtlı hata gömülmüyor; 6–12 hane kuralı rebuild rehberinde zaten tanımlı.
4. **Mercek'e giriş:** Ekran kodu çubuğunda "Sorun yaşıyorum" butonu ile bağlamlı yan panel + ayrı Mercek sohbet sayfası (önerim) mi, yalnızca sohbet sayfası mı?
5. ~~Maliyet modeli~~ **Karar verildi:** Ücret hesaplanmaz; tahmin yalnızca **adam-gün** ve takvim. Teknoloji tarafı **servis** bazlı anlatılır (ana servis / etkileşimli servis).
6. **Demo kullanıcıları:** Faz 3'teki Mehmet (müşteri), Eyüp (L2) ve Ayşe (analist) kullanılır; sahte kullanıcı listesine üç kişi eklenir: **Elif** (şube müşteri temsilcisi, Senaryo A), **Zeynep** (çağrı merkezi temsilcisi, Senaryo B) ve **Fatma** (Kredi Tahsilatları Bölüm Başkanlığı, Senaryo D). Uygun mu?
