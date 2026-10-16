#!/usr/bin/env python3
"""Faz 5 log üreticisinin çıktısına Mercek senaryo kayıtlarını ekler (V3).

Ne yapar:
  1. Temizlik: üreticinin rastgele ODMTFATR VALIDATION_ERROR kayıtlarını "tutar" hatası olarak işaretler,
     böylece "abone numarası" hataları yalnızca senaryodan gelir.
  2. Senaryo C (İSKİ): 1 Ekim'den bu yana 400 kayıt (13 haneli abone no, 187 farklı müşteri)
     + diğer kurumlarda 12 gerçek kullanıcı hatası → toplam 412.
  3. Mehmet (10000003): son 30 günde 3 başarılı Başkentgaz ödemesi (abone 4012345678).
  4. Senaryo B'nin "son 30 dakika" kayıtları burada YAZILMAZ; demo saatine göre demo_reset.py yazar.
     Aynı kayıtları üreten build_demo_window() fonksiyonu bu dosyadadır.

Örnek:
    python3 tools/generate_banking_logs.py --count 10000 --days 30 --seed 42 --end 2026-10-17T09:00:00+03:00
    python3 tools/mercek_data/inject_log_scenarios.py --end 2026-10-17T09:00:00+03:00
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional

TOOLS = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("generate_banking_logs", TOOLS / "generate_banking_logs.py")
gen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gen)  # type: ignore[union-attr]

TR_TZ = gen.TR_TZ
DEFAULT_INPUT = TOOLS / "output" / "dalan-banking-logs.ndjson"
DEFAULT_OUTPUT = TOOLS / "output" / "mercek-logs.ndjson"

# Senaryo sabitleri (docs/mercek-sentetik-veri-uretimi.md §4.2)
ISKI_START = datetime(2026, 10, 1, 0, 0, tzinfo=TR_TZ)
ISKI_RECORDS = 400
ISKI_CUSTOMERS = 187
OTHER_SUBSCRIBER_ERRORS = 12
ISKI_CHANNELS = [("İnternet Şube", 55), ("Mobil", 35), ("Şube", 10)]
SUBSCRIBER_MSG = "Abone numarası 6–12 haneli olmalıdır"
MEHMET = {"id": "CUS-M0003", "number": "10000003", "name": "Mehmet Yılmaz", "segment": "Bireysel",
          "age": 34, "city": "İzmir"}
MEHMET_SUBSCRIBER = "4012345678"
DEMO_WINDOW_RECORDS = 46
DEMO_WINDOW_CHANNELS = [("İnternet Şube", 45), ("Mobil", 40), ("Şube", 15)]


# ---------------------------------------------------------------------------
# Yardımcılar
# ---------------------------------------------------------------------------
def load(path: Path) -> List[Dict]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def write(records: List[Dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def sample_ts(rng: random.Random, start: datetime, end: datetime) -> datetime:
    """start–end arasında, Türkiye saatine göre gündüz ağırlıklı rastgele zaman (UTC döner)."""
    while True:
        ts = start + timedelta(seconds=rng.uniform(0, (end - start).total_seconds()))
        local = ts.astimezone(TR_TZ)
        weight = gen.HOUR_WEIGHTS[local.hour] / max(gen.HOUR_WEIGHTS)
        if local.weekday() >= 5:
            weight *= 0.6
        if rng.random() < weight:
            return ts.astimezone(timezone.utc)


def customers_from(records: List[Dict]) -> Dict[str, Dict]:
    pool: Dict[str, Dict] = {}
    for r in records:
        c = r["customer"]
        pool.setdefault(c["number"], dict(c))
    return pool


def odm_record(rng: random.Random, ts: datetime, customer: Dict, channel: str, *, institution: str,
               category: str, subscriber: str, error: Optional[Dict], amount: Optional[float],
               tx_seq: int) -> Dict:
    """ODMTFATR işlem kaydı (üreticiyle aynı ECS alanları)."""
    rec = gen.base_record(rng, ts, "ODMTFATR", customer, channel)
    day = ts.astimezone(TR_TZ).strftime("%Y%m%d")
    bill = {"category": category, "institution": institution, "subscriber_no": subscriber,
            "subscriber_no_len": len(subscriber), "bill_count": 1}
    if error is None:
        rec.update({
            "log.level": "info",
            "message": f"ODMTFATR Fatura ödendi: {institution} {gen.tl(amount)}",
            "event": {"kind": "event", "action": "transaction.complete", "outcome": "success",
                      "duration": gen.ms_lognormal(rng, 650) * 1_000_000},
            "http": {"request": {"method": "POST"}, "response": {"status_code": 200}},
            "transaction": {"id": f"ODM-{day}-9{tx_seq:05d}", "result": "success"},
        })
        rec["amount"] = {"value": amount, "currency": "TRY"}
    else:
        status = 504 if error["code"] == "INSTITUTION_TIMEOUT" else 422
        dur = gen.ms_lognormal(rng, 8000, 0.15) if status == 504 else gen.ms_lognormal(rng, 300)
        rec.update({
            "log.level": "warn",
            "message": f"ODMTFATR {error['message']}",
            "event": {"kind": "event", "action": "transaction.complete", "outcome": "failure",
                      "duration": dur * 1_000_000},
            "http": {"request": {"method": "POST"}, "response": {"status_code": status}},
            "transaction": {"id": f"ODM-{day}-9{tx_seq:05d}", "result": "rejected"},
            "error": dict(error),
        })
    rec["url"] = {"path": "/api/odm/payments"}
    rec["banking"] = {"bill": bill}
    return rec


# ---------------------------------------------------------------------------
# 1. Temizlik
# ---------------------------------------------------------------------------
def normalize(records: List[Dict]) -> int:
    changed = 0
    for r in records:
        if r["screen"]["code"] != "ODMTFATR":
            continue
        bill = r.get("banking", {}).get("bill")
        if bill:
            bill["subscriber_no_len"] = len(bill["subscriber_no"])
            if bill["institution"] == "İSKİ" and len(bill["subscriber_no"]) >= 13:
                raise ValueError("Üretici 13 haneli İSKİ numarası üretmiş; yasak kural ihlali")
        err = r.get("error")
        if err and err["code"] == "VALIDATION_ERROR":
            err["field"] = "amount"
            err["message"] = "Fatura tutarı doğrulanamadı"
            r["message"] = "ODMTFATR Fatura tutarı doğrulanamadı"
            changed += 1
    return changed


# ---------------------------------------------------------------------------
# 2. Senaryo C: İSKİ 13 hane
# ---------------------------------------------------------------------------
def iski_records(rng: random.Random, pool: Dict[str, Dict], end: datetime, seq_start: int) -> List[Dict]:
    numbers = sorted(pool)
    chosen = rng.sample(numbers, ISKI_CUSTOMERS)
    attempts = {n: 1 for n in chosen}
    remaining = ISKI_RECORDS - ISKI_CUSTOMERS
    while remaining:
        n = rng.choice(chosen)
        if attempts[n] < 5:
            attempts[n] += 1
            remaining -= 1
    out = []
    seq = seq_start
    error = {"code": "VALIDATION_ERROR", "message": SUBSCRIBER_MSG, "type": "business", "field": "subscriber_no"}
    for n in chosen:
        customer = pool[n]
        subscriber = "1" + "".join(str(rng.randint(0, 9)) for _ in range(12))  # 13 hane
        channel = gen.weighted(rng, ISKI_CHANNELS)
        first = sample_ts(rng, ISKI_START, end)
        for k in range(attempts[n]):
            ts = first if k == 0 else min(first + timedelta(minutes=rng.uniform(1, 72 * 60)),
                                          end - timedelta(minutes=1))
            ch = channel if rng.random() < 0.8 else gen.weighted(rng, ISKI_CHANNELS)
            seq += 1
            out.append(odm_record(rng, ts, customer, ch, institution="İSKİ", category="Su",
                                  subscriber=subscriber, error=error, amount=None, tx_seq=seq))
    return out


def other_subscriber_errors(rng: random.Random, pool: Dict[str, Dict], exclude: set, end: datetime,
                            seq_start: int) -> List[Dict]:
    """Gerçek kullanıcı hataları: 4–5 hane ya da harf içeren numara (İSKİ dışı kurumlar)."""
    numbers = [n for n in sorted(pool) if n not in exclude]
    institutions = [(cat, inst) for cat, items in gen.BILLS.items() for inst in items if inst != "İSKİ"]
    error = {"code": "VALIDATION_ERROR", "message": SUBSCRIBER_MSG, "type": "business", "field": "subscriber_no"}
    out = []
    for i in range(OTHER_SUBSCRIBER_ERRORS):
        cat, inst = rng.choice(institutions)
        if i % 2 == 0:
            sub = "".join(str(rng.randint(0, 9)) for _ in range(rng.choice([4, 5])))
        else:
            digits = [str(rng.randint(0, 9)) for _ in range(10)]
            digits[rng.randint(2, 8)] = rng.choice("ABCDEOS")
            sub = "".join(digits)
        ts = sample_ts(rng, ISKI_START, end)
        out.append(odm_record(rng, ts, pool[rng.choice(numbers)], gen.weighted(rng, gen.CHANNELS),
                              institution=inst, category=cat, subscriber=sub, error=error, amount=None,
                              tx_seq=seq_start + i + 1))
    return out


# ---------------------------------------------------------------------------
# 3. Mehmet'in geçmiş ödemeleri
# ---------------------------------------------------------------------------
def mehmet_payments(rng: random.Random, end: datetime, seq_start: int) -> List[Dict]:
    out = []
    for i, days_ago in enumerate((27, 18, 6)):
        day = (end - timedelta(days=days_ago)).astimezone(TR_TZ)
        ts = day.replace(hour=rng.choice([10, 13, 20]), minute=rng.randint(0, 59), second=rng.randint(0, 59))
        out.append(odm_record(rng, ts.astimezone(timezone.utc), MEHMET, "İnternet Şube",
                              institution="Başkentgaz", category="Doğalgaz", subscriber=MEHMET_SUBSCRIBER,
                              error=None, amount=round(rng.uniform(380, 920), 2), tx_seq=seq_start + i + 1))
    return out


# ---------------------------------------------------------------------------
# 4. Senaryo B: demo penceresi (demo_reset.py kullanır)
# ---------------------------------------------------------------------------
def build_demo_window(now: datetime, pool: Dict[str, Dict], seed: int = 7) -> List[Dict]:
    """now − 30 dk … now − 1 dk arasına 46 Başkentgaz INSTITUTION_TIMEOUT kaydı (Mehmet'inki 47. olur)."""
    rng = random.Random(seed)
    numbers = rng.sample(sorted(pool), DEMO_WINDOW_RECORDS)
    error = {"code": "INSTITUTION_TIMEOUT", "message": "Kurumdan yanıt alınamadı", "type": "business"}
    out = []
    for i, n in enumerate(numbers):
        ts = now - timedelta(minutes=30) + timedelta(seconds=rng.uniform(0, 29 * 60))
        customer = pool[n]
        sub = gen.subscriber_no(rng, {"subscriptions": {}}, "Başkentgaz")
        out.append(odm_record(rng, ts.astimezone(timezone.utc), customer, gen.weighted(rng, DEMO_WINDOW_CHANNELS),
                              institution="Başkentgaz", category="Doğalgaz", subscriber=sub, error=error,
                              amount=None, tx_seq=50000 + i))
    out.sort(key=lambda r: r["@timestamp"])
    return out


# ---------------------------------------------------------------------------
# Özet ve kontrol
# ---------------------------------------------------------------------------
def summarize(records: List[Dict]) -> Dict:
    since = ISKI_START.astimezone(timezone.utc)
    sub_err = [r for r in records if r["screen"]["code"] == "ODMTFATR" and r.get("error", {}).get("field") == "subscriber_no"
               and parse_ts(r["@timestamp"]) >= since]
    iski = [r for r in sub_err if r["banking"]["bill"]["institution"] == "İSKİ"]
    iski_before_13 = [r for r in records if r.get("banking", {}).get("bill", {}).get("institution") == "İSKİ"
                      and r["banking"]["bill"]["subscriber_no_len"] >= 13 and parse_ts(r["@timestamp"]) < since]
    return {
        "total": len(records),
        "subscriber_errors_since_oct1": len(sub_err),
        "iski": len(iski),
        "iski_share_pct": round(100 * len(iski) / max(1, len(sub_err)), 1),
        "iski_all_13": all(r["banking"]["bill"]["subscriber_no_len"] == 13 for r in iski),
        "iski_customers": len({r["customer"]["number"] for r in iski}),
        "iski_13_before_oct1": len(iski_before_13),
        "subscriber_errors_total": sum(1 for r in records if r.get("error", {}).get("field") == "subscriber_no"),
        "mehmet_payments": sum(1 for r in records if r["customer"]["number"] == "10000003"),
    }


def run(input_path: Path, output_path: Path, end: datetime, seed: int) -> Dict:
    rng = random.Random(seed)
    records = load(input_path)
    normalize(records)
    pool = customers_from(records)
    c_records = iski_records(rng, pool, end, seq_start=10000)
    used = {r["customer"]["number"] for r in c_records}
    c_records += other_subscriber_errors(rng, pool, used, end, seq_start=20000)
    records += c_records
    records += mehmet_payments(rng, end, seq_start=30000)
    records.sort(key=lambda r: r["@timestamp"])
    write(records, output_path)
    summary = summarize(records)
    expected = {"subscriber_errors_since_oct1": 412, "iski": 400, "iski_all_13": True,
                "iski_customers": 187, "iski_13_before_oct1": 0, "subscriber_errors_total": 412,
                "mehmet_payments": 3}
    wrong = {k: (summary[k], v) for k, v in expected.items() if summary[k] != v}
    if wrong:
        raise AssertionError(f"Senaryo değerleri tutmuyor (bulunan, beklenen): {wrong}")
    return summary


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Faz 5 loglarına Mercek senaryo kayıtlarını ekler.")
    p.add_argument("--input", default=str(DEFAULT_INPUT))
    p.add_argument("--output", default=str(DEFAULT_OUTPUT))
    p.add_argument("--end", default="2026-10-17T09:00:00+03:00", help="Veri bitiş zamanı (üreticiyle aynı)")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--demo-window-now", help="Yerel deneme: verilen zamana göre B'nin 46 kaydını ayrı dosyaya yaz")
    args = p.parse_args(argv)

    end = gen.parse_end(args.end)
    summary = run(Path(args.input), Path(args.output), end, args.seed)
    print(f"{summary['total']} kayıt yazıldı: {args.output}")
    print(f"C · abone no hatası (1 Ekim sonrası): {summary['subscriber_errors_since_oct1']} · İSKİ {summary['iski']} "
          f"(%{summary['iski_share_pct']}) · hepsi 13 hane: {summary['iski_all_13']} · "
          f"farklı müşteri {summary['iski_customers']} · 1 Ekim öncesi 13 hane: {summary['iski_13_before_oct1']}")
    print(f"Mehmet'in ödemeleri: {summary['mehmet_payments']}")
    if args.demo_window_now:
        now = gen.parse_end(args.demo_window_now)
        window = build_demo_window(now, customers_from(load(Path(args.output))))
        out = Path(args.output).with_name("mercek-demo-window.ndjson")
        write(window, out)
        print(f"B · demo penceresi: {len(window)} kayıt → {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
