#!/usr/bin/env python3
"""Bankacılık ekranları için Kibana (ECS) uyumlu sentetik işlem logu üretici.

Rebuild rehberi Faz 5'e göre yazılmıştır. Yalnızca standart kütüphane kullanır, Python 3.9+ ile çalışır.
Tüm veriler sentetiktir; gerçek kişi, kurum hesabı veya banka verisi içermez.

Örnek:
    python3 tools/generate_banking_logs.py --count 10000 --days 30 --seed 42 --format ndjson \
        --end 2026-10-17T09:00:00+03:00
"""
from __future__ import annotations

import argparse
import json
import math
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional

TR_TZ = timezone(timedelta(hours=3))
DEFAULT_INDEX = "dalan-banking-logs"
SERVICE = {"name": "dalan-banking", "environment": "demo", "version": "1.4.0"}

# ---------------------------------------------------------------------------
# Referans veriler
# ---------------------------------------------------------------------------
MODULES = {
    "KRT": "Kartlar",
    "KRD": "Krediler",
    "ODM": "Ödemeler",
    "MUS": "Müşteri",
    "HSP": "Hesaplar",
}
# kod: (ad, ağırlık, medyan süre ms, işlem API yolu)
SCREENS = {
    "ODMTFATR": ("Fatura Ödeme", 35, 650, "/api/odm/payments"),
    "HSPTVDSZ": ("Vadesiz Hesap Açılışı", 18, 950, "/api/hsp/accounts"),
    "KRTTBASV": ("Kredi Kartı Başvurusu", 16, 850, "/api/krt/applications"),
    "KRDTKULL": ("Bireysel Kredi Kullandırım", 16, 1200, "/api/krd/loans"),
    "MUSTGUNC": ("Müşteri Bilgi Güncelleme", 15, 400, "/api/mus/customer"),
}
CHANNELS = [("Mobil", 55), ("İnternet Şube", 25), ("Şube", 12), ("Çağrı Merkezi", 8)]
USER_AGENTS = {
    "Mobil": [
        "BankaMobil/4.2.1 (Android 14; SM-A546E)",
        "BankaMobil/4.2.1 (iOS 18.0; iPhone15,2)",
        "BankaMobil/4.1.9 (Android 13; Redmi Note 12)",
    ],
    "İnternet Şube": [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 Version/17.5 Safari/605.1.15",
    ],
    "Şube": ["SubeTerminal/2.3 (Windows 10; Kurumsal)"],
    "Çağrı Merkezi": ["CagriMerkeziKonsol/1.8 (Windows 11)"],
}
BRANCHES = ["0101", "0102", "0601", "3501"]
# il: (ağırlık, enlem, boylam)
CITIES = {
    "İstanbul": (30, 41.015, 28.979),
    "Ankara": (12, 39.933, 32.859),
    "İzmir": (9, 38.423, 27.142),
    "Bursa": (6, 40.188, 29.061),
    "Antalya": (6, 36.896, 30.713),
    "Adana": (5, 37.000, 35.321),
    "Konya": (5, 37.874, 32.493),
    "Gaziantep": (4, 37.066, 37.383),
    "Kayseri": (4, 38.734, 35.467),
    "Trabzon": (3, 41.002, 39.717),
    "Samsun": (3, 41.286, 36.330),
    "Eskişehir": (3, 39.776, 30.520),
}
SEGMENTS = [("Bireysel", 70, 32000), ("Premium", 25, 85000), ("Özel Bankacılık", 5, 250000)]
FIRST_NAMES = [
    "Ahmet", "Mehmet", "Mustafa", "Ali", "Hüseyin", "Hasan", "İbrahim", "Murat", "Emre", "Burak",
    "Can", "Deniz", "Eren", "Kaan", "Oğuz", "Serkan", "Tolga", "Umut", "Yusuf", "Cem",
    "Ayşe", "Fatma", "Emine", "Hatice", "Zeynep", "Elif", "Merve", "Esra", "Büşra", "Selin",
    "Derya", "Ebru", "Gizem", "İrem", "Melike", "Nur", "Özge", "Seda", "Tuğba", "Yasemin",
]
LAST_NAMES = [
    "Yılmaz", "Kaya", "Demir", "Şahin", "Çelik", "Yıldız", "Yıldırım", "Öztürk", "Aydın", "Özdemir",
    "Arslan", "Doğan", "Kılıç", "Aslan", "Çetin", "Kara", "Koç", "Kurt", "Özkan", "Şimşek",
    "Polat", "Erdoğan", "Güneş", "Aksoy", "Tekin", "Korkmaz", "Bulut", "Avcı", "Uçar", "Keskin",
]
OCCUPATIONS = ["Mühendis", "Öğretmen", "Memur", "Esnaf", "Muhasebeci", "Hemşire", "Satış Temsilcisi",
               "Serbest Meslek", "Teknisyen", "Avukat", "Doktor", "Şoför"]
BILLS = {
    "Elektrik": ["CK Boğaziçi Elektrik", "Enerjisa Başkent", "Gediz Elektrik"],
    "Su": ["İSKİ", "ASKİ", "İZSU"],
    "Doğalgaz": ["İGDAŞ", "Başkentgaz", "İzmirgaz"],
    "İnternet": ["Türk Telekom", "Superonline", "Turknet"],
    "GSM": ["Turkcell", "Vodafone", "Türk Telekom Mobil"],
}
CARDS = {  # ad: (tavan limit, gelir şartı, yıllık ücret)
    "Klasik": (25000, 0, 0),
    "Gold": (75000, 20000, 650),
    "Platinum": (250000, 60000, 1450),
}
LOAN_TERMS = [3, 6, 12, 18, 24, 36]
CURRENCIES = ["TRY", "USD", "EUR", "GBP", "XAU"]
# Türkiye saatine göre saatlik yoğunluk (0-23)
HOUR_WEIGHTS = [1, 0.5, 0.3, 0.2, 0.2, 0.4, 1, 3, 6, 9, 10, 10, 9, 10, 10, 9, 9, 8, 8, 9, 9, 7, 5, 2]

BUSINESS_ERRORS = {
    "INSUFFICIENT_INCOME": "Gelir, seçilen kart tipinin şartını karşılamıyor",
    "AFFORDABILITY_EXCEEDED": "Taksit tutarı gelirin %50'sini aşıyor",
    "INSUFFICIENT_BALANCE": "Hesap bakiyesi yetersiz",
    "INSTITUTION_TIMEOUT": "Kurumdan yanıt alınamadı",
    "VALIDATION_ERROR": "Girilen bilgiler doğrulanamadı",
    "KYC_CHECK_FAILED": "Kimlik doğrulaması başarısız",
}
TECHNICAL_ERRORS = {
    "CORE_BANKING_TIMEOUT": (504, "Ana bankacılık sistemi zaman aşımı"),
    "SERVICE_UNAVAILABLE": (503, "Servis geçici olarak kullanılamıyor"),
    "DB_CONNECTION_ERROR": (500, "Veritabanı bağlantı hatası"),
}
# Ekrana göre olası iş kuralı retleri ve ağırlıkları
SCREEN_BUSINESS_ERRORS = {
    "KRTTBASV": [("INSUFFICIENT_INCOME", 6), ("VALIDATION_ERROR", 3), ("KYC_CHECK_FAILED", 2)],
    "KRDTKULL": [("AFFORDABILITY_EXCEEDED", 7), ("VALIDATION_ERROR", 2), ("KYC_CHECK_FAILED", 1)],
    "ODMTFATR": [("INSUFFICIENT_BALANCE", 5), ("INSTITUTION_TIMEOUT", 2), ("VALIDATION_ERROR", 4)],
    "MUSTGUNC": [("VALIDATION_ERROR", 7), ("KYC_CHECK_FAILED", 2)],
    "HSPTVDSZ": [("VALIDATION_ERROR", 4), ("KYC_CHECK_FAILED", 4)],
}
VIEW_RATIO = 0.25
BUSINESS_ERROR_RATE = 0.12
TECHNICAL_ERROR_RATE = 0.03


# ---------------------------------------------------------------------------
# Yardımcılar
# ---------------------------------------------------------------------------
def tl(value: float) -> str:
    """Tutarı Türkçe sayı biçiminde yazar: 13500 -> '13.500 TRY', 747.71 -> '747,71 TRY'."""
    if abs(value - round(value)) < 0.005:
        text = f"{int(round(value)):,}".replace(",", ".")
    else:
        text = f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{text} TRY"


def weighted(rng: random.Random, items):
    """[(değer, ağırlık), ...] listesinden ağırlıklı seçim."""
    total = sum(w for _, w in items)
    r = rng.uniform(0, total)
    upto = 0.0
    for value, w in items:
        upto += w
        if r <= upto:
            return value
    return items[-1][0]


def mod97(digits: str) -> int:
    remainder = 0
    for ch in digits:
        remainder = (remainder * 10 + int(ch)) % 97
    return remainder


def generate_iban(rng: random.Random) -> str:
    """Simülasyon banka kodu 00999 ile ISO 13616 uyumlu TR IBAN üretir."""
    bban = "00999" + "0" + "".join(str(rng.randint(0, 9)) for _ in range(16))
    check = 98 - mod97(bban + "292700")
    return f"TR{check:02d}{bban}"


def is_valid_iban(iban: str) -> bool:
    rearranged = iban[4:] + iban[:4]
    digits = "".join(str(int(ch, 36)) for ch in rearranged)
    return mod97(digits) == 1


def monthly_rate(term: int) -> float:
    if term <= 6:
        return 0.0309
    if term <= 12:
        return 0.0329
    return 0.0349


def installment(amount: float, rate: float, term: int) -> float:
    """loanPlan ile aynı formül: efektif oran = faiz × 1,30 (KKDF %15 + BSMV %15)."""
    e = rate * 1.30
    return amount * e / (1 - (1 + e) ** -term)


def ms_lognormal(rng: random.Random, median_ms: float, sigma: float = 0.45) -> int:
    return max(20, int(rng.lognormvariate(math.log(median_ms), sigma)))


# ---------------------------------------------------------------------------
# Müşteri havuzu
# ---------------------------------------------------------------------------
def build_customers(rng: random.Random, count: int) -> List[Dict]:
    numbers = rng.sample(range(10000101, 10040101), count)
    customers = []
    for i, number in enumerate(numbers):
        segment = weighted(rng, [(s, w) for s, w, _ in SEGMENTS])
        median_income = next(m for s, _, m in SEGMENTS if s == segment)
        age = rng.randint(19, 75)
        if age >= 62:
            occupation = "Emekli"
        elif age <= 24 and rng.random() < 0.7:
            occupation = "Öğrenci"
        else:
            occupation = rng.choice(OCCUPATIONS)
        income = int(rng.lognormvariate(math.log(median_income), 0.45))
        if occupation == "Öğrenci":
            income = int(income * 0.35)
        city = weighted(rng, [(c, v[0]) for c, v in CITIES.items()])
        customers.append({
            "id": f"CUS-{i + 1:05d}",
            "number": str(number),
            "name": f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}",
            "segment": segment,
            "age": age,
            "city": city,
            "occupation": occupation,
            "monthly_income": max(income, 8500),
            "activity": rng.paretovariate(1.4),
            "subscriptions": {},
        })
    return customers


def subscriber_no(rng: random.Random, customer: Dict, institution: str) -> str:
    """Müşteri + kurum için kalıcı abone numarası (6–12 hane; çoğunlukla 10–12)."""
    subs = customer["subscriptions"]
    if institution not in subs:
        length = weighted(rng, [(8, 1), (9, 1), (10, 4), (11, 3), (12, 3)])
        first = str(rng.randint(1, 9))
        subs[institution] = first + "".join(str(rng.randint(0, 9)) for _ in range(length - 1))
    return subs[institution]


# ---------------------------------------------------------------------------
# Zaman
# ---------------------------------------------------------------------------
def build_timestamps(rng: random.Random, count: int, days: int, end: datetime) -> List[datetime]:
    """Türkiye saatine göre gece düşük, gündüz yüksek; hafta sonu %40 az. UTC döner."""
    end_tr = end.astimezone(TR_TZ)
    start_day = (end_tr - timedelta(days=days)).date()
    day_slots = []
    for d in range(days + 1):
        day = start_day + timedelta(days=d)
        weight = 0.6 if day.weekday() >= 5 else 1.0
        for hour in range(24):
            slot_start = datetime(day.year, day.month, day.day, hour, tzinfo=TR_TZ)
            if slot_start >= end_tr:
                continue
            day_slots.append((slot_start, weight * HOUR_WEIGHTS[hour]))
    stamps = []
    total = sum(w for _, w in day_slots)
    cumulative = []
    acc = 0.0
    for slot, w in day_slots:
        acc += w
        cumulative.append((acc, slot))
    for _ in range(count):
        r = rng.uniform(0, total)
        lo, hi = 0, len(cumulative) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            if cumulative[mid][0] < r:
                lo = mid + 1
            else:
                hi = mid
        slot = cumulative[lo][1]
        ts = slot + timedelta(seconds=rng.uniform(0, 3600))
        if ts >= end_tr:
            ts = end_tr - timedelta(seconds=rng.uniform(1, 600))
        stamps.append(ts.astimezone(timezone.utc))
    stamps.sort()
    return stamps


def iso(ts: datetime) -> str:
    return ts.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.") + f"{ts.microsecond // 1000:03d}Z"


# ---------------------------------------------------------------------------
# Ekran işlemleri: (açıklama, banking detayı, tutar) üretir; iş kuralı reddini tutarlı kurar
# ---------------------------------------------------------------------------
def tx_card(rng, c, error):
    income = c["monthly_income"]
    if error == "INSUFFICIENT_INCOME":
        options = [k for k, v in CARDS.items() if v[1] > income]
        if not options:
            return None
        card = rng.choice(options)
    else:
        card = rng.choice([k for k, v in CARDS.items() if v[1] <= income])
    cap, required, fee = CARDS[card]
    requested = int(rng.choice([5000, 10000, 15000, 20000, 30000, 50000, 75000, 100000, 150000]))
    approved = int(min(requested, income * 3, cap) // 500 * 500)
    detail = {"card": {"product": card, "requested_limit": requested, "monthly_income": income,
                       "income_requirement": required, "annual_fee": fee,
                       "statement_day": rng.choice([1, 5, 10, 15, 20, 25])}}
    if error == "INSUFFICIENT_INCOME":
        return f"{card} kart başvurusu reddedildi: gelir şartı {tl(required)}", detail, requested
    if error is None:
        detail["card"]["approved_limit"] = approved
        result = "kısmi onay" if approved < requested else "onaylandı"
        return f"{card} kart başvurusu {result}: limit {tl(approved)}", detail, approved
    return f"{card} kart başvurusu", detail, requested


def tx_loan(rng, c, error):
    income = c["monthly_income"]
    term = rng.choice(LOAN_TERMS)
    rate = monthly_rate(term)
    max_ok = income * 0.5 / installment(1, rate, term)
    if error == "AFFORDABILITY_EXCEEDED":
        low = max(5000, max_ok * 1.05)
        if low > 500000:
            low = 500000
        amount = round(rng.uniform(low, min(500000, max(low * 1.8, low + 5000))) / 1000) * 1000
        if installment(amount, rate, term) <= income * 0.5:
            amount = 500000
            term = 3
            rate = monthly_rate(term)
            if installment(amount, rate, term) <= income * 0.5:
                return None  # gelir çok yüksek: bu müşteride kural ihlali kurulamaz
    else:
        upper = max(5000, min(500000, max_ok))
        amount = round(rng.uniform(5000, upper) / 1000) * 1000
        amount = max(5000, min(amount, int(max_ok // 1000 * 1000) or 5000))
    inst = installment(amount, rate, term)
    detail = {"loan": {"amount": amount, "term": term, "monthly_rate": rate,
                       "installment": round(inst, 2), "monthly_income": income,
                       "debt_to_income": round(inst / income, 4)}}
    if error == "AFFORDABILITY_EXCEEDED":
        return (f"Taksit tutarı gelirin %50'sini aşıyor: taksit {tl(round(inst, 2))}, "
                f"gelir {tl(income)}"), detail, amount
    if error is None:
        return f"{tl(amount)} kredi kullandırıldı, {term} ay, taksit {tl(round(inst, 2))}", detail, amount
    return f"{tl(amount)} kredi kullandırım", detail, amount


def tx_bill(rng, c, error):
    category = rng.choice(list(BILLS))
    institution = rng.choice(BILLS[category])
    sub = subscriber_no(rng, c, institution)
    amount = round(rng.uniform(150, 2000), 2)
    detail = {"bill": {"category": category, "institution": institution, "subscriber_no": sub,
                       "subscriber_no_len": len(sub), "bill_count": rng.choice([1, 1, 1, 2, 3])}}
    if error is None:
        return f"Fatura ödendi: {institution} {tl(amount)}", detail, amount
    return f"{institution} fatura ödemesi", detail, amount


def tx_customer(rng, c, error):
    fields = rng.sample(["email", "mobile_phone", "address", "income", "occupation", "permissions"],
                        k=rng.randint(1, 3))
    detail = {"customer_update": {"changed_fields": fields}}
    if error is None:
        return f"Müşteri bilgileri güncellendi: {', '.join(fields)}", detail, None
    return "Müşteri bilgi güncelleme", detail, None


def tx_account(rng, c, error):
    currency = weighted(rng, [("TRY", 70), ("USD", 12), ("EUR", 10), ("GBP", 3), ("XAU", 5)])
    branch = weighted(rng, [("9999", 60)] + [(b, 10) for b in BRANCHES])
    detail = {"account": {"currency": currency, "branch_code": branch}}
    if error is None:
        iban = generate_iban(rng)
        detail["account"]["iban"] = iban
        return f"{currency} vadesiz hesap açıldı: {iban[:4]} **** {iban[-4:]}", detail, None
    return f"{currency} vadesiz hesap açılışı", detail, None


TX_BUILDERS = {"KRTTBASV": tx_card, "KRDTKULL": tx_loan, "ODMTFATR": tx_bill,
               "MUSTGUNC": tx_customer, "HSPTVDSZ": tx_account}


# ---------------------------------------------------------------------------
# Kayıt üretimi
# ---------------------------------------------------------------------------
def base_record(rng, ts, code, customer, channel) -> Dict:
    name, _, _, api_path = SCREENS[code]
    city = customer["city"]
    _, lat, lon = CITIES[city]
    record = {
        "@timestamp": iso(ts),
        "service": dict(SERVICE),
        "host": {"name": f"bank-app-0{rng.randint(1, 4)}"},
        "screen": {"code": code, "name": name, "module": code[:3], "module_name": MODULES[code[:3]],
                   "type": code[3]},
        "channel": channel,
        "customer": {"id": customer["id"], "number": customer["number"], "name": customer["name"],
                     "segment": customer["segment"], "age": customer["age"], "city": city},
        "client": {"ip": f"{rng.choice(['192.0.2', '198.51.100', '203.0.113'])}.{rng.randint(1, 254)}",
                   "geo": {"city_name": city, "country_iso_code": "TR",
                           "location": {"lat": round(lat + rng.uniform(-0.05, 0.05), 5),
                                        "lon": round(lon + rng.uniform(-0.05, 0.05), 5)}}},
        "user_agent": {"original": rng.choice(USER_AGENTS[channel])},
        "trace": {"id": f"{rng.getrandbits(128):032x}"},
    }
    if channel in ("Şube", "Çağrı Merkezi"):
        record["employee"] = {"id": f"E{rng.randint(1000, 9999)}"}
    if channel == "Şube":
        record["branch"] = {"code": rng.choice(BRANCHES)}
    return record


def make_view(rng, ts, code, customer, channel) -> Dict:
    rec = base_record(rng, ts, code, customer, channel)
    dur = ms_lognormal(rng, 120, 0.35)
    rec.update({
        "log.level": "info",
        "message": f"{code} ekranı görüntülendi",
        "event": {"kind": "event", "action": "screen.view", "outcome": "success", "duration": dur * 1_000_000},
        "url": {"path": f"/bankacilik/{code.lower()}"},
        "http": {"request": {"method": "GET"}, "response": {"status_code": 200}},
    })
    return rec


def make_transaction(rng, ts, code, customer, channel, seq: Dict[str, int]) -> Dict:
    rec = base_record(rng, ts, code, customer, channel)
    name, _, median_ms, api_path = SCREENS[code]
    error_code: Optional[str] = None
    error_type: Optional[str] = None
    roll = rng.random()
    if roll < TECHNICAL_ERROR_RATE:
        error_type = "technical"
        error_code = weighted(rng, [("CORE_BANKING_TIMEOUT", 5), ("SERVICE_UNAVAILABLE", 3), ("DB_CONNECTION_ERROR", 2)])
    elif roll < TECHNICAL_ERROR_RATE + BUSINESS_ERROR_RATE:
        error_type = "business"
        error_code = weighted(rng, SCREEN_BUSINESS_ERRORS[code])

    built = TX_BUILDERS[code](rng, customer, error_code if error_type == "business" else None)
    if built is None:  # kural bu müşteri için tutarlı kurulamadı (ör. gelir zaten yüksek)
        error_code = "VALIDATION_ERROR"
        built = TX_BUILDERS[code](rng, customer, error_code)
    desc, detail, amount = built

    day = ts.astimezone(TR_TZ).strftime("%Y%m%d")
    seq[code[:3]] = seq.get(code[:3], 0) + 1
    tx_id = f"{code[:3]}-{day}-{seq[code[:3]]:06d}"

    if error_type == "technical":
        status, err_msg = TECHNICAL_ERRORS[error_code]
        dur = ms_lognormal(rng, 12000, 0.35) if error_code == "CORE_BANKING_TIMEOUT" else ms_lognormal(rng, median_ms)
        if error_code == "CORE_BANKING_TIMEOUT":
            dur = min(max(dur, 5000), 30000)
        level, outcome, message = "error", "failure", f"{code} {err_msg}"
        error = {"code": error_code, "message": err_msg, "type": "technical"}
        result = "error"
    elif error_type == "business":
        status = 422
        dur = ms_lognormal(rng, median_ms)
        err_msg = BUSINESS_ERRORS[error_code]
        if error_code in ("INSUFFICIENT_INCOME", "AFFORDABILITY_EXCEEDED"):
            message = f"{code} {desc}"
        else:
            message = f"{code} {err_msg}"
        if error_code == "INSTITUTION_TIMEOUT":
            dur = ms_lognormal(rng, 8000, 0.15)
        level, outcome = "warn", "failure"
        error = {"code": error_code, "message": err_msg, "type": "business"}
        result = "rejected"
    else:
        status, dur = 200, ms_lognormal(rng, median_ms)
        level, outcome, message, error, result = "info", "success", f"{code} {desc}", None, "success"

    rec.update({
        "log.level": level,
        "message": message,
        "event": {"kind": "event", "action": "transaction.complete", "outcome": outcome,
                  "duration": dur * 1_000_000},
        "url": {"path": api_path},
        "http": {"request": {"method": "POST"}, "response": {"status_code": status}},
        "transaction": {"id": tx_id, "result": result},
        "banking": detail,
    })
    if amount is not None:
        rec["amount"] = {"value": amount, "currency": "TRY"}
    if error:
        rec["error"] = error
    return rec


def generate(count: int, days: int, seed: int, customers_n: int, end: datetime) -> List[Dict]:
    rng = random.Random(seed)
    customers = build_customers(rng, customers_n)
    activity = [(c, c["activity"]) for c in customers]
    stamps = build_timestamps(rng, count, days, end)
    screen_weights = [(code, v[1]) for code, v in SCREENS.items()]
    seq: Dict[str, int] = {}
    records = []
    for ts in stamps:
        code = weighted(rng, screen_weights)
        customer = weighted(rng, activity)
        channel = weighted(rng, CHANNELS)
        if rng.random() < VIEW_RATIO:
            records.append(make_view(rng, ts, code, customer, channel))
        else:
            records.append(make_transaction(rng, ts, code, customer, channel, seq))
    return records


# ---------------------------------------------------------------------------
# Çıktı
# ---------------------------------------------------------------------------
def index_template(index: str) -> Dict:
    return {
        "index_patterns": [f"{index}*"],
        "template": {"mappings": {
            "dynamic_templates": [{"strings_as_keyword": {"match_mapping_type": "string",
                                                         "mapping": {"type": "keyword"}}}],
            "properties": {
                "@timestamp": {"type": "date"},
                "message": {"type": "text"},
                "client": {"properties": {"ip": {"type": "ip"},
                                          "geo": {"properties": {"location": {"type": "geo_point"}}}}},
                "event": {"properties": {"duration": {"type": "long"}}},
                "amount": {"properties": {"value": {"type": "double"}}},
                "customer": {"properties": {"age": {"type": "integer"}}},
                "banking": {"properties": {"loan": {"properties": {
                    "monthly_rate": {"type": "double"}, "debt_to_income": {"type": "double"}}}}},
            }}},
    }


def write_records(records: List[Dict], path: Path, fmt: str, index: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for rec in records:
            if fmt == "bulk":
                f.write(json.dumps({"index": {"_index": index}}) + "\n")
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def parse_end(value: Optional[str]) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=TR_TZ)
    return dt


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Sentetik bankacılık logu (ECS) üretir.")
    p.add_argument("--count", type=int, default=10000)
    p.add_argument("--days", type=int, default=30)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--customers", type=int, default=800)
    p.add_argument("--format", choices=["ndjson", "bulk"], default="ndjson")
    p.add_argument("--index", default=DEFAULT_INDEX)
    p.add_argument("--output", help="Çıktı dosyası (varsayılan tools/output/<index>.ndjson)")
    p.add_argument("--end", help="Son zaman (ISO, ör. 2026-10-17T09:00:00+03:00); verilmezse şimdi")
    p.add_argument("--write-template", action="store_true", help="Index template JSON'ını da yaz")
    args = p.parse_args(argv)

    end = parse_end(args.end)
    records = generate(args.count, args.days, args.seed, args.customers, end)
    out_dir = Path(__file__).parent / "output"
    suffix = ".bulk.ndjson" if args.format == "bulk" else ".ndjson"
    path = Path(args.output) if args.output else out_dir / f"{args.index}{suffix}"
    write_records(records, path, args.format, args.index)
    if args.write_template:
        tpl = out_dir / f"{args.index}-template.json"
        tpl.write_text(json.dumps(index_template(args.index), ensure_ascii=False, indent=2), encoding="utf-8")
    levels: Dict[str, int] = {}
    for r in records:
        levels[r["log.level"]] = levels.get(r["log.level"], 0) + 1
    dist = ", ".join(f"{k} %{v * 100 / len(records):.1f}" for k, v in sorted(levels.items()))
    print(f"{len(records)} kayıt yazıldı: {path} ({dist})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
