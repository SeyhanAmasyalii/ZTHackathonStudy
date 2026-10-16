# tools/ — Sentetik veri betikleri

Ayrıntılı açıklama: [`docs/mercek-sentetik-veri-kaynaklari.md`](../docs/mercek-sentetik-veri-kaynaklari.md).

## Hazır betikler (V3–V6)

| Betik | Ne yapar | Çıktı |
|---|---|---|
| `generate_banking_logs.py` | 5 bankacılık ekranı için Kibana (ECS) uyumlu sentetik işlem logu (rebuild Faz 5) | `output/dalan-banking-logs.ndjson` |
| `mercek_data/generate_texts.py` | Çağrı notu, çözüm ve talep metinleri; Foundry veya `--template` (çevrimdışı) | `../data/seed/texts.json` |
| `mercek_data/generate_portfolio.py` | 40.000 müşteri, 33.000 kredi; D ve E'nin kesin rakamları; etkilenen illeri katalogda işaretler | `../data/out/customers.csv`, `loans.csv` |
| `mercek_data/generate_incidents.py` | Müşteri temasları, teknoloji çağrı kayıtları (CAG-0651…2050), çözüm bilgi bankası; B, C, D, E kesin | `../data/out/contacts.csv`, `incidents.csv`, `solutions.csv` |
| `mercek_data/generate_requests.py` | Geçmiş talepler (D ve E'nin benzer talepleri kesin); `--eval` ile değerlendirme seti | `../data/out/requests.csv`, `../data/seed/eval_cases.json` |
| `mercek_data/inject_log_scenarios.py` | Üretici çıktısına senaryo kayıtlarını ekler (C: 412 abone no hatası; Mehmet'in ödemeleri); B'nin demo penceresi için `build_demo_window()` | `output/mercek-logs.ndjson` |

Yalnızca standart kütüphane, Python 3.9+ (Foundry'de anahtar yoksa isteğe bağlı `azure-identity`).

```bash
python3 tools/generate_banking_logs.py --count 10000 --days 30 --seed 42 --end 2026-10-17T09:00:00+03:00
python3 tools/mercek_data/inject_log_scenarios.py --end 2026-10-17T09:00:00+03:00
python3 tools/mercek_data/generate_texts.py --template --force
python3 tools/mercek_data/generate_portfolio.py
python3 tools/mercek_data/generate_incidents.py
python3 tools/mercek_data/generate_requests.py --eval
python3 -m pytest tools/mercek_data/tests -q
```

## Üretici parametreleri

| Parametre | Varsayılan | Açıklama |
|---|---|---|
| `--count` | 10000 | Kayıt sayısı |
| `--days` | 30 | Kaç güne yayılacağı |
| `--seed` | 42 | Aynı seed ve `--end` → birebir aynı çıktı |
| `--customers` | 800 | Müşteri havuzu |
| `--format` | ndjson | `bulk`: Elasticsearch `_bulk` biçimi |
| `--index` | dalan-banking-logs | Index adı (dosya adını da belirler) |
| `--output` | `output/<index>.ndjson` | Çıktı yolu |
| `--end` | şimdi | Verinin bitiş zamanı (Mercek: `2026-10-17T09:00:00+03:00`) |
| `--write-template` | — | Index template JSON'ını da yazar |

## Kibana'ya yükleme (isteğe bağlı)

Mercek logları Azure SQL'den okur; Kibana gerekmez. Kibana'da görmek isterseniz:
1. `--write-template --format bulk` ile üretin.
2. `PUT _index_template/dalan-banking-logs` (template dosyası), ardından `POST _bulk` (bulk dosyası).
3. Data view: `dalan-banking-logs*`, zaman alanı `@timestamp`.

Ayrıntı: rebuild rehberi Faz 6 (`KIBANA_AZURE_ROADMAP.md`).
