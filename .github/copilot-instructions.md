# Copilot Talimatları — Ziraat Teknoloji YZ Hackathonu

Bu repo Ziraat Teknoloji Yapay Zeka Hackathonu projesidir. Çözüm AstreAI (otomatik, %30) ve jüri (%70) tarafından puanlanır. Ayrıntılı kurallar: `docs/hackathon-teknik-kilavuz.md`. Yanıtlar Türkçe, kod ve kod yorumları İngilizce olsun.

## Kesin yasaklar
- `.github/workflows/` altındaki organizasyon **CodeQL workflow dosyasını** asla düzenleme, silme, taşıma, yeniden adlandırma veya kopyalama; ikinci bir CodeQL taraması tanımlama; `.gitignore` ile `.github/` klasörünü dışlama.
- Koda, config'e, teste, örnek dosyaya veya dokümana **secret, API key, şifre, connection string, token** yazma. Bunlar ortam değişkeni, App Service ayarları veya Azure Key Vault / Managed Identity üzerinden okunur. Örnek dosyalarda yalnızca `<PLACEHOLDER>` kullan.
- Gerçek müşteri / kişisel veri kullanma; test ve demo için sentetik veri üret.

## Güvenlik (GHAS – 15 puan, kesinti geri alınmaz)
- main'e giren her CodeQL, Dependabot veya secret scanning bulgusu kalıcı puan kaybıdır. Kodu güvenli yaz: girdi doğrulama, parametreli sorgular, çıktı encoding, güvenli deserialization, güncel ve sabitlenmiş bağımlılık sürümleri.
- Bilinen açığı olan veya bakımı bırakılmış paket önerme; gereksiz bağımlılık ekleme.
- Değişiklikler feature branch + PR ile gelir; doğrudan main'e push önerme.

## Kod ve mimari (Repo Kodu – 35 puan, LLM Judge)
- Katmanlı, okunabilir mimari: sunum / iş mantığı / veri erişimi / AI entegrasyonu ayrı.
- Küçük, tek sorumluluklu fonksiyonlar; anlamlı isimler; tip bilgisi; merkezi hata yönetimi ve loglama (loglara secret yazma).
- Her yeni iş mantığı için birim testi yaz; AI çağrılarını testlerde mock'la.
- Prompt'ları koddan ayrı dosyalarda (ör. `prompts/`) tut ve sürüm kontrolüne al.
- README güncel kalsın: kurulum, çalıştırma, mimari ve **her Azure kaynağının amacı**.

## CI/CD (15 puan)
- Build/test/deploy için CodeQL'den **ayrı** bir workflow dosyası kullan (ör. `.github/workflows/ci-cd.yml`).
- Adımlar: bağımlılık kurulumu → lint → test → build → Azure App Service'e deploy. Azure kimlik doğrulaması OIDC / GitHub Secrets ile; YAML'a secret yazma.
- Son pipeline çalıştırmasının **success** olması hedeftir; workflow'u kıracak değişiklik önerme.

## Azure (15 puan)
- Kaynaklar yalnızca takımın resource group'unda.
- App Service bir sağlık endpoint'i (ör. `/health`) üzerinden HTTP 200 dönmeli.
- LLM çağrıları Azure AI Foundry'de deploy edilmiş model üzerinden yapılır.
- Yalnızca gerçekten gereken destek servislerini (AI Search, Storage vb.) öner.

## Maliyet (20 puan)
- Takım Copilot bütçesi 50 $; tam puan için toplam harcama **20 $ altı** kalmalı.
- Yanıtları kısa ve odaklı tut; istenmeyen dosyaları baştan yazma, yalnızca gerekli değişikliği yap.
- Basit işlerde (açıklama, küçük düzeltme, boilerplate) daha ucuz modelin yeterli olacağını hatırlat.

## Jüri odaklılık
- Özellikler, demoda gösterilecek somut bir problem örneğini uçtan uca çözmeli.
- AI'ın, kodun ve kuralların hangi işi yaptığı kodda ve README'de net ayrılmalı.
- Ölçülebilir iş değeri (süre, adım sayısı, doğruluk) gösterebilecek metrik/log noktalarını öner.
