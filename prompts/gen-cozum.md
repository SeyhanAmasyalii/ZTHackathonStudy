# gen-cozum

Amaç: Çözüm bilgi bankası kayıtları (L2 destek ve geliştirme için).
Girdiler: error_code, error_hint, service_name, screen_code, count, avoid_root_causes
Çıktı şeması: {"items": [{"title": string, "symptom": string, "root_cause": string, "steps": [string]}]}
Kullanan: tools/mercek_data/generate_texts.py (V4)

## system
Bankacılık uygulaması için sentetik çözüm bilgi bankası kaydı üretiyorsun. Kayıtlar L2 destek ve geliştirme ekipleri içindir: kısa, teknik ve uygulanabilir.
Kurallar:
- title en fazla 10 kelime; symptom ve root_cause birer cümle; steps 3–5 kısa adım.
- Sunucu adı, IP, şifre, kişi adı veya gerçek sistem adı uydurma.
- Abone numarası uzunluğu, hane sayısı veya abone numarası formatıyla ilgili kayıt ÜRETME.
- Her kayıt farklı bir kök nedene dayansın.
- Yalnızca istenen JSON'u döndür.

## user
Hata kodu: {{error_code}}
Kuralın açıklaması: {{error_hint}}
Servis: {{service_name}}
Ekran: {{screen_code}}
Adet: {{count}}
Şu kök nedenleri kullanma (başka kayıtlarda var): {{avoid_root_causes}}
Çıktı: {"items": [{"title": "...", "symptom": "...", "root_cause": "...", "steps": ["...", "..."]}]}
