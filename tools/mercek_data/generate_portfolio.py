#!/usr/bin/env python3
"""Sentetik müşteri ve kredi portföyü (V5).

40.000 müşteri, 26.000 aktif kredili müşteri, 33.000 kredi. Senaryo kümeleri önce tam sayıda kurulur,
kalan veri dağılımla üretilir:
  D · hedef grup: son 12 ayda gecikmesi olan, aktif kredili 2.340 müşteri; izin kesişimi
      e-posta+SMS 1.169 · yalnız e-posta 188 · yalnız SMS 726 · hiçbiri 257
  E · etkilenen bölge (3 il): aktif kredili 4.870 müşteri · 6.215 kredi · 612'si gecikmede ·
      10.10.2026'dan sonra adres değiştiren 37 müşteri
Log müşterileri (V3, 800 kişi) aynı numara, ad, il ve segmentle portföyde yer alır.

Örnek:
  python3 tools/mercek_data/generate_portfolio.py
Çıktı: data/out/customers.csv, data/out/loans.csv; catalog.json → affected_region.provinces
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import random
import unicodedata
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("generate_banking_logs", ROOT / "tools" / "generate_banking_logs.py")
gen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gen)  # type: ignore[union-attr]

CATALOG = ROOT / "data" / "seed" / "catalog.json"
LOGS = ROOT / "tools" / "output" / "mercek-logs.ndjson"
OUT_DIR = ROOT / "data" / "out"

TODAY = date(2026, 10, 17)
DISASTER = date(2026, 10, 10)
FIRST_NO, LAST_NO = 10000101, 10040100

# Kesin değerler (docs/mercek-sentetik-veri-uretimi.md §5)
CUSTOMERS = 40000
ACTIVE_LOAN_CUSTOMERS = 26000
LOANS = 33000
D_TARGET = 2340
D_PERMISSIONS = {(True, True): 1169, (True, False): 188, (False, True): 726, (False, False): 257}
E_CUSTOMERS = 4870
E_LOANS = 6215
E_DELINQUENT_LOANS = 612
E_ADDRESS_CHANGED = 37
NON_REGION_DELINQUENT_LOANS = 950  # bölge dışında şu an gecikmede olan kredi (dağılım, kesin değil)
REGION_CANDIDATES = ["Bursa", "Antalya", "Adana"]  # İstanbul, Ankara, İzmir dışındaki en büyük üç il

DISTRICTS = {
    "İstanbul": ["Kadıköy", "Beşiktaş", "Üsküdar", "Ümraniye", "Bakırköy", "Ataşehir"],
    "Ankara": ["Çankaya", "Keçiören", "Yenimahalle", "Etimesgut"],
    "İzmir": ["Karşıyaka", "Bornova", "Konak", "Buca"],
    "Bursa": ["Osmangazi", "Nilüfer", "Yıldırım"],
    "Antalya": ["Muratpaşa", "Konyaaltı", "Kepez"],
    "Adana": ["Seyhan", "Çukurova", "Yüreğir"],
    "Konya": ["Selçuklu", "Meram", "Karatay"],
    "Gaziantep": ["Şahinbey", "Şehitkamil"],
    "Kayseri": ["Melikgazi", "Kocasinan", "Talas"],
    "Trabzon": ["Ortahisar", "Akçaabat"],
    "Samsun": ["İlkadım", "Atakum", "Canik"],
    "Eskişehir": ["Odunpazarı", "Tepebaşı"],
}

CUSTOMER_FIELDS = ["customer_number", "full_name", "segment", "age", "monthly_income", "city", "district",
                   "region_affected", "address_changed_at", "email", "phone", "perm_email", "perm_sms", "perm_phone",
                   "in_logs"]
LOAN_FIELDS = ["loan_id", "customer_number", "product", "principal", "remaining_principal", "monthly_rate", "term",
               "installment", "paid_installments", "next_due_date", "status", "delinquent_12m", "collection_account"]


# ---------------------------------------------------------------------------
# Yardımcılar
# ---------------------------------------------------------------------------
def ascii_fold(text: str) -> str:
    table = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")
    text = text.translate(table)
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()


def email_for(name: str, number: str) -> str:
    first, *rest = name.lower().split()
    return f"{ascii_fold(first)}.{ascii_fold(rest[-1] if rest else 'musteri')}.{number[-4:]}@ornek.test"


def phone_for(rng: random.Random) -> str:
    return f"+90 5{rng.randint(30, 59)} 000 {rng.randint(10, 99)} {rng.randint(10, 99)}"


def income_for(rng: random.Random, segment: str, age: int) -> int:
    median = next(m for s, _, m in gen.SEGMENTS if s == segment)
    income = int(rng.lognormvariate(math.log(median), 0.45))
    if age <= 24:
        income = int(income * 0.5)
    return max(income, 8500)


def load_log_customers(path: Path) -> Dict[str, Dict]:
    """V3 log müşterileri: numara → ad, il, segment, yaş, (varsa) gelir."""
    if not path.exists():
        raise SystemExit(f"{path} yok. Önce V3'ü çalıştırın (generate_banking_logs.py + inject_log_scenarios.py).")
    out: Dict[str, Dict] = {}
    with path.open(encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            c = r["customer"]
            if not (FIRST_NO <= int(c["number"]) <= LAST_NO):
                continue  # Mehmet (10000003) gibi uygulama kullanıcıları portföyde değil
            entry = out.setdefault(c["number"], {"name": c["name"], "city": c["city"], "segment": c["segment"],
                                                 "age": c["age"], "income": None})
            banking = r.get("banking", {})
            for key in ("loan", "card"):
                if key in banking and banking[key].get("monthly_income"):
                    entry["income"] = int(banking[key]["monthly_income"])
    return out


# ---------------------------------------------------------------------------
# Müşteriler
# ---------------------------------------------------------------------------
def build_customers(rng: random.Random, log_customers: Dict[str, Dict]) -> List[Dict]:
    cities = [(c, v[0]) for c, v in gen.CITIES.items()]
    customers = []
    for number in range(FIRST_NO, LAST_NO + 1):
        no = str(number)
        if no in log_customers:
            lc = log_customers[no]
            name, city, segment, age = lc["name"], lc["city"], lc["segment"], lc["age"]
            income = lc["income"] or income_for(rng, segment, age)
        else:
            segment = gen.weighted(rng, [(s, w) for s, w, _ in gen.SEGMENTS])
            age = rng.randint(19, 78)
            name = f"{rng.choice(gen.FIRST_NAMES)} {rng.choice(gen.LAST_NAMES)}"
            city = gen.weighted(rng, cities)
            income = income_for(rng, segment, age)
        customers.append({
            "customer_number": no, "full_name": name, "segment": segment, "age": age, "monthly_income": income,
            "city": city, "district": rng.choice(DISTRICTS[city]), "region_affected": False,
            "address_changed_at": "", "email": email_for(name, no), "phone": phone_for(rng),
            "perm_email": False, "perm_sms": False, "perm_phone": False, "in_logs": no in log_customers,
        })
    return customers


def assign_address_dates(rng: random.Random, customers: List[Dict], changed_after: Set[str]) -> None:
    """Çoğu müşteri için geçmiş bir adres değişikliği tarihi; yalnızca E'nin 37 müşterisinde afet sonrası."""
    for c in customers:
        if c["customer_number"] in changed_after:
            c["address_changed_at"] = (DISASTER + timedelta(days=rng.randint(1, 6))).isoformat()
        elif rng.random() < 0.55:
            c["address_changed_at"] = (DISASTER - timedelta(days=rng.randint(30, 5 * 365))).isoformat()


def assign_permissions(rng: random.Random, customers: List[Dict], d_target: Set[str]) -> None:
    target = [c for c in customers if c["customer_number"] in d_target]
    rng.shuffle(target)
    combos: List = []
    for combo, n in D_PERMISSIONS.items():
        combos += [combo] * n
    for c, (email, sms) in zip(target, combos):
        c["perm_email"], c["perm_sms"] = email, sms
        c["perm_phone"] = rng.random() < 0.35
    for c in customers:
        if c["customer_number"] in d_target:
            continue
        c["perm_email"] = rng.random() < 0.64
        c["perm_sms"] = rng.random() < 0.82
        c["perm_phone"] = rng.random() < 0.38


# ---------------------------------------------------------------------------
# Krediler
# ---------------------------------------------------------------------------
def split_loans(rng: random.Random, holders: List[Dict], total: int) -> Dict[str, int]:
    """Her kredili müşteriye 1 kredi, kalan krediyi rastgele dağıt (müşteri başına en çok 3)."""
    counts = {c["customer_number"]: 1 for c in holders}
    extra = total - len(holders)
    numbers = [c["customer_number"] for c in holders]
    while extra > 0:
        n = rng.choice(numbers)
        if counts[n] < 3:
            counts[n] += 1
            extra -= 1
    return counts


def make_loan(rng: random.Random, seq: int, customer: Dict, delinquent_now: bool) -> Dict:
    term = rng.choice(gen.LOAN_TERMS)
    rate = gen.monthly_rate(term)
    max_ok = customer["monthly_income"] * 0.5 / gen.installment(1, rate, term)
    if max_ok < 5000:
        term, rate = 36, gen.monthly_rate(36)
        max_ok = customer["monthly_income"] * 0.5 / gen.installment(1, rate, term)
    upper = max(5000, min(500000, max_ok))
    principal = max(5000, int(rng.uniform(5000, upper) // 1000 * 1000))
    inst = gen.installment(principal, rate, term)
    paid = rng.randint(0, term - 1)
    e = rate * 1.30
    remaining = principal * ((1 + e) ** term - (1 + e) ** paid) / ((1 + e) ** term - 1)
    if delinquent_now:
        due = TODAY - timedelta(days=rng.randint(1, 60))
    else:
        due = TODAY + timedelta(days=rng.randint(1, 30))
    return {
        "loan_id": f"KRD{seq:08d}", "customer_number": customer["customer_number"], "product": "Bireysel İhtiyaç",
        "principal": principal, "remaining_principal": round(remaining, 2), "monthly_rate": rate, "term": term,
        "installment": round(inst, 2), "paid_installments": paid, "next_due_date": due.isoformat(),
        "status": "gecikmede" if delinquent_now else "normal", "delinquent_12m": delinquent_now,
        "collection_account": gen.generate_iban(rng),
    }


# ---------------------------------------------------------------------------
# Akış
# ---------------------------------------------------------------------------
def build(seed: int = 42, logs_path: Path = LOGS) -> Dict:
    rng = random.Random(seed)
    log_customers = load_log_customers(logs_path)
    customers = build_customers(rng, log_customers)
    by_no = {c["customer_number"]: c for c in customers}

    # E · etkilenen bölge
    provinces = REGION_CANDIDATES
    region = [c for c in customers if c["city"] in provinces]
    for c in region:
        c["region_affected"] = True
    if len(region) < E_CUSTOMERS:
        raise SystemExit("Seçilen illerde yeterli müşteri yok")
    non_region = [c for c in customers if c["city"] not in provinces]

    # Aktif kredili müşteriler: bölgede tam 4.870, toplam tam 26.000
    region_holders = rng.sample(region, E_CUSTOMERS)
    other_holders = rng.sample(non_region, ACTIVE_LOAN_CUSTOMERS - E_CUSTOMERS)
    region_counts = split_loans(rng, region_holders, E_LOANS)
    other_counts = split_loans(rng, other_holders, LOANS - E_LOANS)

    # Şu an gecikmede olan krediler: bölgede tam 612
    region_loan_slots = [(n, i) for n, k in region_counts.items() for i in range(k)]
    other_loan_slots = [(n, i) for n, k in other_counts.items() for i in range(k)]
    region_delinquent = set(rng.sample(region_loan_slots, E_DELINQUENT_LOANS))
    other_delinquent = set(rng.sample(other_loan_slots, NON_REGION_DELINQUENT_LOANS))

    # D · son 12 ayda gecikmesi olan aktif kredili müşteri: tam 2.340 (şu an gecikmede olanların hepsi dahil)
    overdue_customers = {n for n, _ in region_delinquent | other_delinquent}
    if len(overdue_customers) > D_TARGET:
        raise SystemExit("Şu an gecikmede olan müşteri sayısı D hedef grubunu aşıyor")
    holders = {c["customer_number"] for c in region_holders + other_holders}
    rest = sorted(holders - overdue_customers)
    d_target = overdue_customers | set(rng.sample(rest, D_TARGET - len(overdue_customers)))

    # E · afet sonrası adres değiştiren 37 kredili bölge müşterisi
    changed_after = {c["customer_number"] for c in rng.sample(region_holders, E_ADDRESS_CHANGED)}
    assign_address_dates(rng, customers, changed_after)
    assign_permissions(rng, customers, d_target)

    # Kredi kayıtları
    loans: List[Dict] = []
    seq = 0
    for counts, delinquent in ((region_counts, region_delinquent), (other_counts, other_delinquent)):
        for n, k in counts.items():
            for i in range(k):
                seq += 1
                loan = make_loan(rng, seq, by_no[n], (n, i) in delinquent)
                if n in d_target:
                    loan["delinquent_12m"] = True  # müşterinin geçmiş gecikmesi tüm kredilerine işlenir
                loans.append(loan)
    loans.sort(key=lambda x: x["loan_id"])
    return {"customers": customers, "loans": loans, "provinces": provinces, "d_target": d_target}


def summarize(customers: List[Dict], loans: List[Dict]) -> Dict:
    holders = {x["customer_number"] for x in loans}
    by_no = {c["customer_number"]: c for c in customers}
    d_set = {x["customer_number"] for x in loans if x["delinquent_12m"]}
    d = [by_no[n] for n in d_set]
    region_loans = [x for x in loans if by_no[x["customer_number"]]["region_affected"]]
    region_holders = {x["customer_number"] for x in region_loans}
    return {
        "customers": len(customers),
        "active_loan_customers": len(holders),
        "loans": len(loans),
        "d_target": len(d),
        "d_email": sum(c["perm_email"] for c in d),
        "d_sms": sum(c["perm_sms"] for c in d),
        "d_any": sum(c["perm_email"] or c["perm_sms"] for c in d),
        "d_combo": {f"{e}/{s}": sum(1 for c in d if (c["perm_email"], c["perm_sms"]) == (e, s))
                    for e, s in D_PERMISSIONS},
        "e_customers": len(region_holders),
        "e_loans": len(region_loans),
        "e_delinquent": sum(1 for x in region_loans if x["status"] == "gecikmede"),
        "e_address_changed": sum(1 for n in region_holders if by_no[n]["address_changed_at"] > DISASTER.isoformat()),
        "log_customers_in_portfolio": sum(1 for c in customers if c["in_logs"]),
    }


EXPECTED = {"customers": CUSTOMERS, "active_loan_customers": ACTIVE_LOAN_CUSTOMERS, "loans": LOANS,
            "d_target": D_TARGET, "d_email": 1357, "d_sms": 1895, "d_any": 2083,
            "e_customers": E_CUSTOMERS, "e_loans": E_LOANS, "e_delinquent": E_DELINQUENT_LOANS,
            "e_address_changed": E_ADDRESS_CHANGED}


def write_csv(path: Path, rows: List[Dict], fields: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: (int(v) if isinstance(v, bool) else v) for k, v in r.items() if k in fields})


def update_catalog(provinces: List[str]) -> None:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    catalog["affected_region"]["provinces"] = provinces
    CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Sentetik müşteri ve kredi portföyü (V5)")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--logs", default=str(LOGS))
    p.add_argument("--out-dir", default=str(OUT_DIR))
    p.add_argument("--no-catalog-update", action="store_true")
    args = p.parse_args(argv)

    result = build(args.seed, Path(args.logs))
    s = summarize(result["customers"], result["loans"])
    wrong = {k: (s[k], v) for k, v in EXPECTED.items() if s[k] != v}
    if wrong:
        raise SystemExit(f"Senaryo değerleri tutmuyor (bulunan, beklenen): {wrong}")
    out = Path(args.out_dir)
    write_csv(out / "customers.csv", result["customers"], CUSTOMER_FIELDS)
    write_csv(out / "loans.csv", result["loans"], LOAN_FIELDS)
    if not args.no_catalog_update:
        update_catalog(result["provinces"])
    print(f"{s['customers']} müşteri · {s['active_loan_customers']} kredili · {s['loans']} kredi → {out}")
    print(f"D · hedef grup {s['d_target']} · e-posta {s['d_email']} (%{100 * s['d_email'] / s['d_target']:.0f}) · "
          f"SMS {s['d_sms']} (%{100 * s['d_sms'] / s['d_target']:.0f}) · en az biri {s['d_any']} "
          f"(%{100 * s['d_any'] / s['d_target']:.0f}) · kesişim {s['d_combo']}")
    print(f"E · {s['e_customers']} müşteri · {s['e_loans']} kredi · {s['e_delinquent']} gecikmede · "
          f"{s['e_address_changed']} afet sonrası adres değişikliği")
    print(f"Log müşterileri portföyde: {s['log_customers_in_portfolio']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
