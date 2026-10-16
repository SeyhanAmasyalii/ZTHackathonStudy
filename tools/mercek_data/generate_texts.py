#!/usr/bin/env python3
"""Mercek sentetik verisi için doğal dil metinleri üretir (V4).

Üç tür metin: çağrı notları, çözüm kayıtları, geçmiş talep metinleri; ayrıca değerlendirme seti taslağı.

İki mod:
  foundry  (varsayılan) Azure AI Foundry'deki chat deploy'una 20'şerli partilerle istek atar.
  template (--template) İnternet ve Azure gerektirmeyen, şablonlarla deterministik üretim. Foundry hazır
           değilken V5–V6'nın beklememesi ve testler için. Gerçek metinler sonra üzerine yazılır.

Sonuç data/seed/texts.json'a yazılır ve commit'lenir. Tekrar çalıştırmada hazır olan konular atlanır
(--force ile baştan). Senaryonun kesin metinleri data/seed/fixed_texts.json'dadır; burada üretilmez.

Ortam değişkenleri (foundry modu):
  AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY (yoksa azure-identity ile Entra token),
  CHAT_DEPLOYMENT (varsayılan chat), AZURE_OPENAI_API_VERSION (varsayılan 2024-10-21)

Örnek:
  python3 tools/mercek_data/generate_texts.py --template
  python3 tools/mercek_data/generate_texts.py              # Foundry ile
  python3 tools/mercek_data/generate_texts.py --dry-run    # yalnızca planı yazdır
"""
from __future__ import annotations

import argparse
import json
import os
import random
import re
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[2]
SEED_DIR = ROOT / "data" / "seed"
PROMPTS_DIR = ROOT / "prompts"
CATALOG = SEED_DIR / "catalog.json"
FIXED = SEED_DIR / "fixed_texts.json"
OUTPUT = SEED_DIR / "texts.json"

BATCH = 20
MAX_DROP_RATIO = 0.20
MAX_RETRIES = 3

# ---------------------------------------------------------------------------
# Plan
# ---------------------------------------------------------------------------
CATEGORY_SCREEN = {
    "Fatura ödeme": "Fatura Ödeme",
    "Kredi": "Bireysel Kredi Kullandırım / Kredi Taksit Sorgulama",
    "Kart": "Kredi Kartı Başvurusu",
    "Hesap": "Vadesiz Hesap Açılışı / Havale ve EFT",
    "Müşteri bilgileri": "Müşteri Bilgi Güncelleme",
    "Diğer": "-",
}
FIXED_NOTE_KEYS = {"Fatura ödeme|abone numarası kabul edilmiyor"}  # elle yazılır, şablonla çoğaltılır
LARGE_NOTE_KEYS = {  # çok çağrı alan alt kategoriler: daha fazla çeşitlilik
    "Kredi|hatırlatma almadım / tarihi unuttum", "Kredi|gecikme faizi itirazı",
    "Kredi|taksit tutarı / tarih sorusu", "Kredi|erteleme / ödeme güçlüğü",
}
NOTES_DEFAULT, NOTES_LARGE, NOTES_FIXED_TARGET = 15, 30, 15
# Hata kodu: (adet, kaçınılacak kök nedenler)
SOLUTION_PLAN = {
    "INSTITUTION_TIMEOUT": (3, "kurum tarafında yavaşlama veya planlı bakım (SOL-031'de var)"),
    "VALIDATION_ERROR": (5, "-"),
    "AFFORDABILITY_EXCEEDED": (4, "-"),
    "INSUFFICIENT_INCOME": (4, "-"),
    "INSUFFICIENT_BALANCE": (4, "-"),
    "KYC_CHECK_FAILED": (4, "-"),
    "CORE_BANKING_TIMEOUT": (4, "-"),
    "SERVICE_UNAVAILABLE": (4, "-"),
    "DB_CONNECTION_ERROR": (4, "-"),
}
REQUEST_TYPES = [("mevcut ekran değişikliği", 55), ("yeni ekran", 20), ("batch işi", 15), ("karma", 10)]
REQUESTS_TARGET = 87  # + 8 elle yazılmış + 5 uygulamadaki TLP-1038…1042 ≈ 100
EVAL_GROUPS = {"match": 10, "no_match": 10, "request": 10}

FORBIDDEN = {
    "notes": [r"abone numaras\w* (uzunlu|hane)", r"\b13 hane"],
    "solutions": [r"abone numaras\w*", r"\bhane\b", r"\bhaneli\b"],
    "requests": [r"hatırlatma", r"erteleme", r"ertelen", r"abone numaras\w* (uzunlu|hane)"],
}
PII_PATTERNS = [r"\d{10,}", r"@", r"\+90", r"\bTR\d{2}\b", r"\b\d{11}\b"]


def note_forbidden(category: str, subcategory: str) -> str:
    topics = ["abone numarası uzunluğu"]
    if category == "Kredi" and "hatırlatma" not in subcategory:
        topics.append("hatırlatma mesajı")
    if category == "Kredi" and "erteleme" not in subcategory:
        topics.append("taksit erteleme")
    return ", ".join(topics)


# ---------------------------------------------------------------------------
# Filtreler
# ---------------------------------------------------------------------------
def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", text.lower())).strip()


def _similar(a: str, b: str) -> bool:
    wa, wb = set(_norm(a).split()), set(_norm(b).split())
    if not wa or not wb:
        return False
    return len(wa & wb) / len(wa | wb) >= 0.8


def text_of(item) -> str:
    if isinstance(item, str):
        return item
    return " ".join(str(v) if not isinstance(v, list) else " ".join(v) for v in item.values())


def clean(items: List, kind: str, existing: List) -> Tuple[List, int]:
    """Yasak konu, kişisel veri ve tekrar içeren metinleri atar. (kalanlar, atılan sayısı)"""
    kept: List = []
    dropped = 0
    pool = [text_of(x) for x in existing]
    for item in items:
        t = text_of(item)
        bad = any(re.search(p, t, re.IGNORECASE) for p in FORBIDDEN[kind] + PII_PATTERNS)
        dup = any(_similar(t, other) for other in pool)
        if bad or dup or len(t.split()) < 4:
            dropped += 1
            continue
        kept.append(item)
        pool.append(t)
    return kept, dropped


# ---------------------------------------------------------------------------
# Foundry istemcisi (standart kütüphane)
# ---------------------------------------------------------------------------
def load_prompt(name: str, variables: Dict[str, str]) -> List[Dict[str, str]]:
    raw = (PROMPTS_DIR / f"{name}.md").read_text(encoding="utf-8")
    system = raw.split("## system", 1)[1].split("## user", 1)[0].strip()
    user = raw.split("## user", 1)[1].strip()
    for k, v in variables.items():
        user = user.replace("{{" + k + "}}", str(v))
        system = system.replace("{{" + k + "}}", str(v))
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def _token() -> Tuple[str, str]:
    key = os.environ.get("AZURE_OPENAI_API_KEY")
    if key:
        return "api-key", key
    try:
        from azure.identity import DefaultAzureCredential  # isteğe bağlı bağımlılık
    except ImportError as exc:  # pragma: no cover
        raise SystemExit("AZURE_OPENAI_API_KEY yok ve azure-identity kurulu değil") from exc
    token = DefaultAzureCredential().get_token("https://cognitiveservices.azure.com/.default").token
    return "Authorization", f"Bearer {token}"


def foundry_complete(messages: List[Dict[str, str]], temperature: float = 0.8) -> str:
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
    if not endpoint:
        raise SystemExit("AZURE_OPENAI_ENDPOINT tanımlı değil (ya da --template kullanın)")
    deployment = os.environ.get("CHAT_DEPLOYMENT", "chat")
    version = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-10-21")
    url = f"{endpoint}/openai/deployments/{deployment}/chat/completions?api-version={version}"
    body = json.dumps({"messages": messages, "temperature": temperature,
                       "response_format": {"type": "json_object"}}).encode("utf-8")
    header, value = _token()
    for attempt in range(1, MAX_RETRIES + 1):
        req = urllib.request.Request(url, data=body, method="POST",
                                     headers={"Content-Type": "application/json", header: value})
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as err:
            if err.code in (429, 500, 502, 503, 504) and attempt < MAX_RETRIES:
                time.sleep(2 * attempt)
                continue
            raise
    raise RuntimeError("Foundry isteği başarısız")


def parse_items(content: str) -> List:
    data = json.loads(content)
    items = data.get("items", [])
    return items if isinstance(items, list) else []


# ---------------------------------------------------------------------------
# Şablon modu: deterministik, çevrimdışı
# ---------------------------------------------------------------------------
OPENERS = ["Müşteri", "Arayan müşteri", "Şubeye gelen müşteri", "Müşterimiz", "Bilgi almak için arayan müşteri"]
TAILS = ["Konuyla ilgili bilgi istedi.", "Geri dönüş bekliyor.", "Sorunun ne zaman çözüleceğini soruyor.",
         "Daha önce de aynı sorunu yaşadığını söyledi.", "Tekrar denemesi önerildi.", "Durumu not edildi.",
         "Sakin bir şekilde açıklama bekliyor.", "Acil olduğunu vurguladı.", "Şikâyetini kayda geçirmemizi istedi.",
         "Kendisine bilgi verildi, kayıt açıldı."]
SUB_PHRASES = {
    "kurumdan yanıt alınamadı": ["fatura sorgularken kurumdan yanıt gelmediğini", "ödeme sırasında işlemin zaman aşımına düştüğünü"],
    "abone numarası kabul edilmiyor": ["abone numarasını girdiğinde hata aldığını", "faturadaki numaranın sistemde geçersiz göründüğünü"],
    "fatura bulunamadı": ["sorguladığı faturanın listede çıkmadığını", "son dönem faturasının görünmediğini"],
    "mükerrer ödeme şüphesi": ["aynı faturayı iki kez ödemiş olabileceğini", "hesabından iki kez tahsilat yapıldığını düşündüğünü"],
    "dekont alınamadı": ["ödeme sonrası dekont alamadığını", "dekontun e-postasına gelmediğini"],
    "hatırlatma almadım / tarihi unuttum": ["taksit ödeme tarihini unuttuğunu", "ödeme gününden önce bilgilendirme almadığını"],
    "gecikme faizi itirazı": ["gecikme faizine itiraz ettiğini", "birkaç günlük gecikme için faiz yansıtılmasını haksız bulduğunu"],
    "taksit tutarı / tarih sorusu": ["bu ayki taksit tutarını öğrenmek istediğini", "taksit tarihinin hangi güne denk geldiğini"],
    "erteleme / ödeme güçlüğü": ["taksitlerini ödemekte zorlandığını", "ödemesini bir süre erteleme imkânı olup olmadığını"],
    "kullandırım yapılamadı": ["kredi kullandırım işleminin tamamlanmadığını", "kredi ekranında onay butonunun aktif olmadığını"],
    "erken kapama sorusu": ["kredisini erken kapatmak istediğini", "erken kapama tutarını öğrenmek istediğini"],
    "başvuru reddedildi": ["kart başvurusunun reddedildiğini", "başvurusunun neden onaylanmadığını"],
    "limit sorusu": ["kart limitinin düşük tanımlandığını", "onaylanan limitin talebinden az olduğunu"],
    "şifre belirleyemiyorum": ["kart şifresini belirleyemediğini", "şifre belirleme adımında SMS kodunun gelmediğini"],
    "ekstre görüntülenemiyor": ["kart ekstresini görüntüleyemediğini", "ekstre sayfasının boş açıldığını"],
    "kart teslim edilmedi": ["kartının hâlâ teslim edilmediğini", "kart teslimat durumunu öğrenmek istediğini"],
    "hesap açılamadı": ["vadesiz hesap açılışının tamamlanmadığını", "hesap açılışında onay adımında hata aldığını"],
    "havale/EFT gerçekleşmedi": ["gönderdiği EFT'nin karşı tarafa ulaşmadığını", "havale işleminin beklemede kaldığını"],
    "bakiye görünmüyor": ["hesap bakiyesinin güncel görünmediğini", "yatırdığı tutarın bakiyeye yansımadığını"],
    "IBAN hatası": ["alıcı IBAN'ını girerken hata aldığını", "kendi IBAN bilgisini bulamadığını"],
    "adres güncellenemiyor": ["adres bilgisini güncelleyemediğini", "yeni adresinin kaydedilmediğini"],
    "iletişim izni değiştirilemiyor": ["iletişim izinlerini değiştiremediğini", "SMS iznini kapatmak istediğini"],
    "kimlik doğrulama başarısız": ["kimlik doğrulamasının başarısız olduğunu", "güvenlik sorularında takıldığını"],
    "telefon numarası hatalı": ["kayıtlı telefon numarasının hatalı olduğunu", "eski numarasının sistemde durduğunu"],
    "genel bilgi talebi": ["ürünler hakkında genel bilgi istediğini", "şube çalışma saatlerini sorduğunu"],
    "şikâyet": ["hizmet kalitesinden memnun olmadığını", "bekleme süresinin uzun olduğunu"],
    "öneri": ["mobil uygulama için bir öneride bulunduğunu", "ekranların daha sade olmasını önerdiğini"],
}
VERBS = ["belirtti", "söyledi", "iletti", "aktardı", "bildirdi"]
DETAILS = ["İşlemi farklı kanallardan da denemiş.", "Sorun dün akşamdan beri sürüyormuş.", "Bu ay ilk kez yaşıyormuş.",
           "Mobil uygulamada da aynı durum varmış.", "Şubeye gitmek istemiyor.", "İşlemin bugün tamamlanması gerekiyormuş.",
           "Ekran görüntüsünü paylaşabileceğini söyledi.", "Önceki görüşmede bilgi verilmediğini düşünüyor.", "", ""]


def template_notes(rng: random.Random, category: str, sub: str, count: int, existing: List[str]) -> List[str]:
    phrases = SUB_PHRASES.get(sub, [f"{sub} konusunda sorun yaşadığını"])
    out: List[str] = []
    attempts = 0
    while len(out) < count and attempts < count * 40:
        attempts += 1
        text = f"{rng.choice(OPENERS)} {rng.choice(phrases)} {rng.choice(VERBS)}. {rng.choice(DETAILS)} {rng.choice(TAILS)}"
        text = re.sub(r"\s+", " ", text).strip()
        if not any(_similar(text, o) for o in existing + out):
            out.append(text)
    return out


SOLUTION_BANK = {
    "INSTITUTION_TIMEOUT": [("Kurum sertifikasının süresi dolmuş", "Kurum sertifikasını yenile ve bağlantıyı test et"),
                            ("Kurum servis adresi değişmiş", "Kurum entegrasyon yapılandırmasındaki adresi güncelle"),
                            ("Ağ geçidinde bağlantı havuzu dolmuş", "Bağlantı havuzu limitini artır ve boşta bağlantıları kapat")],
    "VALIDATION_ERROR": [("Tutar alanında ondalık ayırıcı hatalı", "Ondalık ayırıcıyı tr-TR biçimine göre normalize et"),
                         ("Zorunlu onay alanı istemciden gelmiyor", "İstemcide onay kutusunun forma bağlandığını kontrol et"),
                         ("E-posta alanında boşluk karakteri", "Girdiyi kırp ve biçim kontrolünü yeniden çalıştır"),
                         ("Telefon numarası farklı biçimde girilmiş", "Telefon numarasını standart uluslararası biçime normalize et"),
                         ("Tarih alanı yerel saat dilimiyle uyumsuz", "Tarihleri UTC'ye çevirip doğrula")],
    "AFFORDABILITY_EXCEEDED": [("Seçilen vadede taksit gelir sınırını aşıyor", "Daha uzun vade veya daha düşük tutar öner"),
                               ("Müşterinin güncel geliri sistemde eski", "Gelir bilgisini müşteri bilgi güncelleme ekranından güncelle"),
                               ("Ek gelir beyanı hesaba katılmamış", "Belgeli ek geliri müşteri kaydına ekle"),
                               ("Mevcut kredi taksitleri sınırı dolduruyor", "Toplam borç yükünü müşteriyle birlikte değerlendir")],
    "INSUFFICIENT_INCOME": [("Seçilen kart tipinin gelir şartı karşılanmıyor", "Bir alt kart tipini öner"),
                            ("Gelir bilgisi eksik girilmiş", "Gelir alanını doğrula ve başvuruyu yenile"),
                            ("Emekli maaşı gelir olarak tanımlanmamış", "Gelir türünü müşteri kaydında düzelt"),
                            ("Gelir aylık yerine yıllık girilmiş", "Gelir alanının aylık olduğunu müşteriye açıkla")],
    "INSUFFICIENT_BALANCE": [("Hesapta bloke tutar var", "Bloke tutarları kontrol et ve kullanılabilir bakiyeyi açıkla"),
                             ("Yanlış hesap seçilmiş", "Müşterinin başka bir hesap seçmesini öner"),
                             ("Gün içi limit dolmuş", "Günlük işlem limitini kontrol et"),
                             ("Döviz hesabından TL ödeme denenmiş", "Uygun para birimindeki hesabı seçtir")],
    "KYC_CHECK_FAILED": [("Kimlik bilgisi güncel değil", "Müşteriyi kimlik güncellemesi için şubeye yönlendir"),
                         ("Güvenlik sorusu cevabı eşleşmiyor", "Alternatif doğrulama yöntemine geç"),
                         ("SMS doğrulama kodu süresi dolmuş", "Yeni kod gönder ve süreyi müşteriye açıkla"),
                         ("Kayıtlı telefon numarası değişmiş", "Telefon güncellemesi için kimlik doğrulamalı akışı başlat")],
    "CORE_BANKING_TIMEOUT": [("Ana bankacılık sisteminde gün sonu işlemi sürüyor", "Gün sonu takvimini kontrol et, işlemi sonra tekrarla"),
                             ("Uzun süren sorgu kilitlenmesi", "Kilitlenen oturumları tespit edip sonlandır"),
                             ("Zaman aşımı eşiği düşük tanımlı", "İşlem tipine göre zaman aşımı eşiğini gözden geçir"),
                             ("Kuyrukta biriken istekler", "Kuyruk derinliğini izle ve tüketici sayısını artır")],
    "SERVICE_UNAVAILABLE": [("Yeni sürüm dağıtımı sırasında servis kapalı", "Dağıtım takvimini kontrol et, kademeli dağıtıma geç"),
                            ("Sağlık kontrolü başarısız olan örnek trafikte", "Başarısız örneği trafikten çıkar"),
                            ("Bağımlı servis yanıt vermiyor", "Bağımlı servisin durumunu kontrol et ve devre kesiciyi etkinleştir"),
                            ("Bellek sınırına ulaşan servis yeniden başlıyor", "Bellek kullanımını incele ve sınırı ayarla")],
    "DB_CONNECTION_ERROR": [("Veritabanı bağlantı havuzu tükenmiş", "Havuz boyutunu artır ve sızan bağlantıları kapat"),
                            ("Veritabanı parolası yenilenmiş", "Gizli anahtar deposundaki bağlantı bilgisini güncelle"),
                            ("Ağ güvenlik kuralı değişmiş", "Güvenlik duvarı kuralını kontrol et"),
                            ("Veritabanı bakım modunda", "Bakım penceresini kontrol et, işlemi sonra tekrarla")],
}


def template_solutions(error_code: str, count: int, hint: str) -> List[Dict]:
    out = []
    for root, fix in SOLUTION_BANK[error_code][:count]:
        out.append({"title": root, "symptom": hint, "root_cause": root,
                    "steps": ["İlgili logları trace.id ile incele.", fix + ".", "İşlemi tekrarlayarak sonucu doğrula.",
                              "Müşteriye veya temsilciye sonucu bildir."]})
    return out


REQUEST_FEATURES = {
    "mevcut ekran değişikliği": ["{screen} ekranına filtreleme seçeneği eklensin", "{screen} ekranında sonuçlar dışa aktarılabilsin",
                                 "{screen} ekranına açıklama alanı eklensin", "{screen} ekranında zorunlu alan kontrolleri iyileştirilsin",
                                 "{screen} ekranında işlem geçmişi gösterilsin", "{screen} ekranına yetki bazlı görünürlük eklensin",
                                 "{screen} ekranında varsayılan değerler müşteri profiline göre gelsin",
                                 "{screen} ekranının mobil görünümü iyileştirilsin"],
    "yeni ekran": ["{module} modülüne toplu işlem takibi için yeni ekran", "{module} modülünde onay bekleyen işlemler ekranı",
                   "{module} modülü için yönetici özet ekranı", "{module} modülünde istisna kayıtlarını izleme ekranı"],
    "batch işi": ["{module} verileri için gece çalışan mutabakat işi", "{module} işlemleri için haftalık yönetim raporu işi",
                  "{module} kayıtlarında eksik bilgi tespit işi", "{module} için günlük kalite kontrol raporu"],
    "karma": ["{screen} ekranına buton ve arka planda günlük işlem", "{screen} ekranına uyarı alanı ve haftalık özet raporu"],
}
WHY = ["Operasyon ekibinin iş yükünü azaltmak istiyoruz.", "Müşteri şikâyetlerinde bu ihtiyaç sık geçiyor.",
       "Denetim bulgusu kapsamında gerekiyor.", "Şubelerden bu konuda çok talep geliyor.", "Raporlama sürecini hızlandırmak istiyoruz.",
       "Hatalı işlem sayısını azaltmayı hedefliyoruz."]


def template_requests(rng: random.Random, plan: List[Tuple[str, str, str]], existing: List[Dict]) -> List[Dict]:
    out: List[Dict] = []
    for module, screen, rtype in plan:
        for _ in range(20):
            title = rng.choice(REQUEST_FEATURES[rtype]).format(screen=screen, module=module)
            desc = f"{title}. {rng.choice(WHY)}"
            if not any(_similar(desc, text_of(o)) for o in existing + out):
                out.append({"module": module, "screen": screen, "type": rtype, "title": title, "description": desc})
                break
    return out


# ---------------------------------------------------------------------------
# Üretim akışı
# ---------------------------------------------------------------------------
def load_json(path: Path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def request_plan(rng: random.Random, catalog: Dict, count: int) -> List[Tuple[str, str, str]]:
    screens = [(s["module"], s["name"]) for s in catalog["screens"]]
    plan = []
    for _ in range(count):
        module, name = rng.choice(screens)
        rtype = rng.choices([t for t, _ in REQUEST_TYPES], weights=[w for _, w in REQUEST_TYPES])[0]
        plan.append((module, name, rtype))
    return plan


def generate_batch(kind: str, prompt: str, variables: Dict, want: int, existing: List,
                   complete: Callable[[List[Dict[str, str]]], str]) -> List:
    """Foundry'den 20'şerli parti ister; atılan oranı %20'yi geçerse partiyi bir kez daha üretir."""
    got: List = []
    while len(got) < want:
        n = min(BATCH, want - len(got))
        for _attempt in range(2):
            items = parse_items(complete(load_prompt(prompt, {**variables, "count": n})))
            kept, dropped = clean(items, kind, existing + got)
            if items and dropped / len(items) <= MAX_DROP_RATIO:
                break
        got += kept[:n]
        if not kept:
            break
    return got


def run(template: bool, force: bool, seed: int, complete: Optional[Callable] = None,
        output: Path = OUTPUT, dry_run: bool = False) -> Dict:
    rng = random.Random(seed)
    catalog = load_json(CATALOG, None)
    fixed = load_json(FIXED, {})
    texts = {} if force else load_json(output, {})
    texts.setdefault("incident_notes", {})
    texts.setdefault("solutions", {})
    texts.setdefault("requests", [])
    texts.setdefault("eval_drafts", {})
    complete = complete or foundry_complete
    hints: Dict[str, str] = {}
    for r in catalog["error_rules"]:
        hints.setdefault(r["error_code"], r["explanation_hint"])
    services = {s["service_id"]: s["name"] for s in catalog["services"]}
    rule_service = {r["error_code"]: services.get(r["service_id"] or "", "ekranın ana servisi") for r in catalog["error_rules"]}
    rule_screen = {r["error_code"]: r["screen_code"] for r in catalog["error_rules"]}

    plan_lines = []
    # 1) Çağrı notları
    for cat in catalog["incident_categories"]:
        for sub in cat["subcategories"]:
            key = f"{cat['category']}|{sub}"
            target = NOTES_FIXED_TARGET if key in FIXED_NOTE_KEYS else NOTES_LARGE if key in LARGE_NOTE_KEYS else NOTES_DEFAULT
            have = texts["incident_notes"].get(key, [])
            if key in FIXED_NOTE_KEYS:
                have = list(dict.fromkeys(fixed.get("incident_notes", {}).get(key, []) + have))
            missing = target - len(have)
            plan_lines.append(f"not  {key}: {len(have)}/{target}")
            if missing <= 0 or dry_run:
                texts["incident_notes"][key] = have
                continue
            institution = "İSKİ" if key in FIXED_NOTE_KEYS else ("çeşitli fatura kurumları" if cat["category"] == "Fatura ödeme" else "-")
            if template or key in FIXED_NOTE_KEYS:
                new = template_notes(rng, cat["category"], sub, missing, have)
            else:
                new = generate_batch("notes", "gen-cagri-notu",
                                     {"category": cat["category"], "subcategory": sub,
                                      "screen_name": CATEGORY_SCREEN.get(cat["category"], "-"),
                                      "institution": institution,
                                      "forbidden_topics": note_forbidden(cat["category"], sub)},
                                     missing, have, complete)
            texts["incident_notes"][key] = have + new

    # 2) Çözümler (SOL-031 elle; burada üretilmez)
    for code, (target, avoid) in SOLUTION_PLAN.items():
        have = texts["solutions"].get(code, [])
        missing = target - len(have)
        plan_lines.append(f"çözüm {code}: {len(have)}/{target}")
        if missing <= 0 or dry_run:
            continue
        if template:
            new = template_solutions(code, target, hints.get(code, ""))[len(have):]
        else:
            new = generate_batch("solutions", "gen-cozum",
                                 {"error_code": code, "error_hint": hints.get(code, ""),
                                  "service_name": rule_service.get(code, "-"), "screen_code": rule_screen.get(code, "*"),
                                  "avoid_root_causes": avoid}, missing, have, complete)
        texts["solutions"][code] = have + new

    # 3) Talepler (D ve E'nin benzer talepleri elle; burada üretilmez)
    have_r = texts["requests"]
    missing_r = REQUESTS_TARGET - len(have_r)
    plan_lines.append(f"talep: {len(have_r)}/{REQUESTS_TARGET}")
    if missing_r > 0 and not dry_run:
        plan = request_plan(rng, catalog, missing_r)
        if template:
            texts["requests"] = have_r + template_requests(rng, plan, have_r)
        else:
            new_r: List[Dict] = []
            groups: Dict[Tuple[str, str, str], int] = {}
            for p in plan:
                groups[p] = groups.get(p, 0) + 1
            for (module, screen, rtype), n in groups.items():
                items = generate_batch("requests", "gen-talep",
                                       {"module": module, "screen_name": screen, "request_type": rtype,
                                        "forbidden_topics": "taksit hatırlatma, taksit erteleme"}, n, have_r + new_r, complete)
                new_r += [{"module": module, "screen": screen, "type": rtype, **i} for i in items]
            texts["requests"] = have_r + new_r

    # 4) Değerlendirme seti taslağı (V6'da beklenen değerlerle tamamlanır, elle gözden geçirilir)
    drafts = texts["eval_drafts"]
    if not dry_run:
        if len(drafts.get("match", [])) < EVAL_GROUPS["match"]:
            codes = [c for c in SOLUTION_PLAN if c != "INSTITUTION_TIMEOUT"]
            drafts["match"] = [{"error_code": c, "draft": f"Temsilci: {SOLUTION_BANK[c][i % 2][0].lower()} gibi görünen bir sorun bildirildi."}
                               for i, c in enumerate((codes * 2)[:EVAL_GROUPS["match"]])]
        if len(drafts.get("no_match", [])) < EVAL_GROUPS["no_match"]:
            new_issues = ["Kart ekstresinde yabancı para harcamaları iki kez listeleniyor", "Vadeli hesapta faiz tahakkuku bir gün kaymış",
                          "Mobil uygulamada karanlık modda tutar alanı okunmuyor", "Vergi ödemede plaka alanı küçük harf kabul etmiyor",
                          "Hesap hareketleri raporunda tarih filtresi hafta sonunu atlıyor", "Kart şifre belirlemede SMS kodu Türkçe karakterli geliyor",
                          "Bakiye sorgulamada altın hesabı gram yerine kilo gösteriyor", "Kimlik doğrulamada yeni kimlik kartı seri numarası reddediliyor",
                          "İletişim izinleri raporunda il filtresi boş dönüyor", "Havale ekranında alıcı adı uzun olunca kesiliyor"]
            drafts["no_match"] = [{"draft": t} for t in new_issues[:EVAL_GROUPS["no_match"]]]
        if len(drafts.get("request", [])) < EVAL_GROUPS["request"]:
            drafts["request"] = [{"draft": r["description"], "type": r["type"], "screen": r["screen"]}
                                 for r in rng.sample(texts["requests"], min(EVAL_GROUPS["request"], len(texts["requests"])))]
    texts["eval_drafts"] = drafts

    texts["meta"] = {"mode": "template" if template else "foundry",
                     "deployment": None if template else os.environ.get("CHAT_DEPLOYMENT", "chat"),
                     "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "seed": seed,
                     "counts": {"incident_notes": sum(len(v) for v in texts["incident_notes"].values()),
                                "solutions": sum(len(v) for v in texts["solutions"].values()),
                                "requests": len(texts["requests"]),
                                "eval_drafts": sum(len(v) for v in texts["eval_drafts"].values())}}
    if dry_run:
        print("\n".join(plan_lines))
        return texts
    output.write_text(json.dumps(texts, ensure_ascii=False, indent=2), encoding="utf-8")
    return texts


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Mercek doğal dil metinleri (V4)")
    p.add_argument("--template", action="store_true", help="Foundry olmadan şablonlarla üret")
    p.add_argument("--force", action="store_true", help="Var olan texts.json'u yok sayıp baştan üret")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--output", default=str(OUTPUT))
    p.add_argument("--dry-run", action="store_true", help="Yalnızca planı ve mevcut durumu yazdır")
    args = p.parse_args(argv)
    texts = run(args.template, args.force, args.seed, output=Path(args.output), dry_run=args.dry_run)
    if not args.dry_run:
        c = texts["meta"]["counts"]
        print(f"{args.output} ({texts['meta']['mode']}): çağrı notu {c['incident_notes']} · çözüm {c['solutions']} "
              f"(+ SOL-031 elle) · talep {c['requests']} (+ 8 elle) · değerlendirme taslağı {c['eval_drafts']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
