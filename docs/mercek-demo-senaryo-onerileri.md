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

### Senaryo C — "AI kodu okur" (HSPTVDSZ · IBAN kontrol hanesi hatası) ⭐

**Senaryo tek cümleyle:** Geçmişte örneği olmayan bir hata geliyor. Mercek önce kuralla IBAN'ın bozuk olduğunu ve bunun banka kaynaklı olduğunu kanıtlıyor. Sonra loglardan sorunun kaç hesabı etkilediğini buluyor, son olarak kodu okuyup hatanın satırını ve düzeltmesini gösteriyor.

**Problem:** Geçmişte örneği olmayan bir hata çağrısında L2 nereden başlayacağını bilmiyor: kullanıcı hatası mı, karşı banka mı, bizim kodumuz mu? Kod baştan inceleniyor; aynı hatadan kaç müşterinin etkilendiği ise çoğu zaman hiç bilinmiyor.

**Akış**

**1. Çağrı.** Bir müşteri şubeye geliyor: yeni açtığı vadesiz hesaba başka bir bankadan para gönderilemiyor, karşı banka "IBAN hatalı" diyor. **Elif (şube temsilcisi)** Mercek'e yazıyor:
> *"Müşterinin geçen hafta HSPTVDSZ'den açılan hesabına başka bankadan para gelmiyor, IBAN hatalı diyorlar. IBAN: TR30 0999 0711 4710 4974 6507 5"*

**2. Mercek'in ilk kontrolü** (kural, AI değil):
> *"Bu IBAN geçersiz ve hata bankamız kaynaklı. Türkiye IBAN'ı 26 karakter olmalı, bu 25 karakter. Hesap numarası doğru, ama kontrol hanesinin başındaki 0 eksik: kontrol hanesi '03' olmalıyken '3' yazılmış. 4'lü gruplamada bu, IBAN'ı 'TR30…' gibi normal gösterip hatayı gizliyor. Doğru IBAN: **TR03 0099 9071 1471 0497 4650 75**. Müşteriye bu IBAN'ı verebilirsiniz; para bu IBAN'a gelir."*

Elif müşteriyi doğru IBAN ile hemen gönderiyor. Mercek çağrıyı açıp **Hesap Açılış Servisi**'ne atıyor (kural: HSPTVDSZ + IBAN üretimi).

**3. Eyüp (L2) çağrıyı açıyor.** Geçmiş çözümlerle eşleşme **%38**, eşiğin (%75) altında. Mercek uydurma bir çözüm önermiyor, analize geçiyor.

**4. Loglarla etki analizi:**
> *"Son 30 günde HSPTVDSZ ile **1.432** hesap açılmış. Bunların **117'sinin** (%8,2) IBAN'ı 25 karakter. Hepsinde kontrol hanesi 02 ile 09 arasında. Kontrol hanesi 2–98 arasında 97 farklı değer alabildiği için tek haneli 8 değer beklenen oran olan %8,2'yi veriyor. Yani hata rastgele değil, sistematik."*

Etkilenen 117 hesabın listesi (hesap no, şube, açılış tarihi) çağrıya ekleniyor.

**5. Kod analizi:** Mercek Hesap Açılış Servisi'nin IBAN üretim kodunu okuyor:

```diff
   const check = 98 - mod97(bban + "292700");
-  return `TR${check}${bban}`;
+  return `TR${String(check).padStart(2, "0")}${bban}`;
```

> *"Kök neden: Kontrol hanesi 10'dan küçük çıktığında başına 0 eklenmiyor. Bu yüzden IBAN 25 karakter oluyor ve diğer bankaların doğrulamasından geçmiyor.*
> *Test önerisi: 1.000 rastgele IBAN üret; hepsinin 26 karakter olduğunu ve ISO 13616 mod-97 doğrulamasından geçtiğini kontrol et.*
> *Ek öneri: Etkilenen 117 hesabın doğru IBAN'ı, aynı hesap numarasından yeniden hesaplanabilir. Müşterilere bilgilendirme gönderilmeli."*

Etiket: **"Öneridir, uygulanmadı."**

**Kanıtladığı:**
- **Kural ile AI'ın birlikte çalışması:** IBAN doğrulaması ve doğru IBAN'ın hesabı kodla yapılıyor (deterministik, kesin). Yorum ve kök neden AI'dan geliyor.
- **M1.4 eşleşme yoksa kod analizi** ve dürüst eşik: uydurma eşleşme yok.
- **Log + kod ilişkilendirme:** Tek bir çağrıdan, sessizce etkilenen 117 müşteriye ulaşılıyor. Bu müşteriler henüz çağrı açmamış; Mercek sorunu onlar fark etmeden buluyor.
- **Anında müşteri çözümü:** Elif, kod düzeltilmeden önce müşteriye doğru IBAN'ı veriyor.

**Jüriye nasıl görünür:** Önce ekranda görünen hali, sonra boşluksuz hali gösterilir.
- Ekranda (4'lü grup): **TR30 0999 0711 4710 4974 6507 5** — normal bir IBAN gibi görünüyor.
- Boşluksuz, hatalı: `TR3` + `0099907114710497465075` → 25 karakter
- Boşluksuz, doğru: `TR03` + `0099907114710497465075` → 26 karakter

Tek bir eksik "0" görsel olarak hemen anlaşılır; gruplamanın hatayı nasıl gizlediği de neden kimsenin fark etmediğini açıklar. Ardından "%8,2 = 97 değerden 8'i" açıklaması, hatanın rastgele değil sistematik olduğunu gösterir.

**Önemli:** Hatalı kod **uygulamanın kendisinde değil**, `sample-codebase/` altındaki "Hesap Açılış Servisi" kopyasında durur. Uygulamadaki `generateIban()` doğru kalır (rebuild rehberinin "1.000 IBAN'ın tamamı geçerli" kabul kriteri bozulmaz) ve kod kalitesi puanı zarar görmez.
**Veride hazır olacaklar:** HSPTVDSZ için 30 günde 1.432 hesap açılış logu; bunların 117'sinde 25 karakterli IBAN (kontrol hanesi 2–9). Örnek müşterinin hesabı ve IBAN'ı sabit.

**Alternatif hata (yedek):** KRTTBASV'de Gold kart gelir şartı `gelir >= 20000` yerine `gelir > 20000` yazılmış; geliri tam 20.000 TL olan müşteriler reddediliyor. Anlaşılması daha kolay, ama "sessizce etkilenen müşterileri bulma" etkisi daha zayıf.

---

### Senaryo D — "Talepten plana, sorundan kapsama" (Talep Yönlendirme · taksit hatırlatma) ⭐ önerilen kapanış

**Senaryo tek cümleyle:** Bir iş birimi taksit gecikmelerini azaltmak için hatırlatma özelliği istiyor. Mercek talebi bileşenlerine ayırıyor, etkilenen servisleri, adam-gün tahminini ve takvimi çıkarıyor. Sonra çağrı ve müşteri verisine bakıp hem talebin değerini rakamla doğruluyor, hem de talebin hedef kitlenin önemli bir kısmına ulaşamayacağını fark edip kapsamı düzeltiyor.

**Problem:** İş birimlerinin talepleri teknolojiye düz metin olarak geliyor. Hangi servislerin etkileneceği, hangi verinin hazır olduğu ve talebin hedeflenen müşteriye gerçekten ulaşıp ulaşmayacağı genellikle geliştirme başladıktan sonra fark ediliyor. Tahmin toplantılarda elle yapılıyor.

**Akış**

**1. Talep girişi.** **Fatma (Kredi Tahsilatları Bölüm Başkanlığı)** Talep Yönlendirme ekranına yazıyor:
> *"Taksit ödemelerindeki gecikmeleri azaltmak istiyoruz. Daha önce gecikme yapmış müşterilere, taksit ödeme tarihinden birkaç gün önce otomatik hatırlatma e-postası gönderilsin. Ayrıca temsilcilerimiz gerektiğinde ilgili ekrandan seçtikleri bir müşteriye o taksit için anında hatırlatma e-postası gönderebilsin."*

Talep, teknoloji tarafında analizi yürüten **Ayşe (Kıdemli İş Analisti)**'nin listesine düşüyor. Mercek'in analizi hem Fatma'nın hem Ayşe'nin ekranında görünüyor.

**2. Mercek'in talep analizi** (ekranda kartlar halinde)

**a) Talep özeti** (Mercek talebi iki bileşene ayırıyor)
1. **Otomatik hatırlatma:** Her gün çalışan bir iş, ödeme tarihine X gün kalan taksitleri bulur. Bunlardan "daha önce gecikme yapmış" müşterilere ait olanlara hatırlatma e-postası gönderir.
2. **Manuel hatırlatma:** Şube veya çağrı merkezi temsilcisi, bir müşterinin kredi taksitlerini görüntülediği ekrandan, seçtiği taksit için anında hatırlatma gönderir.

Her iki durumda da gönderim yalnızca müşterinin e-posta iletişim izni varsa yapılır ve kaydı tutulur.

**b) Sınıflandırma**

| Alan | Değer |
|---|---|
| Talep tipi | Yeni geliştirme: **arka plan işi + yeni ekran** |
| İlgili mevcut ekranlar | `KRDTKULL` (taksit planının kaynağı), `MUSTGUNC` (e-posta adresi ve iletişim izinleri) |
| Yeni ekran önerisi | **`KRDTTKIP` · Kredi Taksit Takip.** Kod kurala (`[A-Z]{3}[TR][A-Z0-9]{4}`) uygun, mevcut kodlarla çakışmıyor. |
| Güven | %88 |
| Gerekçe | Ekran kataloğunda müşterinin kredilerini ve taksitlerini listeleyen bir ekran yok. Manuel gönderim için böyle bir ekran gerekiyor. |

**c) Yeni ekran taslağı: `KRDTTKIP`**
- **Arama:** Müşteri no ile. Aktif krediler ve her kredinin taksit listesi: vade tarihi, tutar, durum (ödendi / bekliyor / gecikmede).
- **Taksit satırında "Hatırlatma gönder" butonu.** Müşterinin e-posta izni yoksa buton pasif olur ve "İletişim izni için MUSTGUNC" yönlendirmesi gösterilir.
- **Gönderim geçmişi:** Bu taksit için daha önce gönderilen hatırlatmalar (otomatik veya manuel), tarih ve gönderen.

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
| Otomatik hatırlatma işi | 11 a/g (medyan; aralık 9–14) |
| Yeni ekran ve manuel gönderim (`KRDTTKIP`) | 7 a/g (medyan; aralık 6–8) |

| Servis | Pay |
|---|---|
| Kredi Takip Servisi | 15 a/g |
| Müşteri Yönetim Servisi (adres ve izin entegrasyonu) | 3 a/g |

**g) Takvim**
- Kredi Takip Servisi **8 Kasım'a kadar dolu** (yıl sonu regülasyon işi). Müşteri Yönetim Servisi müsait.
- **Plan: 9 Kasım → 2 Aralık.** Müşteri Yönetim Servisi işi ilk hafta paralel yürür.

**h) Gerekçe** (Mercek'in açıklaması)
> *"Otomatik bileşen için en yakın örnek TLP-0871: o talepte de segment bazlı, zamanlanmış bir hatırlatma yapılmıştı, ama kanal SMS'ti. Manuel bileşen, ekrandan doküman gönderen iki taleple benzer. Bu talepte ek olarak yeni bir ekran gerekiyor. Hesap kurallarla yapıldı; ben yalnızca açıklıyorum."*

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
- M2.1 sınıflandırma: karma talebi (arka plan işi + yeni ekran) ayırıyor.
- M2.3 yeni ekran kapsamı: ekran kodu önerisi, taslak, netleştirilecek sorular.
- M2.4 servis bazlı etki analizi.
- M2.5 bileşen ve servis bazlı adam-gün tahmini ve takvim.
- M2.6 köprü: çağrı verisiyle talebin değerini kanıtlıyor, müşteri verisiyle kapsam riskini yakalıyor.

**Hikâyenin kapanışı:** Bir iş biriminin düz metin talebi, beş dakika içinde gerekçesi rakamla kanıtlanmış, kapsamı veriyle düzeltilmiş, servis bazlı tahmini ve takvimi çıkmış bir geliştirme planına dönüşüyor. Talep sahibi, eksik kapsamı geliştirme bittikten sonra değil, talep anında görüyor.

**Hesap ile AI ayrımı:**
- **Kod:** Benzer talep eforlarının medyanı, servis payları, takvim, hedef grup büyüklüğü ve izin oranları, çağrı sayıları.
- **AI:** Talebi bileşenlere ayırma, sınıflandırma gerekçesi, ekran taslağı, netleştirilecek sorular ve açıklama metinleri.

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
| 2b | **C** — AI kodu okur (HSPTVDSZ) | Elif → Eyüp | ~40 sn | Yenilikçilik, İş değeri (sessizce etkilenen 117 müşteri) |
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
| Veri planı ve üretim rehberi | Log kaynağı olarak **Faz 5 üreticisi** (kendi log üreticimize gerek kalmıyor). Senaryo kayıtları: Başkentgaz artışı, HSPTVDSZ'de 117 hatalı IBAN'lı hesap (1.432 açılış içinde), gecikme konulu 186 çağrı (71'i hatırlatma), 2.340 müşterilik hedef grup ve iletişim izin dağılımı (%58 e-posta, %81 SMS), 5 benzer talep (adam-gün). Servis kataloğu (Kredi Kullandırım, Kredi Takip, Müşteri Yönetim, Fatura Ödeme, Kart Başvuru…) ve servis takvimleri; ücret/maliyet yok. |
| Uygulama rehberi ve prompt'lar | **Teknoloji:** Next.js 16 + FastAPI (uv) → React/Vite varsayımı güncellenir. Ekran kimlikleri → ekran kodları ve `data-tour` hedefleri. Mercek sohbet API'si (`/api/mercek/chat`). Joyride v3 hazır olduğu için M1.5 küçülür. **Dağıtım:** Next.js + FastAPI'nin App Service'e nasıl taşınacağına karar verilmeli. |
| Sunum ve taslak ekranlar | Problem slaytı, demo slaytı, mockup'lar (iç uygulama ekranlarıyla yeniden) |
| Takım anlatım cümleleri | 2. ve 3. cümle |

---

## 5. Onay gereken kararlar

1. **Senaryo seti:** Önerim A + B + C + D canlı, E ve F yedek. Değişiklik var mı?
2. ~~Sahne 2b'deki hata~~ **Karar verildi:** HSPTVDSZ IBAN kontrol hanesi hatası. KRTTBASV sınır değer hatası yedek.
3. **Mercek'in incelediği kod:** `sample-codebase/` altındaki kopya (önerim, uygulama doğru kalır) mı, uygulamanın kendi kodu mu?
4. **Mercek'e giriş:** Ekran kodu çubuğunda "Sorun yaşıyorum" butonu ile bağlamlı yan panel + ayrı Mercek sohbet sayfası (önerim) mi, yalnızca sohbet sayfası mı?
5. ~~Maliyet modeli~~ **Karar verildi:** Ücret hesaplanmaz; tahmin yalnızca **adam-gün** ve takvim. Teknoloji tarafı **servis** bazlı anlatılır (ana servis / etkileşimli servis).
6. **Demo kullanıcıları:** Faz 3'teki Mehmet (müşteri), Eyüp (L2) ve Ayşe (analist) kullanılır; sahte kullanıcı listesine üç kişi eklenir: **Elif** (şube müşteri temsilcisi, Senaryo A), **Zeynep** (çağrı merkezi temsilcisi, Senaryo B) ve **Fatma** (Kredi Tahsilatları Bölüm Başkanlığı, Senaryo D). Uygun mu?
