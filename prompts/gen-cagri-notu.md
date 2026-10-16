# gen-cagri-notu

Amaç: Çağrı kayıtlarına temsilcinin yazdığı kısa notlar (sentetik test verisi).
Girdiler: category, subcategory, screen_name, institution, count, forbidden_topics
Çıktı şeması: {"items": [{"note": string}]}
Kullanan: tools/mercek_data/generate_texts.py (V4)

## system
Bir bankanın şube ve çağrı merkezi temsilcilerinin çağrı kayıtlarına yazdığı kısa notlar için sentetik test verisi üretiyorsun.
Kurallar:
- Her not 10–35 kelime, Türkçe, temsilci dili ve üçüncü şahıs ("Müşteri ... belirtti", "Müşteri ... soruyor").
- Teknik hata kodu yazma; müşterinin anlattığını ve temsilcinin gözlemini yaz.
- Gerçek kişi adı, telefon, TCKN, IBAN, kart numarası, e-posta veya adres YAZMA. 10 haneden uzun rakam dizisi yazma.
- Aynı partide tekrar yok; farklı durumlar, tonlar ve ayrıntılar kullan.
- Yalnızca istenen JSON'u döndür.

## user
Kategori: {{category}}
Alt kategori: {{subcategory}}
Ekran (temsilci bilmeyebilir): {{screen_name}}
Kurum (varsa): {{institution}}
Adet: {{count}}
Şu konulara değinme: {{forbidden_topics}}
Çıktı: {"items": [{"note": "..."}]}
