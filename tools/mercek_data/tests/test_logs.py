"""V3 testleri: log üretici ve senaryo enjeksiyonu. Çalıştırma: python3 -m pytest tools/mercek_data/tests -q"""
import collections
import importlib.util
from datetime import datetime, timedelta, timezone
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
END = gen.parse_end("2026-10-17T09:00:00+03:00")


@pytest.fixture(scope="module")
def generated(tmp_path_factory):
    path = tmp_path_factory.mktemp("logs") / "base.ndjson"
    records = gen.generate(10000, 30, 42, 800, END)
    gen.write_records(records, path, "ndjson", gen.DEFAULT_INDEX)
    return path, records


@pytest.fixture(scope="module")
def injected(generated, tmp_path_factory):
    base, _ = generated
    out = tmp_path_factory.mktemp("logs") / "mercek.ndjson"
    summary = inj.run(base, out, END, 42)
    return summary, inj.load(out)


def test_generator_is_deterministic():
    a = gen.generate(500, 30, 42, 100, END)
    b = gen.generate(500, 30, 42, 100, END)
    assert a == b


def test_generator_volume_order_and_levels(generated):
    _, records = generated
    assert len(records) == 10000
    stamps = [r["@timestamp"] for r in records]
    assert stamps == sorted(stamps)
    levels = collections.Counter(r["log.level"] for r in records)
    assert 0.86 < levels["info"] / 10000 < 0.92
    assert 0.07 < levels["warn"] / 10000 < 0.11
    assert 0.01 < levels["error"] / 10000 < 0.035


def test_generator_business_rules_hold(generated):
    _, records = generated
    for r in records:
        loan = r.get("banking", {}).get("loan")
        if loan and r["event"]["outcome"] == "success":
            assert loan["debt_to_income"] <= 0.5
        if loan and r.get("error", {}).get("code") == "AFFORDABILITY_EXCEEDED":
            assert loan["debt_to_income"] > 0.5
        iban = r.get("banking", {}).get("account", {}).get("iban")
        if iban:
            assert gen.is_valid_iban(iban)


def test_tl_format():
    assert gen.tl(13500) == "13.500 TRY"
    assert gen.tl(747.71) == "747,71 TRY"


def test_scenario_c_numbers(injected):
    summary, _ = injected
    assert summary["subscriber_errors_since_oct1"] == 412
    assert summary["iski"] == 400
    assert summary["iski_share_pct"] == pytest.approx(97.1, abs=0.1)
    assert summary["iski_all_13"] is True
    assert summary["iski_customers"] == 187
    assert summary["iski_13_before_oct1"] == 0


def test_no_subscriber_error_outside_injection(injected):
    _, records = injected
    errs = [r for r in records if r.get("error", {}).get("field") == "subscriber_no"]
    assert len(errs) == 412
    other = [r for r in records if r["screen"]["code"] == "ODMTFATR"
             and r.get("error", {}).get("code") == "VALIDATION_ERROR" and r["error"].get("field") != "subscriber_no"]
    assert all(r["error"]["field"] == "amount" for r in other)


def test_all_records_before_end(injected):
    _, records = injected
    assert all(inj.parse_ts(r["@timestamp"]) <= END for r in records)


def test_mehmet_history(injected):
    _, records = injected
    mine = [r for r in records if r["customer"]["number"] == "10000003"]
    assert len(mine) == 3
    assert all(r["banking"]["bill"]["subscriber_no"] == "4012345678" and r["event"]["outcome"] == "success" for r in mine)


def test_demo_window(injected):
    _, records = injected
    now = datetime(2026, 10, 17, 15, 10, tzinfo=timezone(timedelta(hours=3)))
    window = inj.build_demo_window(now, inj.customers_from(records))
    assert len(window) == 46
    for r in window:
        ts = inj.parse_ts(r["@timestamp"])
        assert now - timedelta(minutes=30) <= ts <= now - timedelta(minutes=1)
        assert r["banking"]["bill"]["institution"] == "Başkentgaz"
        assert r["error"]["code"] == "INSTITUTION_TIMEOUT"
