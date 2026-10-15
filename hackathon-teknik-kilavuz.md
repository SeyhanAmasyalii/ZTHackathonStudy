# Ziraat Teknoloji Yapay Zeka Hackathonu — Teknik Kılavuz Özeti

Kaynak: Katılımcı Teknik Kılavuzu (Nephos AI / Microsoft). Takımımız: 5 kişi → Copilot bütçesi 50 $.

## Genel puan
- **AstreAI teknik değerlendirme: %30** (otomatik, 0–100)
- **Jüri değerlendirmesi: %70** (final sunum + demo)

## Ortam
- Tüm geliştirme atanmış **Azure sanal masaüstünde (VDI)** yapılır; makinede tam admin yetkisi, doğrudan internet.
- Kimlikler:
  - Windows App / Azure Portal / Entra: `hc_kullanici@ziraatbank.onmicrosoft.com` + kendi belirlenen şifre + MFA
  - VDI Windows oturumu: `.\hackadmin` (baştaki `.\` zorunlu)
  - GitHub: kullanıcı adı alanına `_ziraathc`, şifre boş → Microsoft girişi + MFA (EMU hesap)
- Azure kaynakları yalnızca takıma tahsis edilen **resource group** içinde oluşturulur. `az login` aynı kurumsal hesapla.
- **Kişisel GitHub hesabı kullanılmaz.** Copilot (VS Code, Copilot App veya başka IDE) mutlaka `_ziraathc` hesabıyla açık olmalı; aksi halde kullanım değerlendirmeye yansımaz.

## Etkin Copilot modelleri
GPT-5.3-Codex, Claude Haiku 4.5, Claude Haiku 5.5, Claude Opus 4.8, Claude Opus 5, Claude Opus 5.5, Claude Sonnet 5, Claude Sonnet 5.5, Gemini 3.7 Flash, Gemini 3.8 Flash, GPT-5.5, GPT-5.6 Luna/Sol/Terra, GPT-6 Astra/Luna/Sol, GPT-6.1 Sol. Geçerli liste IDE'deki model seçicidir; tüketim bilgisi orada görünür.

## AstreAI metrikleri (100 puan)

| Metrik | Puan | Yöntem |
|---|---|---|
| Repo Kodu (Kod & Mimari) | 35 | LLM Judge rubriği: mimari, güvenlik, test, kod kalitesi |
| GHAS | 15 | Açık bulgu başına puan kırma |
| CI/CD | 15 | 5 AI (workflow kalitesi) + 5 (en az bir kez çalıştı) + 5 (son çalıştırma success) |
| Azure Ortamı & Runtime | 15 | Web App sağlık 5, AI Foundry kaynağı 3, model deploy 3, destek servisleri 4 |
| LLM Kullanım Maliyeti | 20 | Takım harcama bandı |

### GHAS kuralları (kritik)
- Kesinti: Critical −2, High −1, Medium −0,5, Low −0,25 (açık bulgu başına; 0'ın altına inmez).
- **Kesinti geri alınmaz:** main'de bir kez tespit edilen bulgu sonradan düzeltilse de ceza kalır. → Güvenlik açıkları main'e girmeden (PR/feature branch'te) giderilmeli.
- CodeQL, Dependabot ve secret scanning sayılır. Repo'ya asla secret/API key/connection string girmez.
- `.github/workflows/` içindeki organizasyon CodeQL dosyasına **dokunulmaz**: düzenleme, silme, taşıma, yeniden adlandırma, ikinci CodeQL tanımı, workflow'u disable etme, `.gitignore` ile dışlama YASAK.

### CI/CD
- Kendi build/test/deploy workflow'umuz **CodeQL dosyasından ayrı** bir dosya olmalı.
- Değerlendirme öncesi son pipeline çalıştırması **success** olmalı.

### Azure Ortamı
- App Service HTTP sağlık kontrolüne 200 dönmeli.
- Azure AI Foundry kaynağı + en az bir deploy edilmiş, erişilebilir model.
- Sadece gerçekten gereken destek servisleri (AI Search, Storage vb.); kullanılmayan kontrol puanı diğerlerine dağıtılır.
- README'de her Azure kaynağının amacı açıklanmalı.

### LLM maliyet bantları (5 kişi = 50 $)
| Harcama | Puan |
|---|---|
| < 20 $ (%40) | 20 |
| 20–25 $ | 15 |
| 25–30 $ | 10 |
| 30–35 $ | 5 |
| ≥ 35 $ | 0 |
→ Hedef: takım toplamı **20 $ altı** (kişi başı ~4 $). Basit işlerde ucuz modeller, pahalı modeller yalnızca zor işlerde.

## Jüri kriterleri (%70, her biri 1–10)
| Kriter | Ağırlık | Nasıl cevaplanır |
|---|---|---|
| Yenilikçilik | %10 | Mevcut çözümlerden fark, AI'ın neyi mümkün kıldığı |
| Probleme Uygunluk | %10 | Somut problem örneği → demoda aynı örneğin çözümü |
| **İş Değeri ve Etki** | **%20** | Önce/sonra; süre, adım, iş gücü, doğruluk; varsayımlar açık |
| Kullanıcı Deneyimi | %10 | Hedef kullanıcı + akış |
| Ürün Çalışırlığı | %10 | Azure'da çalışan uygulama üzerinden temel işlevler |
| Sunum | %10 | Problem → çözüm → demo → iş değeri; prova |

## Sunum (5 dakika, .pptx 16:9)
Önerilen akış: 1 Kapak (takım + proje adı) · 2 Takım (ad, birim, rol) · 3 Problem · 4 Çözüm & hedef kullanıcı · 5 Yenilikçilik · 6 Mimari (Web App, Foundry modeli, veri katmanı, Azure servisleri, CI/CD) · 7 Kullanıcı deneyimi · 8 Demo (canlı/video) · 9 İş değeri · 10 Sonuçlar & sonraki adımlar · 11 Ekler (repo, Web App URL, demo video).
- Az metin, çok görsel; her slayt tek mesaj.
- AI'ın / kodun / kuralların hangi işi yaptığı net.
- Şifre, API key, connection string, gerçek müşteri verisi görünmez.
- Yedek demo videosu hazır.
- S-C hazırlığı: kim/ne sıklıkla kullanır, canlıya geçiş, AI yanlış sonuç üretirse ne olur, çalışma maliyeti.

## Teslim öncesi kontrol listesi
- [ ] Herkes VDI, Azure Portal, GitHub'a kurumsal hesapla girebiliyor; IDE'lerde sadece `_ziraathc`
- [ ] Sadece etkin listedeki modeller kullanıldı
- [ ] Kod, testler, promptlar, dokümanlar, workflow ve config şablonları main'de
- [ ] Repo'da secret / gerçek kişisel veri yok
- [ ] CodeQL dosyası sağlam ve aktif; Security sekmesi incelendi
- [ ] Build/test/deploy workflow en az bir kez çalıştı, son çalıştırma success
- [ ] App Service HTTP 200; Foundry + model deploy; destek servisleri README'de
- [ ] Copilot harcaması izlendi (hedef < 20 $)
- [ ] Sunum: kapak, takım, mimari, ekran görüntüleri + demo videosu, her jüri sorusuna cevap, gizli bilgi yok, prova yapıldı
