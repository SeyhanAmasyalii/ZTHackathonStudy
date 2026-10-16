#!/usr/bin/env python3
"""Geçmiş talepler ve değerlendirme seti (V6).

requests: V4'teki 87 talep metni + elle yazılmış 8 kesin talep (D'nin 5'i, E'nin 3'ü) = 95 kayıt.
          Numaralar TLP-0500 … TLP-1037, tarihler 2020-06 … 2026-10 (numarayla artan).
          Uygulamadaki örnek talepler (TLP-1038 … 1042) uygulamanın kendi verisidir; burada üretilmez.
--eval:   30 vakalık değerlendirme seti (10 eşleşmeli, 10 eşleşmesiz, 10 talep) → data/seed/eval_cases.json.
          Vakalar indekse yüklenmez; metinleri indekstekilere çok benzerse elenir.

Girdi: data/seed/catalog.json, texts.json, fixed_texts.json; --eval için data/out/solutions.csv (V6 incidents)
Çıktı: data/out/requests.csv; --eval ile data/seed/eval_cases.json
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import random
import re
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List, Optional

ROOT = Path(__file__).resolve().parents[2]
SEED = ROOT / "data" / "seed"
OUT = ROOT / "data" / "out"

FIRST_ID, LAST_ID = 500, 1037
FIRST_DATE, LAST_DATE = date(2020, 6, 1), date(2026, 10, 9)
TYPE_CODES = {"mevcut ekran değişikliği": "existing_change", "yeni ekran": "new_screen", "batch işi": "batch",
              "karma": "mixed"}
UNITS = ["Kredi Tahsilatları", "Bireysel Krediler", "Kart Ürünleri", "Ödeme Sistemleri", "Şube Operasyonları",
         "Dijital Bankacılık", "Müşteri Deneyimi", "Uyum ve İç Kontrol"]
ANALYSTS = ["Ayşe Kaya", "Selin Kurt", "Burak Tekin"]
FORBIDDEN = re.compile(r"hatırlatma|erteleme|ertelen", re.IGNORECASE)

# Kesin talepler (docs/mercek-sentetik-veri-uretimi.md §8)
FIXED = {
    "TLP-0871": dict(type="batch", screens=["KRTREKST"], component="otomatik", effort=14, unit="Kart Ürünleri",
                     services={"KART_BASVURU": 12, "MUSTERI_YONETIM": 2},
                     decisions="Son ödeme tarihinden 3 gün önce; günde bir çalışır; aynı ekstre için tek gönderim"),
    "TLP-0915": dict(type="batch", screens=["ODMTFATR"], component="otomatik", effort=11, unit="Ödeme Sistemleri",
                     services={"FATURA_ODEME": 9, "MUSTERI_YONETIM": 2}, decisions="E-postada tutar yer almaz"),
    "TLP-0962": dict(type="batch", screens=["HSPTVDLI"], component="otomatik", effort=9, unit="Dijital Bankacılık",
                     services={"HESAP_YONETIM": 8, "MUSTERI_YONETIM": 1}, decisions="Yalnızca iletişim izni olan müşteriler"),
    "TLP-1004": dict(type="existing_change", screens=["KRTREKST"], component="manuel", effort=6, unit="Kart Ürünleri",
                     services={"KART_BASVURU": 5, "MUSTERI_YONETIM": 1},
                     decisions="Şube ve çağrı merkezi temsilcileri gönderebilir; son gönderim satırda görünür"),
    "TLP-1019": dict(type="existing_change", screens=["HSPRHRKT"], component="manuel", effort=8, unit="Şube Operasyonları",
                     services={"HESAP_YONETIM": 6, "MUSTERI_YONETIM": 2}, decisions="İzin yoksa buton pasif"),
    "TLP-0588": dict(type="new_screen", screens=[], component="yeni ekran", effort=15, unit="Bireysel Krediler",
                     services={"KREDI_TAKIP": 8, "KREDI_KULLANDIRIM": 3, "MUSTERI_YONETIM": 4}, decisions=""),
    "TLP-0712": dict(type="new_screen", screens=[], component="yeni ekran", effort=13, unit="Kart Ürünleri",
                     services={"KART_BASVURU": 9, "MUSTERI_YONETIM": 4}, decisions=""),
    "TLP-0846": dict(type="new_screen", screens=[], component="yeni ekran", effort=17, unit="Bireysel Krediler",
                     services={"KREDI_TAKIP": 13, "KREDI_KULLANDIRIM": 4}, decisions=""),
}
FIELDS = ["request_id", "created_at", "requester_unit", "title", "description", "type", "components_json",
          "screens_json", "services_json", "effort_md", "component_efforts_json", "service_efforts_json", "decisions",
          "analysis_json", "analyst", "approved_by", "scope_additions", "status", "planned_service_id", "planned_from",
          "planned_to"]


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def date_for(number: int) -> date:
    span = (LAST_DATE - FIRST_DATE).days
    return FIRST_DATE + timedelta(days=round(span * (number - FIRST_ID) / (LAST_ID - FIRST_ID)))


def norm_words(text: str) -> set:
    return set(re.sub(r"[^\w\s]", " ", text.lower()).split())


def too_similar(a: str, b: str, threshold: float = 0.8) -> bool:
    wa, wb = norm_words(a), norm_words(b)
    return bool(wa and wb) and len(wa & wb) / len(wa | wb) >= threshold


def components_for(rtype: str) -> List[Dict]:
    return {"existing_change": [{"kind": "manuel"}], "new_screen": [{"kind": "yeni ekran"}],
            "batch": [{"kind": "otomatik"}], "mixed": [{"kind": "otomatik"}, {"kind": "manuel"}]}[rtype]


def build_requests(seed: int = 42) -> List[Dict]:
    rng = random.Random(seed)
    catalog = load_json(SEED / "catalog.json")
    texts = load_json(SEED / "texts.json")
    fixed_text = {r["request_id"]: r for r in load_json(SEED / "fixed_texts.json")["requests"]}
    screen_by_name = {s["name"]: s["code"] for s in catalog["screens"]}
    roles = catalog["screen_services"]

    generated = [r for r in texts["requests"] if not FORBIDDEN.search(r["title"] + " " + r["description"])]
    free_ids = [n for n in range(FIRST_ID, LAST_ID + 1) if f"TLP-{n:04d}" not in FIXED]
    ids = sorted(rng.sample(free_ids, len(generated)))
    rng.shuffle(generated)
    rows: List[Dict] = []

    for number, item in zip(ids, generated):
        rtype = TYPE_CODES.get(item["type"], "existing_change")
        code = screen_by_name.get(item["screen"])
        main = next((x["service_id"] for x in roles if x["screen_code"] == code and x["role"] == "ana"), None)
        interactive = [x["service_id"] for x in roles if x["screen_code"] == code and x["role"] == "etkilesimli"]
        effort = int(min(40, max(3, round(rng.lognormvariate(math.log(12), 0.5)))))
        services = {main: effort} if main else {}
        if interactive and effort >= 4:
            share = max(1, round(effort * rng.uniform(0.1, 0.3)))
            services = {main: effort - share, interactive[0]: share}
        comps = components_for(rtype)
        if rtype == "mixed":
            first = max(1, round(effort * rng.uniform(0.4, 0.7)))
            comp_efforts = {"otomatik": first, "manuel": effort - first}
        else:
            comp_efforts = {comps[0]["kind"]: effort}
        rows.append(_row(number, rng.choice(UNITS), item["title"], item["description"], rtype, comps,
                         [code] if code and rtype != "new_screen" else [], services, effort, comp_efforts, "", rng))

    for rid, spec in FIXED.items():
        text = fixed_text[rid]
        number = int(rid.split("-")[1])
        rows.append(_row(number, spec["unit"], text["title"], text["description"], spec["type"],
                         [{"kind": spec["component"]}], spec["screens"], spec["services"], spec["effort"],
                         {spec["component"]: spec["effort"]}, spec["decisions"], rng))
    rows.sort(key=lambda r: r["request_id"])
    return rows


def _row(number, unit, title, description, rtype, comps, screens, services, effort, comp_efforts, decisions, rng):
    services = {k: v for k, v in services.items() if k}
    ordered = sorted(services.items(), key=lambda kv: -kv[1])
    return {
        "request_id": f"TLP-{number:04d}", "created_at": date_for(number).isoformat(), "requester_unit": unit,
        "title": title, "description": description, "type": rtype,
        "components_json": json.dumps(comps, ensure_ascii=False),
        "screens_json": json.dumps(screens, ensure_ascii=False),
        "services_json": json.dumps([{"service_id": s, "role": "ana" if i == 0 else "etkilesimli"}
                                     for i, (s, _) in enumerate(ordered)], ensure_ascii=False),
        "effort_md": effort, "component_efforts_json": json.dumps(comp_efforts, ensure_ascii=False),
        "service_efforts_json": json.dumps(services, ensure_ascii=False), "decisions": decisions,
        "analysis_json": "", "analyst": rng.choice(ANALYSTS), "approved_by": "", "scope_additions": "",
        "status": "tamamlandi", "planned_service_id": ordered[0][0] if ordered else "", "planned_from": "",
        "planned_to": "",
    }


# ---------------------------------------------------------------------------
# Değerlendirme seti
# ---------------------------------------------------------------------------
MATCH_FRAMES = ["Temsilci notu: {x} gibi görünen bir durum bildirildi, müşteri işlemi tamamlayamadı.",
                "Şubeden gelen kayıt: ekranda {x} benzeri bir sorun var, çözüm aranıyor.",
                "Çağrı merkezi aktarımı: müşteri {x} yaşıyor olabilir, yönlendirme bekliyor."]
REQUEST_EVAL = [  # (metin, beklenen tip, beklenen ekranlar, beklenen ana servis)
    ("Kart limit bilgisini gösteren listede kullanılabilir limit sütunu da görünsün.", "existing_change", ["KRTRKRTL"], "KART_BASVURU"),
    ("Bakiye sorgulama sonucunda bloke tutarlar ayrı bir satırda gösterilsin.", "existing_change", ["HSPRBKYE"], "HESAP_YONETIM"),
    ("Kimlik doğrulama adımında yeni kimlik kartı seri numarası da kabul edilsin.", "existing_change", ["MUSTKYCD"], "MUSTERI_YONETIM"),
    ("Vergi ödemelerinde plaka ile birden fazla borç tek seferde ödenebilsin.", "existing_change", ["ODMTVRGI"], "FATURA_ODEME"),
    ("Havale ekranında sık kullanılan alıcılar kaydedilip listeden seçilebilsin.", "existing_change", ["HSPTHVLE"], "ODEME_SISTEMLERI"),
    ("Her gece bir önceki günün başarısız fatura ödemelerini kurum bazında raporlayan bir iş istiyoruz.", "batch", ["ODMTFATR"], "FATURA_ODEME"),
    ("Vadeli hesapların aylık faiz tahakkukunu kontrol eden gece işi kurulsun.", "batch", ["HSPTVDLI"], "HESAP_YONETIM"),
    ("Şubelerin kart teslimat bekleyen başvurularını takip edebileceği yeni bir ekran istiyoruz.", "new_screen", [], "KART_BASVURU"),
    ("Kredi başvuru durumu ekranına karar gerekçesi eklensin ve reddedilenler haftalık raporlansın.", "mixed", ["KRDRBASV"], "KREDI_KULLANDIRIM"),
    ("Müşteri bilgi sorgulama ekranında son güncelleme tarihi ve güncelleyen kanal görünsün.", "existing_change", ["MUSRBLGI"], "MUSTERI_YONETIM"),
]


def build_eval(seed: int, requests: List[Dict], solutions_path: Path) -> Dict:
    rng = random.Random(seed + 1)
    texts = load_json(SEED / "texts.json")
    if not solutions_path.exists():
        raise SystemExit(f"{solutions_path} yok. Önce generate_incidents.py çalıştırın.")
    with solutions_path.open(encoding="utf-8") as f:
        solutions = [s for s in csv.DictReader(f) if s["solution_id"] != "SOL-031"]
    indexed = [f"{s['title']} {s['symptom']} {s['root_cause']} {s['steps']}" for s in solutions]
    indexed += [f"{r['title']} {r['description']}" for r in requests]

    def ok(text: str) -> bool:
        return not any(too_similar(text, other) for other in indexed)

    cases: List[Dict] = []
    for i, s in enumerate(rng.sample(solutions, 10)):
        text = MATCH_FRAMES[i % 3].format(x=s["title"].lower())
        cases.append({"id": f"EV-M{i + 1:02d}", "group": "match", "text": text, "expected_solution_id": s["solution_id"],
                      "expected_error_code": s["error_code"], "leak_check": ok(text), "reviewed": False})
    for i, d in enumerate(texts["eval_drafts"]["no_match"][:10]):
        text = f"Temsilci notu: {d['draft']}."
        cases.append({"id": f"EV-N{i + 1:02d}", "group": "no_match", "text": text, "expected_solution_id": None,
                      "leak_check": ok(text), "reviewed": False})
    for i, (text, rtype, screens, main) in enumerate(REQUEST_EVAL):
        cases.append({"id": f"EV-T{i + 1:02d}", "group": "request", "text": text, "expected_type": rtype,
                      "expected_screens": screens, "expected_main_service": main, "leak_check": ok(text),
                      "reviewed": False})
    return {"_meta": {"description": "Değerlendirme seti (§8.1). İndekse yüklenmez. 'reviewed' alanı elle gözden "
                                     "geçirildikten sonra true yapılır.", "groups": {"match": 10, "no_match": 10, "request": 10}},
            "cases": cases}


def write_csv(path: Path, rows: List[Dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Geçmiş talepler ve değerlendirme seti (V6)")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out-dir", default=str(OUT))
    p.add_argument("--eval", action="store_true", help="Değerlendirme setini de üret")
    args = p.parse_args(argv)
    out = Path(args.out_dir)
    rows = build_requests(args.seed)
    bad = [r["request_id"] for r in rows if FORBIDDEN.search(r["title"] + r["description"]) and r["request_id"] not in FIXED]
    if bad:
        raise SystemExit(f"Yasak konulu talep: {bad}")
    write_csv(out / "requests.csv", rows)
    print(f"{len(rows)} talep ({rows[0]['request_id']}…{rows[-1]['request_id']}) → {out / 'requests.csv'}")
    if args.eval:
        ev = build_eval(args.seed, rows, out / "solutions.csv")
        leaks = [c["id"] for c in ev["cases"] if not c["leak_check"]]
        if leaks:
            raise SystemExit(f"İndekstekine çok benzeyen değerlendirme vakası: {leaks}")
        (SEED / "eval_cases.json").write_text(json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Değerlendirme seti: {len(ev['cases'])} vaka → data/seed/eval_cases.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
