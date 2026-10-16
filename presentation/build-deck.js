// Mercek — hackathon sunumu (.pptx, 16:9). Çalıştırma: node build-deck.js
const path = require("path");
const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const fa = require("react-icons/fa");
const { applyTheme } = require("/mnt/skills/public/pptx/scripts/apply_theme.js");

const OUT = path.join(__dirname, "Mercek_AI_Overflow_Sunum.pptx");
const IMG = (f) => path.join(__dirname, "mockups", f);

const THEME = {
  name: "Mercek",
  headFontFace: "Calibri",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "17202A", lt1: "FFFFFF", dk2: "2B3A67", lt2: "F4F6F8",
    accent1: "E8A33D", accent2: "2A9D8F", accent3: "E76F51",
    accent4: "2B3A67", accent5: "5B6673", accent6: "C8424B",
    hlink: "2A9D8F", folHlink: "2B3A67",
  },
};
const HEX = THEME.colors;

async function icon(Comp, color, size = 256) {
  const svg = ReactDOMServer.renderToStaticMarkup(React.createElement(Comp, { color: "#" + color, size: String(size) }));
  const buf = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + buf.toString("base64");
}

(async () => {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5
  pres.title = "Mercek — AI Overflow";
  pres.author = "AI Overflow";
  pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
  const C = pres.SchemeColor;
  const W = 13.333;

  // ---------- Layouts ----------
  pres.defineSlideMaster({
    title: "DARK",
    background: { color: C.text1 },
    objects: [],
  });
  pres.defineSlideMaster({
    title: "CONTENT",
    background: { color: C.background1 },
    margin: [0.5, 0.6, 0.6, 0.6],
    objects: [
      { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.35, w: W - 1.2, h: 0.9,
          fontSize: 36, bold: true, color: C.text1, valign: "middle", margin: 0 }, text: "" } },
      { text: { text: "AI Overflow · Mercek", options: { x: 0.6, y: 7.0, w: 4, h: 0.3, fontSize: 10, color: C.accent5, margin: 0 } } },
    ],
    slideNumber: { x: W - 1.1, y: 7.0, w: 0.5, h: 0.3, fontSize: 10, color: C.accent5, align: "right" },
  });

  const ic = {
    user: await icon(fa.FaUser, HEX.dk2),
    userW: await icon(fa.FaUser, HEX.lt1),
    headset: await icon(fa.FaHeadset, HEX.lt1),
    clip: await icon(fa.FaClipboardList, HEX.lt1),
    bolt: await icon(fa.FaBolt, HEX.lt1),
    code: await icon(fa.FaCode, HEX.lt1),
    sync: await icon(fa.FaSyncAlt, HEX.lt1),
    shield: await icon(fa.FaShieldAlt, HEX.lt1),
    quote: await icon(fa.FaQuoteLeft, HEX.accent1),
    unlink: await icon(fa.FaUnlink, HEX.lt1),
    brain: await icon(fa.FaUserFriends, HEX.lt1),
    eye: await icon(fa.FaEyeSlash, HEX.lt1),
    github: await icon(fa.FaGithub, HEX.dk1),
    githubW: await icon(fa.FaGithub, HEX.lt1),
    check: await icon(fa.FaCheckCircle, HEX.lt1),
    warn: await icon(fa.FaExclamationTriangle, HEX.lt1),
    route: await icon(fa.FaRoute, HEX.lt1),
    globe: await icon(fa.FaGlobe, HEX.lt1),
    video: await icon(fa.FaVideo, HEX.lt1),
    users: await icon(fa.FaUsers, HEX.dk2),
    headsetD: await icon(fa.FaHeadset, HEX.dk2),
    clipD: await icon(fa.FaClipboardList, HEX.dk2),
    chart: await icon(fa.FaChartLine, HEX.dk2),
  };

  const iconCircle = (slide, x, y, d, fill, img, name) => {
    slide.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: fill }, line: { color: fill }, objectName: name + "-circle" });
    const p = d * 0.26;
    slide.addImage({ data: img, x: x + p, y: y + p, w: d - 2 * p, h: d - 2 * p, objectName: name + "-icon" });
  };
  const card = (slide, x, y, w, h, fill, name, lineColor) =>
    slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.12, fill: { color: fill },
      line: { color: lineColor || fill, width: 1 }, objectName: name });
  const lens = (slide, cx, cy, r) => {
    slide.addShape(pres.shapes.OVAL, { x: cx - r, y: cy - r, w: 2 * r, h: 2 * r, fill: { type: "none" }, line: { color: C.accent1, width: 6 }, objectName: "lens-outer" });
    const r2 = r * 0.62;
    slide.addShape(pres.shapes.OVAL, { x: cx - r2, y: cy - r2, w: 2 * r2, h: 2 * r2, fill: { type: "none" }, line: { color: C.accent2, width: 3 }, objectName: "lens-inner" });
    const r3 = r * 0.22;
    slide.addShape(pres.shapes.OVAL, { x: cx - r3, y: cy - r3, w: 2 * r3, h: 2 * r3, fill: { color: C.accent1 }, line: { color: C.accent1 }, objectName: "lens-core" });
  };
  const draftNote = (slide, x, y, w) => slide.addText("Taslak görsel — gerçek ekran görüntüsüyle değiştirilecek",
    { x, y, w, h: 0.28, fontSize: 10, italic: true, color: C.accent5, margin: 0, isTextBox: true, objectName: "draft-note" });

  // ---------- 1. Kapak ----------
  pres.addSection({ title: "Açılış" });
  let s = pres.addSlide({ masterName: "DARK", sectionTitle: "Açılış" });
  s.addText("ZİRAAT TEKNOLOJİ YAPAY ZEKA HACKATHONU · TEMA 2", { x: 0.8, y: 1.55, w: 7.4, h: 0.4, fontSize: 14, bold: true, color: C.accent1, charSpacing: 3, margin: 0, isTextBox: true });
  s.addText("Mercek", { x: 0.8, y: 2.05, w: 7.4, h: 1.5, fontSize: 88, bold: true, color: C.background1, margin: 0, isTextBox: true });
  s.addText("Soruna odaklanır, çözümü netleştirir.", { x: 0.8, y: 3.6, w: 7.4, h: 0.7, fontSize: 28, italic: true, color: C.background2, margin: 0, isTextBox: true });
  s.addText("AI Overflow takımı", { x: 0.8, y: 5.25, w: 7.4, h: 0.45, fontSize: 20, bold: true, color: C.background1, margin: 0, isTextBox: true });
  s.addText("17 Ekim 2026", { x: 0.8, y: 5.7, w: 7.4, h: 0.4, fontSize: 16, color: C.background2, margin: 0, isTextBox: true });
  lens(s, 10.35, 3.75, 2.25);
  s.addNotes("0:00–0:10 · Merhaba, biz AI Overflow. Projemizin adı Mercek: soruna odaklanır, çözümü netleştirir.");

  // ---------- 2. Takım ----------
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Açılış" });
  s.addText("AI Overflow takımı", { placeholder: "title" });
  for (let i = 0; i < 5; i++) {
    const x = 0.6 + i * 2.47, y = 1.75, w = 2.27, h = 4.35;
    card(s, x, y, w, h, C.background2, `team-card-${i + 1}`);
    s.addShape(pres.shapes.OVAL, { x: x + w / 2 - 0.65, y: y + 0.4, w: 1.3, h: 1.3, fill: { color: C.background1 }, line: { color: C.accent1, width: 3 }, objectName: `team-photo-${i + 1}` });
    s.addImage({ data: ic.user, x: x + w / 2 - 0.3, y: y + 0.75, w: 0.6, h: 0.6, objectName: `team-photo-icon-${i + 1}` });
    s.addText([
      { text: "Ad Soyad", options: { fontSize: 18, bold: true, color: C.text1, breakLine: true } },
      { text: "Birim", options: { fontSize: 14, color: C.accent5, breakLine: true } },
      { text: " ", options: { fontSize: 8, breakLine: true } },
      { text: "Projedeki rolü", options: { fontSize: 14, color: C.text2 } },
    ], { x: x + 0.15, y: y + 1.95, w: w - 0.3, h: 2.1, align: "center", valign: "top", margin: 0, isTextBox: true, objectName: `team-text-${i + 1}` });
  }
  s.addText("Sorumluluklar 19 maddelik listeden herkesin kendi seçimiyle dağıtıldı.", { x: 0.6, y: 6.3, w: 12, h: 0.4, fontSize: 14, color: C.accent5, margin: 0, isTextBox: true });
  s.addNotes("0:10–0:20 · Takımı tek cümleyle tanıtın. (Ad, birim ve rolleri doldurun; fotoğraf eklenecekse daire içine yerleştirin.)");


  // ---------- 3. Problem ----------
  pres.addSection({ title: "Problem ve çözüm" });
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Problem ve çözüm" });
  s.addText("Hata mı, kural mı? Bilinmeyince çağrı açılıyor", { placeholder: "title" });
  card(s, 0.6, 1.6, 3.5, 4.95, C.text2, "quote-card");
  s.addImage({ data: ic.quote, x: 0.95, y: 1.95, w: 0.55, h: 0.55, objectName: "quote-icon" });
  s.addText("“Ekran ‘kullandırılamaz’ diyor. Sistem mi bozuk?”", { x: 0.95, y: 2.65, w: 2.9, h: 2.2, fontSize: 24, italic: true, bold: true, color: C.background1, margin: 0, valign: "top", isTextBox: true });
  s.addText("Elif, şube müşteri temsilcisi · KRDTKULL", { x: 0.95, y: 5.6, w: 2.9, h: 0.7, fontSize: 14, color: C.background2, margin: 0, valign: "bottom", isTextBox: true });

  const steps = ["Temsilci uyarıyı görür", "Çağrı açar", "L1 Kibana'da log arar", "L2 kurumu ve kodu inceler", "Yeni talep bu sorunlardan habersiz planlanır"];
  steps.forEach((t, i) => {
    const x = 4.45 + i * 1.66, y = 1.6, w = 1.5, h = 1.9;
    card(s, x, y, w, h, C.background2, `flow-step-${i + 1}`);
    s.addShape(pres.shapes.OVAL, { x: x + 0.15, y: y + 0.15, w: 0.45, h: 0.45, fill: { color: C.accent3 }, line: { color: C.accent3 }, objectName: `flow-num-${i + 1}` });
    s.addText(String(i + 1), { x: x + 0.15, y: y + 0.15, w: 0.45, h: 0.45, fontSize: 14, bold: true, color: C.background1, align: "center", valign: "middle", margin: 0, isTextBox: true });
    s.addText(t, { x: x + 0.15, y: y + 0.7, w: w - 0.3, h: 1.1, fontSize: 13, color: C.text1, valign: "top", margin: 0, isTextBox: true });
  });
  s.addText([{ text: "Bedeli: ", options: { bold: true } }, { text: "işlem yapamayan müşteri · gereksiz çağrılar · aynı kurum sorunu için onlarca kayıt · veriden kopuk planlanan talepler" }],
    { x: 4.45, y: 3.58, w: 8.2, h: 0.6, fontSize: 14, color: C.accent3, margin: 0, valign: "top", isTextBox: true });

  const pains = [
    [ic.eye, "Hata mı kural mı belli değil", "İş kuralı reddi ekranda teknik hatadan ayrılamıyor."],
    [ic.brain, "Aynı sorun, onlarca çağrı", "Kurum kaynaklı sorunda her arama ayrı kayıt; çözüm kişilerde."],
    [ic.unlink, "Talepler veriden kopuk", "Efor toplantıda; erişim ve kapasite sorunları geç fark ediliyor."],
  ];
  pains.forEach(([img, h1, d], i) => {
    const x = 4.45 + i * 2.78, y = 4.3;
    iconCircle(s, x, y, 0.6, C.text2, img, `pain-${i + 1}`);
    s.addText([{ text: h1, options: { bold: true, fontSize: 16, breakLine: true } }, { text: d, options: { fontSize: 14, color: C.accent5 } }],
      { x, y: y + 0.75, w: 2.6, h: 1.5, valign: "top", color: C.text1, margin: 0, isTextBox: true });
  });
  s.addNotes("0:20–0:40 · Şube personeli işlem yapamadığında hata mı kural mı bilemiyor, çağrı açıyor. L1 ve L2 Kibana'da log arıyor, aynı kurum sorunu için onlarca çağrı açılıyor, bilinen çözümler kişilerde kalıyor. Yeni talepler de bu sorunlardan habersiz planlanıyor.");

  // ---------- 4. Çözüm ----------
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Problem ve çözüm" });
  s.addText("Mercek: sorundan plana tek akış", { placeholder: "title" });
  s.addText("Banka çalışanlarının ekranlarda yaşadığı sorunu loglardan, çağrı geçmişinden ve koddan açıklar; çağrıları doğru servise yönlendirip birleştirir ve iş birimi taleplerini servis bazlı efor ve takvimle plana dönüştürür.",
    { x: 0.6, y: 1.35, w: 12.1, h: 0.85, fontSize: 17, color: C.text2, margin: 0, valign: "top", isTextBox: true });
  const mods = [
    [C.accent2, ic.headset, "Akıllı Problem Çözüm ve Çağrı Yönetimi", ["Ekran bağlamıyla logu bulur, iş kuralını hatadan ayırır", "Çağrıyı servise atar, mükerrerleri ana kayda bağlar", "Geçmiş çözümü bulur; yoksa duyuruya ve koda bakar"]],
    [C.accent1, ic.clip, "Akıllı Talep Analizi, Efor ve Takvim", ["Talebi bileşenlere ayırır, ekranları ve servisleri bulur", "Benzer taleplerden adam-gün, servis takviminden plan", "Çağrı ve müşteri verisiyle kapsamı düzeltir"]],
  ];
  mods.forEach(([col, img, head, items], i) => {
    const x = 0.6 + i * 6.6, y = 2.35, w = 5.5, h = 3.05;
    card(s, x, y, w, h, C.background2, `module-card-${i + 1}`);
    iconCircle(s, x + 0.3, y + 0.3, 0.75, col, img, `module-${i + 1}`);
    s.addText(head, { x: x + 1.25, y: y + 0.3, w: w - 1.5, h: 0.75, fontSize: 20, bold: true, color: C.text1, valign: "middle", margin: 0, isTextBox: true });
    s.addText(items.map((t, k) => ({ text: t, options: { bullet: true, breakLine: k < items.length - 1 } })),
      { x: x + 0.3, y: y + 1.25, w: w - 0.6, h: 1.6, fontSize: 15, color: C.text1, paraSpaceAfter: 6, valign: "top", margin: 0, isTextBox: true });
  });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.15, y: 3.35, w: 1.0, h: 1.05, rectRadius: 0.15, fill: { color: C.text1 }, line: { color: C.text1 }, objectName: "bridge-pill" });
  s.addText([{ text: "veri", options: { breakLine: true } }, { text: "→", options: { breakLine: true } }, { text: "kapsam" }], { x: 6.15, y: 3.35, w: 1.0, h: 1.05, fontSize: 12, bold: true, color: C.accent1, align: "center", valign: "middle", margin: 0, isTextBox: true });
  s.addText("Kullanıcılar", { x: 0.6, y: 5.75, w: 2.3, h: 0.5, fontSize: 16, bold: true, color: C.text1, valign: "middle", margin: 0, isTextBox: true });
  const users = [[ic.users, "Şube, çağrı merkezi"], [ic.headsetD, "L2, platform"], [ic.chart, "İş birimleri"], [ic.clipD, "İş analisti"]];
  users.forEach(([img, t], i) => {
    const x = 2.9 + i * 2.45, y = 5.7;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: 2.25, h: 0.6, rectRadius: 0.3, fill: { color: C.background2 }, line: { color: C.background2 }, objectName: `user-chip-${i + 1}` });
    s.addImage({ data: img, x: x + 0.2, y: y + 0.15, w: 0.3, h: 0.3 });
    s.addText(t, { x: x + 0.6, y, w: 1.6, h: 0.6, fontSize: 13, color: C.text1, valign: "middle", margin: 0, isTextBox: true });
  });
  s.addNotes("0:40–0:50 · Tek cümle çözüm. İki modül ve köprü: loglar, çağrı ve müşteri verisi talep kapsamına giriyor. Mercek'i müşteri değil banka çalışanları kullanıyor.");

  // ---------- 5. Yenilikçilik ----------
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Problem ve çözüm" });
  s.addText("Dört farkımız", { placeholder: "title" });
  s.addText("Bugünkü araçlar sorunu kaydeder; Mercek sorunu açıklar, kaynağına bağlar ve yeni talebin planına taşır.",
    { x: 0.6, y: 1.3, w: 12.1, h: 0.45, fontSize: 18, color: C.text2, margin: 0, valign: "middle", isTextBox: true });
  const diffs = [
    [C.accent1, ic.bolt, "Bağlamı bilir", "Ekran kodu, son işlemin logu ve temsilcinin cümlesiyle çalışır; kullanıcı yazmadan açıklar ve ekranı doğru değerlerle doldurur."],
    [C.accent2, ic.code, "Üç kaynağı birleştirir", "Log (ne oluyor), kurum duyurusu (neden) ve uygulama kodu (nerede düzeltilir) tek analizde."],
    [C.text2, ic.sync, "Kapalı döngü", "Çağrı ve müşteri verisi, talebin değerini kanıtlar ve eksik kapsamı talep anında gösterir."],
    [C.accent3, ic.shield, "Güvenilir AI", "Hesabı kod yapar, AI açıklar. Eşik altında öneri yok; her rakam ve kod satırı doğrulanır."],
  ];
  diffs.forEach(([col, img, head, desc], i) => {
    const x = 0.6 + (i % 2) * 6.25, y = 1.95 + Math.floor(i / 2) * 2.45, w = 5.85, h = 2.2;
    card(s, x, y, w, h, C.background2, `diff-card-${i + 1}`);
    iconCircle(s, x + 0.35, y + 0.4, 0.85, col, img, `diff-${i + 1}`);
    s.addText([{ text: head, options: { fontSize: 22, bold: true, color: C.text1, breakLine: true } }, { text: desc, options: { fontSize: 15, color: C.text2 } }],
      { x: x + 1.5, y: y + 0.35, w: w - 1.8, h: h - 0.6, valign: "top", margin: 0, paraSpaceAfter: 4, isTextBox: true });
  });
  s.addNotes("0:50–0:58 · Mercek çağrıyı kaydetmekle kalmıyor: açıklıyor, birleştiriyor, koda bağlıyor ve talebi gerekçelendiriyor. AI'ın rolü sınırlı ve denetlenebilir.");

  // ---------- 6. Mimari ----------
  pres.addSection({ title: "Ürün" });
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Ürün" });
  s.addText("Mimari: Azure üzerinde uçtan uca", { placeholder: "title" });
  const box = (x, y, w, h, fill, head, sub, name, dark) => {
    card(s, x, y, w, h, fill, name, dark ? fill : C.accent5);
    s.addText([{ text: head, options: { bold: true, fontSize: 15, breakLine: true } }, { text: sub, options: { fontSize: 12 } }],
      { x: x + 0.12, y: y + 0.08, w: w - 0.24, h: h - 0.16, color: dark ? C.background1 : C.text1, valign: "middle", align: "center", margin: 0, isTextBox: true });
  };
  box(0.6, 2.35, 1.9, 2.6, C.background2, "Kullanıcılar", "Şube, çağrı merkezi\nL2 destek\nİş birimi, analist", "arch-users");
  box(3.0, 1.45, 2.55, 1.7, C.text2, "App Service · web", "Next.js 16\nBankacılık ekranları,\nMercek, Talep Yönlendirme", "arch-web", true);
  box(3.0, 4.15, 2.55, 1.7, C.text2, "App Service · api", "FastAPI\n/api/health · orkestrasyon,\nhesap ve doğrulama", "arch-api", true);
  box(6.0, 1.45, 2.75, 1.35, C.background2, "Azure AI Foundry", "chat + embedding modeli", "arch-foundry");
  box(6.0, 2.97, 2.75, 1.35, C.background2, "Azure SQL", "Log, katalog, portföy,\nçağrı, talep, takvim", "arch-sql");
  box(6.0, 4.49, 2.75, 1.35, C.background2, "Azure AI Search", "Çözüm, talep, duyuru\nhibrit arama", "arch-search");
  const arrow = (x1, y1, x2, y2, name) => s.addShape(pres.shapes.LINE, { x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1) || 0.001, h: Math.abs(y2 - y1) || 0.001,
    flipV: y2 < y1, line: { color: C.accent5, width: 2, endArrowType: "triangle" }, objectName: name });
  arrow(2.5, 3.0, 3.0, 2.3, "arrow-users-web");
  arrow(4.275, 3.15, 4.275, 4.15, "arrow-web-api");
  arrow(5.55, 4.6, 6.0, 2.12, "arrow-api-foundry");
  arrow(5.55, 4.85, 6.0, 3.64, "arrow-api-sql");
  arrow(5.55, 5.1, 6.0, 5.16, "arrow-api-search");
  card(s, 0.6, 6.05, 8.15, 0.8, C.background2, "arch-cicd");
  s.addImage({ data: ic.github, x: 0.8, y: 6.22, w: 0.45, h: 0.45, objectName: "arch-github" });
  s.addText([{ text: "GitHub Actions: ", options: { bold: true } }, { text: "lint · test · audit · gitleaks → build → 2 deploy → smoke test   " },
    { text: "GHAS: ", options: { bold: true } }, { text: "CodeQL · Dependabot · secret scanning" }],
    { x: 1.4, y: 6.05, w: 7.25, h: 0.8, fontSize: 12, color: C.text1, valign: "middle", margin: 0, isTextBox: true });
  card(s, 9.1, 1.5, 3.63, 2.55, C.accent2, "ai-card");
  s.addText([{ text: "AI ne yapar (Foundry)", options: { bold: true, fontSize: 16, breakLine: true } },
    ...["Metinden bilgi çıkarma, açıklama", "Çağrı zenginleştirme", "Çözüm uyarlama", "Kod analizi", "Talep bileşenleri ve sorular"].map((t, k, a) => ({ text: t, options: { bullet: true, fontSize: 14, breakLine: k < a.length - 1 } }))],
    { x: 9.3, y: 1.6, w: 3.3, h: 2.35, color: C.background1, valign: "top", margin: 0, paraSpaceAfter: 3, isTextBox: true });
  card(s, 9.1, 4.25, 3.63, 2.6, C.text2, "code-card");
  s.addText([{ text: "Kod ne yapar (kurallar)", options: { bold: true, fontSize: 16, breakLine: true } },
    ...["Log örüntüsü, kredi hesabı", "Eşik, servis ataması, ana kayıt", "Adam-gün medyanı, takvim", "Köprü sayıları", "AI çıktısındaki sayı ve satırları doğrulama"].map((t, k, a) => ({ text: t, options: { bullet: true, fontSize: 14, breakLine: k < a.length - 1 } }))],
    { x: 9.3, y: 4.35, w: 3.3, h: 2.4, color: C.background1, valign: "top", margin: 0, paraSpaceAfter: 3, isTextBox: true });
  s.addNotes("0:58–1:05 · İki App Service (web ve api), Foundry'de sohbet ve embedding modeli, SQL yapısal veri, AI Search hibrit arama. CI/CD her PR'da test ve güvenlik taraması yapıyor. Sağda AI'ın ve kuralların işi. (Yalnızca gerçekten çalışan servisler bu slaytta kalmalı.)");

  // ---------- 7. Kullanım senaryoları ----------
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Ürün" });
  s.addText("Altı kullanım senaryosu", { placeholder: "title" });
  // live: true = canlı demoda; 2. gün 12:00 kararına göre güncellenir
  const scen = [
    ["A", "Hata mı, kural mı?", "KRDTKULL", "Elif (şube)", "İş kuralı açıklandı, uygun tutar ekrana dolduruldu", "Çağrı açılmadı", true, C.accent1],
    ["B", "Yaygın sorun, bilinen çözüm", "ODMTFATR", "Mehmet → Zeynep → Kerem", "Müşteriye hazır açıklama, %93 eşleşen çözüm", "Onlarca arama tek kayıtta", true, C.accent2],
    ["C", "Dış dünya değişti", "ODMTFATR", "Elif → Kerem", "Log + kurum duyurusu + kod; düzeltme önerisi", "187 müşteri · ASKİ önceden", true, C.accent3],
    ["D", "Talepten plana", "Talep Yönlendirme", "Fatma → Ayşe", "Servis, adam-gün, takvim; veriyle kapsam", "Erişim %58 → %89 · 20 a/g", true, C.text2],
    ["E", "Acil yeni ekran", "KRDTERTL (yeni)", "Hakan → Ayşe", "Etkilenen müşteri, riskli sorular, kapasite çatışması", "Aynı gün karar · 17 a/g", false, C.accent5],
    ["F", "Günlük durum özeti", "Mercek sohbet", "Kerem", "Kibana bilgisi gerektirmeden sohbetle özet", "En sorunlu ekran: ODMTFATR", false, C.accent5],
  ];
  scen.forEach(([L, head, scr, who, what, res, live, col], i) => {
    const x = 0.6 + (i % 3) * 4.1, y = 1.45 + Math.floor(i / 3) * 2.75, w = 3.85, h = 2.55;
    card(s, x, y, w, h, C.background2, `scen-card-${L}`);
    s.addShape(pres.shapes.OVAL, { x: x + 0.25, y: y + 0.25, w: 0.6, h: 0.6, fill: { color: col }, line: { color: col }, objectName: `scen-letter-${L}` });
    s.addText(L, { x: x + 0.25, y: y + 0.25, w: 0.6, h: 0.6, fontSize: 20, bold: true, color: C.background1, align: "center", valign: "middle", margin: 0, isTextBox: true });
    s.addText([{ text: head, options: { fontSize: 16, bold: true, color: C.text1, breakLine: true } }, { text: scr + " · " + who, options: { fontSize: 11, color: C.accent5 } }],
      { x: x + 1.0, y: y + 0.2, w: w - 1.15, h: 0.75, valign: "middle", margin: 0, isTextBox: true });
    s.addText(what, { x: x + 0.25, y: y + 1.05, w: w - 0.5, h: 0.65, fontSize: 13, color: C.text2, valign: "top", margin: 0, isTextBox: true });
    s.addText(res, { x: x + 0.25, y: y + 1.75, w: w - 1.55, h: 0.55, fontSize: 13, bold: true, color: C.text1, valign: "middle", margin: 0, isTextBox: true });
    const pc = live ? C.accent2 : C.accent5;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + w - 1.3, y: y + 1.85, w: 1.1, h: 0.36, rectRadius: 0.18, fill: { color: pc }, line: { color: pc }, objectName: `scen-status-${L}` });
    s.addText(live ? "CANLI" : "KAYIT", { x: x + w - 1.3, y: y + 1.85, w: 1.1, h: 0.36, fontSize: 11, bold: true, color: C.background1, align: "center", valign: "middle", margin: 0, isTextBox: true });
  });
  s.addNotes("1:05–1:20 · Mercek'in altı kullanım senaryosu. 'CANLI' etiketliler birazdan canlı gösterilecek; diğerleri ekran görüntüsü veya kısa videoyla. (2. gün 12:00 kod dondurmada etiketleri gerçek duruma göre güncelleyin: canlı demoya yalnızca deploy edilmiş ortamda doğrulaması yeşil ve 3 provada hatasız olan senaryolar girer.)");

  // ---------- 8. Canlı demo ----------
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Ürün" });
  s.addText("Canlı demo: dört sahne", { placeholder: "title" });
  const scenes = [
    ["~45 sn", "A · Hata mı, kural mı?", "m-a-panel.png", "Elif yazmadan Mercek iş kuralını açıklıyor, 'Bana göster' ile 330.000 TL / 36 ay dolduruluyor. Çağrı açılmıyor."],
    ["~50 sn", "B · Bilinen çözüm", "m-b-callcenter.png", "Zeynep'e müşteriye söylenecek metin; vaka CAG-2051'e bağlanıyor; Kerem'e %93 eşleşen çözüm."],
    ["~35 sn", "C · Dış dünya değişti", "m-c-code.png", "412 hata, %97 İSKİ, 13 hane; İSKİ duyurusu; kuralın koddaki iki yeri ve düzeltme; ASKİ uyarısı."],
    ["~45 sn", "D · Talepten plana", "m-d-request.png", "Fatma'nın talebi: KRDRTKSR'ye buton + batch işi, 18 a/g; SMS ile erişim %58 → %89, 20 a/g, 4 Aralık."],
  ];
  const AR = 2560 / 1516;
  scenes.forEach(([t, head, img, desc], i) => {
    const x = 0.6 + (i % 2) * 6.15, y = 1.4 + Math.floor(i / 2) * 2.75, w = 5.95, h = 2.6;
    card(s, x, y, w, h, C.background2, `scene-card-${i + 1}`);
    const ih = 2.2, iw = ih * AR;
    s.addImage({ path: IMG(img), x: x + 0.2, y: y + 0.2, w: iw, h: ih, objectName: `demo-image-${i + 1}` });
    const tx = x + 0.4 + iw, tw = w - iw - 0.6;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: tx, y: y + 0.2, w: 0.95, h: 0.34, rectRadius: 0.17, fill: { color: C.accent1 }, line: { color: C.accent1 }, objectName: `scene-time-${i + 1}` });
    s.addText(t, { x: tx, y: y + 0.2, w: 0.95, h: 0.34, fontSize: 11, bold: true, color: C.text1, align: "center", valign: "middle", margin: 0, isTextBox: true });
    s.addText(head, { x: tx, y: y + 0.62, w: tw, h: 0.5, fontSize: 15, bold: true, color: C.text1, margin: 0, valign: "top", isTextBox: true });
    s.addText(desc, { x: tx, y: y + 1.12, w: tw, h: 1.35, fontSize: 11.5, color: C.text2, valign: "top", margin: 0, isTextBox: true });
  });
  draftNote(s, 0.6, 6.85, 8);
  s.addNotes("1:20–4:15 · CANLI DEMO (~3 dk), önce demo_reset çalıştırılmış olmalı. A: Elif KRDTKULL 400.000 / 3 ay → Sorun yaşıyorum → iş kuralı kartı → Bana göster. B: Mehmet ODMTFATR Başkentgaz (odm-dogalgaz turu) → Zeynep Mercek'e yazar → müşteriye söylenecek metin, CAG-2051 bağlı vaka 12 → Kerem %93 eşleşme. C: Elif İSKİ metni → 412 / %97 / 13 hane, duyuru → Kerem: %35, kod analizi, diff, ASKİ. D: Fatma talebi → analiz kartları → önerileri kabul et → 18 a/g, 9 Kasım–2 Aralık → köprü → Evet → 20 a/g, 4 Aralık. Canlıda olmayan sahneyi ekran görüntüsüyle 15 sn'de geçin; bir sahne bozulursa videosuna geçin.");

  // ---------- 9. İş değeri ----------
  pres.addSection({ title: "Değer ve kapanış" });
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Değer ve kapanış" });
  s.addText("İş değeri: önce ve sonra", { placeholder: "title" });
  const stats = [["Çağrı hiç açılmıyor", "İş kuralı reddinde (A)", C.accent2], ["Onlarca arama → tek kayıt", "Kurum kaynaklı sorunda (B)", C.accent1], ["Toplantı → dakikalar", "Talep analizi ve planı (D)", C.text2]];
  stats.forEach(([big, lbl, col], i) => {
    const x = 0.6 + i * 4.1, w = 3.85;
    card(s, x, 1.5, w, 1.65, C.background2, `stat-card-${i + 1}`);
    s.addText([{ text: big, options: { fontSize: 22, bold: true, color: col, breakLine: true } }, { text: lbl, options: { fontSize: 14, color: C.accent5 } }],
      { x: x + 0.3, y: 1.6, w: w - 0.6, h: 1.45, valign: "middle", margin: 0, isTextBox: true });
  });
  const hdr = (t) => ({ text: t, options: { bold: true, color: C.background1, fill: { color: C.text2 } } });
  const rows = [
    [hdr("Ölçü"), hdr("Bugün"), hdr("Mercek ile")],
    ["İş kuralı reddi", "Çağrı açılır, L1 kuralı açıklar", "Ekranda açıklanır, uygun alternatif hesaplanır"],
    ["Yaygın kurum sorunu", "Her arama ayrı çağrı", "Tek ana kayıt, temsilciye hazır müşteri açıklaması"],
    ["Bilinen sorun", "L2 log arar, çözüm kişide", "Kaynaklı eşleşen çözüm, saniyeler içinde"],
    ["Yeni sorun", "Kök neden günlerce aranır", "Log + duyuru + kod; sonraki olay önceden görülür"],
    ["Talep planı", "Servisler ve erişim sorunu geç fark edilir", "Servis bazlı a/g ve takvim; kapsam veriyle düzeltilir"],
  ];
  s.addTable(rows, { x: 0.6, y: 3.4, w: 12.1, colW: [3.0, 4.2, 4.9], fontSize: 13, color: C.text1, fontFace: THEME.bodyFontFace,
    border: { type: "solid", pt: 1, color: "DDE2E8" }, rowH: 0.47, valign: "middle", margin: [0.05, 0.12, 0.05, 0.12] });
  s.addText("Rakamlar sentetik veriye dayanır; demo sırasında Mercek'in sayaçları (önlenen çağrı, bağlanan vaka, analiz süresi) gösterilir.", { x: 0.6, y: 6.55, w: 12, h: 0.3, fontSize: 11, italic: true, color: C.accent5, margin: 0, isTextBox: true });
  s.addNotes("4:15–4:45 · Önce/sonra. Demo sırasında artan sayaçları ve ölçülen analiz süresini söyleyin. Varsayımları açıkça belirtin.");

  // ---------- 10. Sonuçlar ve sonraki adımlar ----------
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Değer ve kapanış" });
  s.addText("Neredeyiz, sırada ne var", { placeholder: "title" });
  const cols = [
    [C.accent2, ic.check, "Tamamlanan", ["M1: bağlam, log örüntüsü, servis ataması, ana kayıt, eşleştirme, kod analizi", "M2: talep analizi, servis etkisi, adam-gün, takvim, köprü", "Azure: 2 App Service, Foundry, SQL, AI Search", "CI/CD ve PR'da güvenlik taraması"]],
    [C.accent3, ic.warn, "Sınırlamalar", ["Veri tamamen sentetik", "Gerçek log, çağrı ve kod entegrasyonu yok", "Kod düzeltmeleri öneri; uygulama insan onaylı", "E-posta ve SMS gönderimi simülasyon"]],
    [C.accent1, ic.route, "Canlıya geçiş", ["Log kaynağı: Kibana / Elasticsearch", "Çağrı sistemi ve kod reposu için salt-okur entegrasyon", "KVKK: loglarda maskeleme", "Pilot: şube kanalı, KRDTKULL ve ODMTFATR"]],
  ];
  cols.forEach(([col, img, head, items], i) => {
    const x = 0.6 + i * 4.1, w = 3.85;
    card(s, x, 1.5, w, 5.2, C.background2, `next-card-${i + 1}`);
    iconCircle(s, x + 0.3, 1.8, 0.75, col, img, `next-${i + 1}`);
    s.addText(head, { x: x + 1.2, y: 1.8, w: w - 1.4, h: 0.75, fontSize: 20, bold: true, color: C.text1, valign: "middle", margin: 0, isTextBox: true });
    s.addText(items.map((t, k) => ({ text: t, options: { bullet: true, breakLine: k < items.length - 1 } })),
      { x: x + 0.3, y: 2.8, w: w - 0.6, h: 3.7, fontSize: 14, color: C.text1, valign: "top", paraSpaceAfter: 8, margin: 0, isTextBox: true });
  });
  s.addNotes("4:45–4:55 · 'Tamamlanan' listesini 2. gün 12:00'de gerçek duruma göre güncelleyin. S-C: AI yanlışsa → eşik, kaynak, sayı doğrulaması, insan onayı. Maliyet → küçük model, kısa bağlam, analiz başına ölçülen token.");

  // ---------- 11. Ekler / kapanış ----------
  s = pres.addSlide({ masterName: "DARK", sectionTitle: "Değer ve kapanış" });
  s.addText("Ekler", { x: 0.8, y: 0.8, w: 6, h: 0.9, fontSize: 40, bold: true, color: C.background1, margin: 0, isTextBox: true });
  const links = [[ic.githubW, "GitHub repository", "[repo bağlantısı]"], [ic.globe, "Web uygulaması", "[mercek-web adresi]"], [ic.video, "Senaryo videoları", "[video bağlantısı]"]];
  links.forEach(([img, h1, v], i) => {
    const y = 2.1 + i * 1.15;
    iconCircle(s, 0.8, y, 0.75, C.text2, img, `link-${i + 1}`);
    s.addText([{ text: h1, options: { bold: true, fontSize: 18, color: C.background1, breakLine: true } }, { text: v, options: { fontSize: 16, color: C.accent1 } }],
      { x: 1.8, y: y - 0.05, w: 5.5, h: 0.9, valign: "middle", margin: 0, isTextBox: true });
  });
  s.addText("Soruna odaklanır, çözümü netleştirir.", { x: 0.8, y: 5.75, w: 7, h: 0.6, fontSize: 24, italic: true, color: C.background2, margin: 0, isTextBox: true });
  s.addText("Teşekkürler · AI Overflow", { x: 0.8, y: 6.35, w: 7, h: 0.45, fontSize: 16, bold: true, color: C.accent1, margin: 0, isTextBox: true });
  lens(s, 10.35, 3.75, 2.25);
  s.addNotes("4:55–5:00 · Sloganla kapatın. Bağlantıları sunumdan önce doldurun; şifre, anahtar veya gerçek müşteri verisi görünmediğini kontrol edin.");

  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("OK", OUT);
})().catch((e) => { console.error(e); process.exit(1); });
