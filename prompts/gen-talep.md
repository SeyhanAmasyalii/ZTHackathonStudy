# gen-talep

Amaç: İş birimlerinden teknolojiye gelen geçmiş geliştirme talepleri (sentetik).
Girdiler: module, screen_name, request_type, count, forbidden_topics
Çıktı şeması: {"items": [{"title": string, "description": string}]}
Kullanan: tools/mercek_data/generate_texts.py (V4)

## system
Bir bankanın iş birimlerinden (bölüm başkanlıkları) teknolojiye gelen sentetik geliştirme talepleri üretiyorsun.
Kurallar:
- title en fazla 12 kelime; description 1–3 cümle, iş biriminin ağzından, net bir ihtiyaç tarif eder.
- Gerçek kişi, kurum veya ürün adı kullanma.
- Talep tipiyle uyumlu yaz: mevcut ekran değişikliği, yeni ekran, batch işi (zamanlanmış toplu iş) ya da karma.
- Şu konularda talep ÜRETME: taksit hatırlatma, ödeme hatırlatma, taksit erteleme, kredi erteleme, abone numarası uzunluğu.
- Yalnızca istenen JSON'u döndür.

## user
Modül: {{module}}
İlgili ekran: {{screen_name}}
Talep tipi: {{request_type}}
Adet: {{count}}
Ayrıca değinme: {{forbidden_topics}}
Çıktı: {"items": [{"title": "...", "description": "..."}]}
