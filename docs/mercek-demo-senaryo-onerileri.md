# Mercek — Demo Senaryoları

## 1. Uygulama ve kullanıcılar

### Uygulama

**Ana modüller:** Bankacılık · **Mercek** (sohbet arayüzü) · **Talep Yönlendirme** (talep analizi ve efor tahmini)

**İşlem ekranları:**

| Kod | Ekran | Senaryoda kullanılan iş kuralı |
|---|---|---|
| `KRTTBASV` | Kredi Kartı Başvurusu | Gold için gelir ≥ 20.000; onay limiti = min(talep, gelir × 3, kart tavanı) |
| `KRDTKULL` | Bireysel Kredi Kullandırım | Taksit gelirin %50'sini aşarsa uyarı, buton kapalı |
| `ODMTFATR` | Fatura Ödeme | Kurum entegrasyonu (Başkentgaz, İSKİ…), abone sorgu |
| `MUSTGUNC` | Müşteri Bilgi Güncelleme | İletişim izinleri (SMS, e-posta, telefon) |
| `HSPTVDSZ` | Vadesiz Hesap Açılışı | Döviz cinsi, şube, IBAN üretimi |

**Servisler:** Teknoloji tarafı servis bazlı anlatılır: Kredi Kullandırım, Kredi Takip, Müşteri Yönetim, Fatura Ödeme, Hesap Yönetim ve Kart Başvuru servisleri. Talep analizlerinde her talep için bir **ana servis** ve **etkileşimli servisler** belirlenir; tahminler **adam-gün (a/g)** cinsindendir.

### Kullanıcılar ve Mercek'e giriş noktaları

| Kullanıcı | Nerede çalışır | Mercek'e nasıl ulaşır |
|---|---|---|
| **Elif** (şube müşteri temsilcisi) | Bankacılık işlem ekranları | Ekran kodu çubuğundaki **"Sorun yaşıyorum"** butonu. Mercek paneli ekran kodu, müşteri no, son `trace.id` ve ekrandaki hata mesajıyla açılır. |
| **Mehmet** (banka müşterisi) | İnternet şubesi (ODMTFATR) | Mercek'i kullanmaz; sorun yaşayınca çağrı merkezini arar. |
| **Zeynep** (çağrı merkezi temsilcisi) | Mercek sohbet | Müşterinin anlattığını serbest metinle yazar; Mercek logları, ana kaydı ve müşteriye söylenecekleri getirir. |
| **Kerem** (Platform Yöneticisi / L2 destek) | Mercek sayfası | Sohbet + çağrı listesi: zenginleştirilmiş kayıtlar, loglar, eşleşmeler, kod analizi |
| **Fatma** (Kredi Tahsilatları Bölüm Başkanlığı, iş birimi) | Talep Yönlendirme | İhtiyacını kendi cümleleriyle yazar; Mercek'in analizini görür, kapsam önerisini onaylar. |
| **Ayşe** (Kıdemli İş Analisti, teknoloji) | Talep Yönlendirme | Mercek'in analizini gözden geçirir, açık soruları iş birimiyle netleştirir, köprü önerisini iş birimine sunar. |

---

## 2. Senaryolar

### Senaryolar bir bakışta

| Senaryo | Problem | Mercek'in katkısı | Sonuç |
|---|---|---|---|
| **A** · KRDTKULL | Temsilci hata mı kural mı bilemiyor | Logdan iş kuralını açıklıyor, uygun tutarı hesaplayıp ekranı dolduruyor | Çağrı hiç açılmıyor |
| **B** · ODMTFATR | Kurum sorunu; her müşteri ayrı çağrı | Müşteriye hazır açıklama, ana kayda bağlama, %93 eşleşen çözüm | Onlarca çağrı tek kayıtta |
| **C** · ODMTFATR | Kurum numara formatını değiştirdi, ekran eskide kaldı | Log örüntüsü + kurum duyurusu + kod; düzeltme ve kalıcı öneri | 187 müşteri bulundu, sonraki olay önlendi |
| **D** · Talep Yönlendirme | İş birimi taksit hatırlatması istiyor (otomatik + ekrandan manuel); servis, efor ve erişim geç fark ediliyor | Bileşen ve servis analizi, a/g tahmini, çağrı ve izin verisiyle kapsam düzeltme | Gerekçeli plan: 20 a/g |
| E · yedek | Afet sonrası acil taksit erteleme kararı; ekran yok, süre iki hafta | Yeni ekran ve kodu, etkilenen müşteri sayısı, riskli sorular, kapasite çatışması seçenekleri, proaktif SMS | Aynı gün karar verilebilir plan: 17 a/g |
| F · yedek | Durum görmek Kibana bilgisi istiyor | Sohbetle günlük özet | Herkes için durum görünürlüğü |

### 2.1 Yönetici özetleri

#### Senaryo A — "Hata mı, kural mı?" (KRDTKULL · iş kuralı reddi) · açılış

> - **Problem:** Şube temsilcisi müşteriye kredi kullandıramıyor. Ekrandaki uyarının sistem hatası mı yoksa iş kuralı mı olduğunu ayırt edemiyor ve çağrı açmaya yöneliyor.
> - **Kim:** Elif (şube müşteri temsilcisi)
> - **Mercek nasıl yönlendirdi:** Ekran kodu ve son işlem üzerinden logu buldu. Durumun hata değil iş kuralı olduğunu açıkladı (taksit gelirin %50'sini aşıyor). Kullandırılabilecek en yüksek tutarı hesapladı (36 ay, ~334.000 TL) ve "Bana göster" ile ekranı doğru değerlerle doldurdu.
> - **Sonuç:** İşlem şubede tamamlandı, **çağrı hiç açılmadı.**

#### Senaryo B — "Yaygın teknik sorun, bilinen çözüm" (ODMTFATR · kurum zaman aşımı · çağrı merkezi)

> - **Problem:** Bir kurumun (Başkentgaz) entegrasyonu yavaşladı, müşteriler fatura ödeyemiyor ve çağrı merkezini arıyor. Her aramada ayrı çağrı açılıyor, temsilci müşteriye ne söyleyeceğini bilmiyor.
> - **Kim:** Mehmet (müşteri) → Zeynep (çağrı merkezi) → Kerem (L2)
> - **Mercek nasıl yönlendirdi:**
>   - Temsilcinin serbest metninden ekranı, kurumu ve abone no'yu çıkardı; loglarda müşterinin başarısız işlemini ve yaygın kurum sorununu buldu.
>   - Temsilciye müşteriye söylenecek hazır açıklamayı verdi.
>   - Yeni çağrı açmak yerine vakayı mevcut ana kayda bağladı.
>   - L2'ye %93 eşleşen geçmiş çözümü getirdi.
> - **Sonuç:** Müşteri doğru bilgilendirildi, onlarca arama **tek kayıtta toplandı**, L2 bilinen çözümü dakikalar içinde uyguladı.

#### Senaryo C — "Dış dünya değişti, ekran değişmedi" (ODMTFATR · İSKİ abone numarası formatı)

> - **Problem:** İSKİ yeni abonelere 13 haneli numara vermeye başladı, ama ekranımız 6–12 hane kabul ediyor. Müşteriler su faturasını ödeyemiyor ve kimse nedenini bilmiyor.
> - **Kim:** Elif (şube) → Kerem (L2)
> - **Mercek nasıl yönlendirdi:**
>   - Log örüntüsünü buldu: hatalar yalnızca İSKİ'de, yalnızca 13 haneli numaralarda ve 1 Ekim'den beri görülüyor.
>   - Kurum duyuruları arşivinde İSKİ'nin geçiş duyurusunu buldu.
>   - Kuralın kodda iki yerde sabit yazıldığını gösterdi; düzeltmeyi ve kalıcı öneriyi (kurum bazlı parametre) sundu.
>   - ASKİ'nin Ocak'taki benzer geçişini önceden haber verdi.
> - **Sonuç:** Kök neden dakikalar içinde bulundu, **187 etkilenen müşteri** belirlendi, bir sonraki benzer olay önlendi.

#### Senaryo D — "Talepten plana, sorundan kapsama" (Talep Yönlendirme · taksit hatırlatma) · kapanış

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

#### Senaryo E — Acil yeni ekran: "Afet bölgesi taksit erteleme başvurusu" (KRD · yeni ekran) · yedek

> - **Problem:** Bir doğal afetin ardından banka yönetimi, etkilenen illerdeki müşterilerin bireysel kredi taksitlerini 3 ay ertelemeye karar veriyor ve uygulamanın **iki hafta içinde** devreye girmesini istiyor. Erteleme başvurusu alıp yeni ödeme planı üreten bir ekran yok.
> - **Kim:** Hakan (Bireysel Krediler Bölüm Başkanlığı) → Ayşe (iş analisti)
> - **Hakan'ın talebi:** Etkilenen illerdeki müşteriler şubeden ve çağrı merkezinden taksit erteleme başvurusu yapabilsin; erteleme sonrası yeni ödeme planı müşteriye gösterilsin.
> - **Mercek nasıl yönlendirdi:**
>   - Talebi **yeni ekran** olarak sınıflandırdı, kurala uygun kod önerdi (`KRDTERTL`); ödeme planı hesabını KRDTKULL'den yeniden kullanan bir taslak çıkardı.
>   - Etkilenen müşteri sayısını hemen hesapladı: **4.870 müşteri, 6.215 kredi.**
>   - Kimsenin sormadığı kritik soruları getirdi: uygunlukta afet tarihinden sonra değiştirilen adresler, ve Senaryo D'de planlanan hatırlatma işinin ertelenen taksitler için mesaj göndermemesi.
>   - **Kapasite çatışmasını yakaladı:** Ana servis 8 Kasım'a kadar regülasyon işiyle dolu; "iki hafta" hedefi ancak öncelik kararıyla tutuyor. İki seçeneği sonuçlarıyla birlikte sundu.
>   - Çağrı verisinden etkilenen illerdeki çağrı artışını görüp müşterilere **proaktif SMS bilgilendirmesi** önerdi.
> - **Sonuç:** Acil bir yönetim kararı, aynı gün içinde etkisi, riski ve takvim seçenekleri ortaya konmuş bir plana dönüştü: **17 a/g**; öncelik verilirse **19 Ekim – 2 Kasım.**

#### Senaryo F — Günlük durum özeti (Mercek sohbet) · yedek

> - **Problem:** Ekranların günlük durumunu görmek için Kibana'da panel taramak gerekiyor; bu herkesin yapabileceği bir iş değil.
> - **Kim:** Kerem (platform yöneticisi)
> - **Mercek nasıl yönlendirdi:** "Bugün en çok sorun yaşanan ekran hangisi?" sorusuna loglardan özet çıkardı: ekran, sorun, etkilenen şube ve işlem sayısı, açık ana kayıt.
> - **Sonuç:** Kibana bilgisi gerektirmeden, sohbetle durum özeti.

---

### 2.2 Senaryo detayları

#### Senaryo A — "Hata mı, kural mı?" (KRDTKULL · iş kuralı reddi) · açılış

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

#### Senaryo B — "Yaygın teknik sorun, bilinen çözüm" (ODMTFATR · kurum zaman aşımı · çağrı merkezi)

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
6. **Kerem (L2)**, Mercek sayfasında CAG-2051'i açıyor:
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

#### Senaryo C — "Dış dünya değişti, ekran değişmedi" (ODMTFATR · İSKİ abone numarası formatı)

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

**3. Kerem (L2) çağrıyı açıyor.** Geçmiş çözümlerle eşleşme **%35**, eşiğin (%75) altında; bu yeni bir sorun. Mercek koda geçiyor.

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
- Bu sefer kasıtlı bir hata gömülmüyor. Uygulamada ODMTFATR abone numarası kuralı zaten **6–12 hane** olarak tanımlı. Mercek **uygulamanın kendi kodunu** okuyabilir; `sample-codebase/` kopyasına gerek yok.
- Demo modunda ekrandaki doğrulama hatası backend'e log olarak yazılır (gerçekte Fatura Ödeme Servisi'nin `VALIDATION_ERROR` kaydı).
- **Veride hazır olacaklar:** 1 Ekim'den beri İSKİ için 13 haneli 412 doğrulama hatası (187 müşteri), 23 çağrı ve kurum duyuruları arşivi (İSKİ 12 Eylül, ASKİ Ocak 2027 ve birkaç ilgisiz duyuru). Arşiv AI Search'te ayrı bir indeks olur.


---

#### Senaryo D — "Talepten plana, sorundan kapsama" (Talep Yönlendirme · taksit hatırlatma) · kapanış

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

#### Senaryo E — Acil yeni ekran: "Afet bölgesi taksit erteleme başvurusu" (KRD · yeni ekran) · yedek

**1. Talep girişi.** **Hakan (Bireysel Krediler Bölüm Başkanlığı)** Talep Yönlendirme'ye yazıyor:
> *"Yönetim, doğal afetten etkilenen 3 ildeki müşterilerimizin bireysel kredi taksitlerinin 3 ay ertelenmesine karar verdi. Erteleme başvurusu şubelerden ve çağrı merkezinden alınabilsin, müşteriye ertelemeden sonraki yeni ödeme planı gösterilsin. Uygulamanın iki hafta içinde devreye girmesi gerekiyor."*

**2. Mercek'in talep analizi**

**a) Sınıflandırma**

| Alan | Değer |
|---|---|
| Talep tipi | **Yeni ekran** (acil) |
| Gerekçe | Ekran kataloğunda mevcut bir kredinin ödeme planını değiştiren ya da erteleme başvurusu alan bir ekran yok. KRDTKULL yalnızca yeni kredi kullandırıyor; ödeme planı hesabı oradan yeniden kullanılabilir. |
| Ekran kodu önerisi | **`KRDTERTL`** · Kredi Taksit Erteleme Başvurusu (KRD = Krediler, T = İşlem, ERTL = erteleme). Kurala uygun, mevcut kodlarla çakışmıyor. |
| Güven | %94 |

**b) Etkilenen müşteri büyüklüğü** (kod, veriden)
- Etkilenen 3 ilde adresi kayıtlı ve aktif bireysel kredisi olan **4.870 müşteri**, toplam **6.215 kredi.**
- Bu kredilerin **612'si** şu anda gecikmede.

**c) Ekran taslağı**

| Bölüm | İçerik | Kaynak |
|---|---|---|
| Müşteri ve uygunluk | Müşteri no ile arama; adres afet bölgesinde mi ve **afet tarihinden önce mi kayıtlı** kontrolü | MUSTGUNC adres bilgisi ve adres değişiklik tarihi |
| Aktif krediler | Kredi listesi: kalan anapara, sıradaki taksit tarihi, gecikme durumu | Kredi Takip Servisi |
| Erteleme seçimi | Ertelenecek kredi(ler); süre (karar gereği 3 ay, parametre) | Yeni |
| Yeni ödeme planı önizleme | Ertelenen taksitlerin vade sonuna eklendiği plan; eski ve yeni plan yan yana | KRDTKULL ödeme planı hesabı (yeniden kullanım) |
| Bilgilendirme ve onay | Müşteri bilgilendirme metni, onay | KRDTKULL onay bileşeni |
| Sonuç | Referans no, yeni ilk taksit tarihi | Ortak `ResultPanel` |

**d) Netleştirilecek sorular** (Mercek'in varsayılan önerileriyle)

| Soru | Mercek'in önerisi |
|---|---|
| Uygunluk adrese göre mi belirlenecek? Afet sonrası adres değiştirenler ne olacak? | Afet tarihinden **önce** kayıtlı adres esas alınsın; sonradan değişen adresler şube yetkilisi onayına düşsün (kötüye kullanım riski). |
| Erteleme süresince faiz işletilecek mi? | Yönetim kararına göre; ekranda veya kodda sabit değil, **ürün parametresi** olarak tanımlansın. |
| Şu an gecikmede olan taksitler kapsamda mı? Gecikme faizi silinecek mi? | Kapsamda olsun; gecikme faizi kararı iş birimine ait (**açık soru**). |
| Hangi kredi türleri kapsamda? | İlk fazda bireysel ihtiyaç kredileri (KRDTKULL ile kullandırılanlar). |
| Planlanan diğer işlerle çakışma var mı? | **Var:** Senaryo D'de planlanan taksit hatırlatma işi, ertelenen taksitler için hatırlatma göndermemeli. İki talebe de not düşüldü. |

**e) Etkilenen servisler**

| Servis | Rol | Neden etkileniyor |
|---|---|---|
| **Kredi Takip Servisi** | Ana servis | Taksit planının değiştirilmesi, erteleme kaydı, gecikme durumunun güncellenmesi |
| **Kredi Kullandırım Servisi** | Etkileşimli servis | Ödeme planı hesaplama bileşeni yeniden kullanılıyor |
| **Müşteri Yönetim Servisi** | Etkileşimli servis | Adres ve adres değişiklik tarihi okunuyor (uygunluk kontrolü) |

**f) Efor tahmini (adam-gün)**

| Talep | Başlık | Efor | Benzerlik |
|---|---|---|---|
| TLP-0588 | Salgın döneminde kredi taksit erteleme ekranı | 15 a/g | %87 |
| TLP-0712 | Kredi kartı borcu taksitlendirme ekranı | 13 a/g | %79 |
| TLP-0846 | Kredi vade değişikliği (iç operasyon ekranı) | 17 a/g | %76 |

**Tahmin: 15 a/g** (medyan; aralık 13–17). Kredi Takip 10, Müşteri Yönetim 3, Kredi Kullandırım 2.

**g) Takvim ve kapasite çatışması**

> *"İki haftalık hedef, ana servis olan Kredi Takip Servisi'ne bağlı. Bu servis 8 Kasım'a kadar yıl sonu regülasyon işiyle dolu. Karar gerekiyor:"*

| Seçenek | Erteleme ekranı | Yan etkisi |
|---|---|---|
| **A. Öncelik ver** (regülasyon işinden 2 hafta kapasite kaydır) | **19 Ekim → 30 Ekim** (hedef tutar) | Regülasyon işi 8 → 22 Kasım'a kayar. Yasal bir son tarihi varsa bu seçenek uygulanamaz. Senaryo D'deki hatırlatma talebi 4 → 18 Aralık'a kayar. |
| **B. Sıraya koy** | **9 Kasım → 20 Kasım** (hedef kaçar, ~3 hafta geç) | Regülasyon işi etkilenmez. Senaryo D'deki talep 21 Aralık'a kayar. |

Ayşe iki seçeneği Hakan'a ve servis sahiplerine sunuyor. Afet aciliyeti nedeniyle **A** seçiliyor; regülasyon işinin son tarihi olmadığı teyit ediliyor.

**3. Köprü: çağrı verisi**

> **Etkilenen 3 il · son 5 gün**
> - Bu illerden gelen çağrılar normalin **6 katı.**
> - En sık konu: *"Taksitimi ödeyemeyeceğim, erteleme var mı?"* (**418 çağrı**).
>
> **Öneri:** Erteleme hakkı olan 4.870 müşteriye **proaktif SMS bilgilendirmesi** gönderilsin: hak, başvuru kanalları, son başvuru tarihi. Hem müşteri hakkından haberdar olur, hem de çağrı merkezine gelen bilgi amaçlı aramalar azalır.
> - İletişim izni olan müşterilere gönderilir (Müşteri Yönetim Servisi).
> - Gönderim, Senaryo D'de planlanan gönderim altyapısıyla aynı yaklaşımı kullanır.
> - Ek efor: **+2 a/g** (Kredi Takip 1, Müşteri Yönetim 1)
>
> *Kapsama eklensin mi?*

Hakan **"Evet"** diyor. Tahmin kartı güncelleniyor:
- **15 → 17 a/g**
- **Seçenek A ile bitiş: 30 Ekim → 2 Kasım**

**Kanıtladığı:**
- M2.1 yeni ekran tespiti ve kurala uygun ekran kodu.
- M2.3 kapsam olgunlaştırma: yeniden kullanım ve kimsenin sormadığı riskli sorular (adres değiştirme, D ile çakışma).
- M2.4 servis etki analizi; M2.5 tahmin ve **kapasite çatışmasının seçenekleriyle görünür kılınması**.
- M2.6 köprü: çağrı artışından proaktif bilgilendirme kapsamı.

**Neden gerçekçi:** Afet sonrası taksit erteleme Türkiye'de bankaların gerçekten yaşadığı, çok kısa sürede devreye alınması gereken bir ihtiyaç. Bu tür acil talepler mevcut işlerle çatışır; o çatışmayı ilk gün görmek planlamanın en değerli kısmıdır.

**Sunum notu (hassasiyet):**
- Gerçek bir afet, il adı veya tarih kullanılmaz; veride "etkilenen 3 il" sentetik tanımlanır.
- Mercek'in mesajları sade ve saygılı bir dille yazılır; görsel olarak afet imgesi kullanılmaz.

---

#### Senaryo F — Günlük durum özeti (Mercek sohbet) · yedek

Kerem Mercek'e soruyor: *"Bugün en çok sorun yaşanan ekran hangisi?"* Loglardan cevap: ODMTFATR, Başkentgaz zaman aşımı artışı, etkilenen şube ve işlem sayısı, açık ana kayıt. Kibana'ya girmeden sohbetle durum özeti alınıyor.

---

## 3. Demo kurgusu (≈ 2,5 dakika)

| Sahne | Senaryo | Kim | Süre | Jüri kriteri |
|---|---|---|---|---|
| 1 | **A** — Hata mı, kural mı? (KRDTKULL) | Elif | ~45 sn | Probleme uygunluk, Kullanıcı deneyimi, İş değeri (çağrı önleme) |
| 2a | **B** — Yaygın sorun, bilinen çözüm (ODMTFATR) | Mehmet (müşteri) → Zeynep (çağrı merkezi) → Kerem | ~50 sn | Ürün çalışırlığı, İş değeri (mükerrer çağrı) |
| 2b | **C** — Dış dünya değişti (ODMTFATR · İSKİ) | Elif → Kerem | ~35 sn | Yenilikçilik, Ürün çalışırlığı |
| 3 | **D** — Talepten plana + köprü (taksit hatırlatma) | Fatma (iş birimi) → Ayşe (analist) | ~45 sn | İş değeri, Yenilikçilik |
| Yedek | E, F | — | video / S-C | — |

**Hikâye ipi:** Mercek her sahnede aynı veriyi (loglar ve çağrı geçmişi) farklı bir işe koşuyor. Sahne 1'de çağrıyı **önlüyor**, Sahne 2a'da mükerrer çağrıları **birleştiriyor**, Sahne 2b'de çağrıyı **koda bağlıyor**, Sahne 3'te bir iş biriminin talebini **gerekçelendirip kapsamını düzeltiyor**. Ekran kodları her sahnede görünür ve Mercek'in ekran bağlamını bildiğini sürekli hatırlatır.

**Problem slaytı da buna göre değişir:** *"Şube personeli işlem yapamadığında hata mı kural mı bilemiyor, çağrı açıyor. L1 ve L2 Kibana'da log arıyor, aynı sorun için onlarca çağrı açılıyor, bilinen çözümler kişilerde kalıyor. Yeni talepler bu sorunlardan habersiz planlanıyor."*

### İş değeri anlatımı

| Ölçü | Bugün | Mercek ile |
|---|---|---|
| İş kuralı reddi | Çağrı açılır, L1 kuralı açıklar | Ekranda anında açıklanır, uygun alternatif önerilir: **çağrı hiç açılmaz** |
| Yaygın teknik sorun | Her şubeden ayrı çağrı | Tek ana kayıt, şubelere anında bilgi |
| Bilinen sorun | L2 log arar, çözüm kişide | %93 eşleşme, kaynaklı çözüm, saniyeler |
| Yeni hata | Kod baştan incelenir | Log + kod ilişkilendirilip satır düzeyinde öneri |
| Talep tahmini | Toplantıda elle; etkilenen servisler sonradan ortaya çıkıyor | Servis bazlı etki, benzer taleplerden adam-gün ve takvim; ekranın sorun geçmişi kapsamda |
