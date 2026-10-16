"""V5 testleri: müşteri ve kredi portföyü. Log dosyasını geçici klasörde kendisi üretir."""
import importlib.util
import json
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parents[2]


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


gen = _load("generate_banking_logs", TOOLS / "generate_banking_logs.py")
inj = _load("inject_log_scenarios", TOOLS / "mercek_data" / "inject_log_scenarios.py")
gp = _load("generate_portfolio", TOOLS / "mercek_data" / "generate_portfolio.py")
END = gen.parse_end("2026-10-17T09:00:00+03:00")


@pytest.fixture(scope="module")
def logs_path(tmp_path_factory):
    d = tmp_path_factory.mktemp("v5")
    base, out = d / "base.ndjson", d / "mercek.ndjson"
    gen.write_records(gen.generate(10000, 30, 42, 800, END), base, "ndjson", gen.DEFAULT_INDEX)
    inj.run(base, out, END, 42)
    return out


@pytest.fixture(scope="module")
def portfolio(logs_path):
    return gp.build(42, logs_path)


def test_scenario_numbers(portfolio):
    s = gp.summarize(portfolio["customers"], portfolio["loans"])
    for key, expected in gp.EXPECTED.items():
        assert s[key] == expected, key
    assert s["d_combo"] == {"True/True": 1169, "True/False": 188, "False/True": 726, "False/False": 257}


def test_log_customers_consistent(portfolio, logs_path):
    by_no = {c["customer_number"]: c for c in portfolio["customers"]}
    seen = set()
    with logs_path.open(encoding="utf-8") as f:
        for line in f:
            c = json.loads(line)["customer"]
            if c["number"] == "10000003" or c["number"] in seen:
                continue
            seen.add(c["number"])
            p = by_no[c["number"]]
            assert (p["full_name"], p["city"], p["segment"]) == (c["name"], c["city"], c["segment"])
            assert p["in_logs"]
    assert len(seen) > 700


def test_region(portfolio):
    assert "İstanbul" not in portfolio["provinces"] and len(portfolio["provinces"]) == 3
    for c in portfolio["customers"]:
        assert c["region_affected"] == (c["city"] in portfolio["provinces"])
    holders = {x["customer_number"] for x in portfolio["loans"]}
    recent = [c for c in portfolio["customers"] if c["address_changed_at"] > gp.DISASTER.isoformat()]
    assert len(recent) == 37
    assert all(c["region_affected"] and c["customer_number"] in holders for c in recent)


def test_loans_follow_krdtkull_rules(portfolio):
    by_no = {c["customer_number"]: c for c in portfolio["customers"]}
    for x in portfolio["loans"]:
        assert 5000 <= x["principal"] <= 500000
        assert x["term"] in gen.LOAN_TERMS and x["monthly_rate"] == gen.monthly_rate(x["term"])
        assert x["installment"] <= by_no[x["customer_number"]]["monthly_income"] * 0.5 + 0.01
        assert gen.is_valid_iban(x["collection_account"])
        if x["status"] == "gecikmede":
            assert x["delinquent_12m"] and x["next_due_date"] < gp.TODAY.isoformat()


def test_no_personal_data(portfolio):
    for c in portfolio["customers"]:
        assert c["email"].endswith("@ornek.test")
        assert c["phone"].startswith("+90 5") and " 000 " in c["phone"]


def test_deterministic(logs_path, portfolio):
    again = gp.build(42, logs_path)
    assert again["customers"][:200] == portfolio["customers"][:200]
    assert again["loans"][:200] == portfolio["loans"][:200]
