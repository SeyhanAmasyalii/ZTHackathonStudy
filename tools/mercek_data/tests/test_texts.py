"""V4 testleri: metin üretimi (şablon modu ve sahte Foundry istemcisi). İnternet gerektirmez."""
import importlib.util
import json
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("generate_texts", ROOT / "tools" / "mercek_data" / "generate_texts.py")
gt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gt)


def _all_texts(t):
    for notes in t["incident_notes"].values():
        yield from notes
    for items in t["solutions"].values():
        yield from (gt.text_of(i) for i in items)
    yield from (gt.text_of(r) for r in t["requests"])


def test_template_mode_volumes(tmp_path):
    t = gt.run(template=True, force=True, seed=42, output=tmp_path / "texts.json")
    c = t["meta"]["counts"]
    assert c["incident_notes"] >= 450
    assert c["solutions"] == 36
    assert c["requests"] == gt.REQUESTS_TARGET
    assert c["eval_drafts"] == 30
    assert all(len(v) >= 15 for v in t["incident_notes"].values())


def test_fixed_notes_kept_first(tmp_path):
    t = gt.run(template=True, force=True, seed=42, output=tmp_path / "texts.json")
    fixed = json.loads(gt.FIXED.read_text(encoding="utf-8"))["incident_notes"]
    key = "Fatura ödeme|abone numarası kabul edilmiyor"
    assert t["incident_notes"][key][:5] == fixed[key]


def test_no_forbidden_or_pii(tmp_path):
    t = gt.run(template=True, force=True, seed=42, output=tmp_path / "texts.json")
    for text in _all_texts(t):
        for p in gt.PII_PATTERNS:
            assert not re.search(p, text), text
    for r in t["requests"]:
        assert not re.search(r"hatırlatma|erteleme", gt.text_of(r), re.IGNORECASE)
    for items in t["solutions"].values():
        for s in items:
            assert not re.search(r"abone numaras|\bhane", gt.text_of(s), re.IGNORECASE)


def test_deterministic(tmp_path):
    a = gt.run(template=True, force=True, seed=42, output=tmp_path / "a.json")
    b = gt.run(template=True, force=True, seed=42, output=tmp_path / "b.json")
    a.pop("meta"), b.pop("meta")
    assert a == b


def test_clean_filters():
    items = ["Müşteri taksit hatırlatma almadığını söyledi ve bilgi istedi.",
             "Müşteri numarası 12345678901 olan kişi aradı ve bilgi istedi.",
             "Müşteri ekranın yavaş açıldığını belirtti, tekrar denemesi önerildi.",
             "Müşteri ekranın yavaş açıldığını belirtti, tekrar denemesi önerildi."]
    kept, dropped = gt.clean(items, "requests", [])
    assert kept == [items[2]]
    assert dropped == 3


def test_foundry_path_with_fake_client(tmp_path):
    calls = []

    words = ["ekran", "ödeme", "kart", "hesap", "şube", "mobil", "akşam", "sabah", "tutar", "işlem", "bekleme", "kayıt",
             "bilgi", "uyarı", "sayfa", "limit", "tarih", "kurum", "fatura", "şifre", "adres", "izin", "dekont", "bakiye",
             "rapor", "onay", "liste", "filtre", "arama", "süre", "yetki", "kanal", "müşteri", "temsilci", "servis", "kural"]

    def phrase(seed, n=9):
        return " ".join(random.Random(seed).sample(words, n))

    def fake_complete(messages):
        calls.append(messages)
        user = messages[1]["content"]
        n = int(re.search(r"Adet: (\d+)", user).group(1))
        k = len(calls) * 1000
        if "Talep tipi" in user:
            items = [{"title": phrase(k + i, 5), "description": "Talep: " + phrase(k + i + 500)} for i in range(n)]
            items.append({"title": "Hatırlatma", "description": "Taksit hatırlatma e-postası gönderilsin lütfen."})
        elif "Hata kodu" in user:
            items = [{"title": phrase(k + i, 4), "symptom": phrase(k + i + 300), "root_cause": phrase(k + i + 600),
                      "steps": [phrase(k + i + 700, 4), phrase(k + i + 800, 4)]} for i in range(n)]
        else:
            items = [{"note": "Müşteri " + phrase(k + i) + " konusunda bilgi istedi."} for i in range(n)]
        return json.dumps({"items": items}, ensure_ascii=False)

    out = tmp_path / "texts.json"
    t = gt.run(template=False, force=True, seed=42, complete=fake_complete, output=out)
    assert t["meta"]["mode"] == "foundry"
    assert all(not re.search("hatırlatma", gt.text_of(r), re.IGNORECASE) for r in t["requests"])
    assert len(t["requests"]) == gt.REQUESTS_TARGET
    # Tekrar çalıştırma: her şey hazır, Foundry çağrılmaz
    before = len(calls)
    gt.run(template=False, force=False, seed=42, complete=fake_complete, output=out)
    assert len(calls) == before


def test_prompt_loader_fills_variables():
    msgs = gt.load_prompt("gen-talep", {"module": "KRD", "screen_name": "X", "request_type": "yeni ekran",
                                        "count": 3, "forbidden_topics": "-"})
    assert msgs[0]["role"] == "system" and "taksit erteleme" in msgs[0]["content"]
    assert "Adet: 3" in msgs[1]["content"] and "{{" not in msgs[1]["content"]
