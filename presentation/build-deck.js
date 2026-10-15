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
  s.addText("Görevler 19 maddelik sorumluluk listesinden herkesin kendi seçimiyle dağıtıldı.", { x: 0.6, y: 6.3, w: 12, h: 0.4, fontSize: 14, color: C.accent5, margin: 0, isTextBox: true });
  s.addNotes("0:10–0:20 · Takımı tek cümleyle tanıtın. (Ad, birim ve rolleri doldurun; fotoğraf eklenecekse daire içine yerleştirin.)");

  // ---------- 3. Problem ----------
  pres.addSection({ title: "Problem ve çözüm" });
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Problem ve çözüm" });
  s.addText("Bir EFT hatası, saatler süren bir yolculuk", { placeholder: "title" });
  card(s, 0.6, 1.6, 3.5, 4.95, C.text2, "quote-card");
  s.addImage({ data: ic.quote, x: 0.95, y: 1.95, w: 0.55, h: 0.55, objectName: "quote-icon" });
  s.addText("“Kiramı gönderemiyorum, acil.”", { x: 0.95, y: 2.65, w: 2.9, h: 1.6, fontSize: 26, italic: true, bold: true, color: C.background1, margin: 0, valign: "top", isTextBox: true });
  s.addText("Ayşe, bireysel müşteri · Para Transferi ekranı", { x: 0.95, y: 5.6, w: 2.9, h: 0.7, fontSize: 14, color: C.background2, margin: 0, valign: "bottom", isTextBox: true });

  const steps = ["Müşteri hata alır", "Çağrı merkezini arar", "L1 tek cümlelik kayıt açar", "L2 log arar, ekibi bulur", "Ekip kök nedeni arar"];
  steps.forEach((t, i) => {
    const x = 4.45 + i * 1.66, y = 1.6, w = 1.5, h = 1.9;
    card(s, x, y, w, h, C.background2, `flow-step-${i + 1}`);
    s.addShape(pres.shapes.OVAL, { x: x + 0.15, y: y + 0.15, w: 0.45, h: 0.45, fill: { color: C.accent3 }, line: { color: C.accent3 }, objectName: `flow-num-${i + 1}` });
    s.addText(String(i + 1), { x: x + 0.15, y: y + 0.15, w: 0.45, h: 0.45, fontSize: 14, bold: true, color: C.background1, align: "center", valign: "middle", margin: 0, isTextBox: true });
    s.addText(t, { x: x + 0.15, y: y + 0.7, w: w - 0.3, h: 1.1, fontSize: 14, color: C.text1, valign: "top", margin: 0, isTextBox: true });
  });
  s.addText("Toplam: saatler — bu sürede müşteri ödemesini yapamıyor", { x: 4.45, y: 3.6, w: 8.2, h: 0.4, fontSize: 16, bold: true, color: C.accent3, margin: 0, isTextBox: true });

  const pains = [
    [ic.eye, "Bağlam kaybolur", "Ekran, log ve kullanıcı adımları kayda girmiyor."],
    [ic.brain, "Bilgi kişilerde", "Aynı sorun daha önce çözülmüş ama aranamıyor."],
    [ic.unlink, "Talepler kopuk", "Aynı ekrana gelen yeni talep, o ekranın çağrılarını görmüyor."],
  ];
  pains.forEach(([img, h1, d], i) => {
    const x = 4.45 + i * 2.78, y = 4.3;
    iconCircle(s, x, y, 0.6, C.text2, img, `pain-${i + 1}`);
    s.addText([{ text: h1, options: { bold: true, fontSize: 16, breakLine: true } }, { text: d, options: { fontSize: 14, color: C.accent5 } }],
      { x, y: y + 0.75, w: 2.6, h: 1.5, valign: "top", color: C.text1, margin: 0, isTextBox: true });
  });
  s.addNotes("0:20–0:50 · Ayşe'nin hikâyesi: EFT hatası, çağrı merkezi, L1, L2, ekip. Her adımda bağlam kayboluyor. Aynı ekrana gelen değişiklik talepleri de bu çağrı birikimini hiç görmüyor. (Süre ifadeleri varsayımdır; kurum içi gerçek rakam varsa onunla değiştirin.)");

  // ---------- 4. Çözüm ----------
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Problem ve çözüm" });
  s.addText("Mercek: sorundan plana tek akış", { placeholder: "title" });
  s.addText("Sorunu müşteri daha çağrı açarken tespit eder, doğru ekibe yönlendirip çözüm önerir ve bu çağrı birikimini yeni taleplerin kapsamına, maliyetine ve takvimine dönüştürür.",
    { x: 0.6, y: 1.35, w: 12.1, h: 0.85, fontSize: 18, color: C.text2, margin: 0, valign: "top", isTextBox: true });
  const mods = [
    [C.accent2, ic.headset, "Akıllı Problem Çözüm ve Çağrı Yönetimi", ["Hatayı müşteri yazmadan tespit eder", "Çağrıyı zenginleştirir, doğru ekibe yönlendirir", "Geçmiş çözümü bulur; yoksa kodu inceler"]],
    [C.accent1, ic.clip, "Akıllı Talep Analizi, Maliyet ve Takvim", ["Talebi sınıflar, etkilenen servisleri bulur", "Benzer taleplerden efor, maliyet, takvim çıkarır", "Ekranın çağrı geçmişini kapsama ekler"]],
  ];
  mods.forEach(([col, img, head, items], i) => {
    const x = 0.6 + i * 6.6, y = 2.35, w = 5.5, h = 3.05;
    card(s, x, y, w, h, C.background2, `module-card-${i + 1}`);
    iconCircle(s, x + 0.3, y + 0.3, 0.75, col, img, `module-${i + 1}`);
    s.addText(head, { x: x + 1.25, y: y + 0.3, w: w - 1.5, h: 0.75, fontSize: 20, bold: true, color: C.text1, valign: "middle", margin: 0, isTextBox: true });
    s.addText(items.map((t, k) => ({ text: t, options: { bullet: true, breakLine: k < items.length - 1 } })),
      { x: x + 0.3, y: y + 1.25, w: w - 0.6, h: 1.6, fontSize: 16, color: C.text1, paraSpaceAfter: 6, valign: "top", margin: 0, isTextBox: true });
  });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.15, y: 3.35, w: 1.0, h: 1.05, rectRadius: 0.15, fill: { color: C.text1 }, line: { color: C.text1 }, objectName: "bridge-pill" });
  s.addText([{ text: "çağrı", options: { breakLine: true } }, { text: "→", options: { breakLine: true } }, { text: "kapsam" }], { x: 6.15, y: 3.35, w: 1.0, h: 1.05, fontSize: 12, bold: true, color: C.accent1, align: "center", valign: "middle", margin: 0, isTextBox: true });
  s.addText("Hedef kullanıcılar", { x: 0.6, y: 5.75, w: 2.3, h: 0.5, fontSize: 16, bold: true, color: C.text1, valign: "middle", margin: 0, isTextBox: true });
  const users = [[ic.users, "Müşteri"], [ic.headsetD, "L1 / L2 destek"], [ic.clipD, "İş analisti"], [ic.chart, "Takım lideri"]];
  users.forEach(([img, t], i) => {
    const x = 2.9 + i * 2.45, y = 5.7;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: 2.25, h: 0.6, rectRadius: 0.3, fill: { color: C.background2 }, line: { color: C.background2 }, objectName: `user-chip-${i + 1}` });
    s.addImage({ data: img, x: x + 0.2, y: y + 0.15, w: 0.3, h: 0.3 });
    s.addText(t, { x: x + 0.6, y, w: 1.6, h: 0.6, fontSize: 14, color: C.text1, valign: "middle", margin: 0, isTextBox: true });
  });
  s.addNotes("0:50–1:05 · Tek cümle çözüm. İki modül ve aralarındaki köprü: çağrı verisi talep kapsamına giriyor. Hedef kullanıcılar.");

  // ---------- 5. Yenilikçilik ----------
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Problem ve çözüm" });
  s.addText("Dört farkımız", { placeholder: "title" });
  const diffs = [
    [C.accent1, ic.bolt, "Proaktif", "Müşteri daha yazmadan, o ekranın canlı loglarından olası nedeni söyler ve alternatif yolu gösterir."],
    [C.accent2, ic.code, "Kodu okuyan AI", "Geçmişte benzeri yoksa ilgili servis kodunu ve SP'yi inceler, satır düzeyinde düzeltme önerir."],
    [C.text2, ic.sync, "Kapalı döngü", "Bir ekranın çağrı birikimi, o ekrana gelen yeni talebin kapsamına ve maliyetine girer."],
    [C.accent3, ic.shield, "Güvenilir AI", "Hesabı kod yapar, AI açıklar. Eşik altında öneri yok; her öneri kaynağıyla birlikte gelir."],
  ];
  diffs.forEach(([col, img, head, desc], i) => {
    const x = 0.6 + (i % 2) * 6.25, y = 1.6 + Math.floor(i / 2) * 2.6, w = 5.85, h = 2.3;
    card(s, x, y, w, h, C.background2, `diff-card-${i + 1}`);
    iconCircle(s, x + 0.35, y + 0.4, 0.85, col, img, `diff-${i + 1}`);
    s.addText([{ text: head, options: { fontSize: 22, bold: true, color: C.text1, breakLine: true } }, { text: desc, options: { fontSize: 16, color: C.text2 } }],
      { x: x + 1.5, y: y + 0.35, w: w - 1.8, h: h - 0.6, valign: "top", margin: 0, paraSpaceAfter: 4, isTextBox: true });
  });
  s.addNotes("1:05–1:20 · Bugünkü araçlar çağrıyı kaydeder; Mercek çağrı açılmadan tespit eder, gerekirse kodu okur ve çağrı birikimini yeni talebe bağlar. AI'ın rolü sınırlı ve denetlenebilir: hesap kodda.");

  // ---------- 6. Mimari ----------
  pres.addSection({ title: "Ürün" });
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Ürün" });
  s.addText("Mimari: Azure üzerinde uçtan uca", { placeholder: "title" });
  const box = (x, y, w, h, fill, head, sub, name, dark) => {
    card(s, x, y, w, h, fill, name, dark ? fill : C.accent5);
    s.addText([{ text: head, options: { bold: true, fontSize: 16, breakLine: true } }, { text: sub, options: { fontSize: 13 } }],
      { x: x + 0.15, y: y + 0.1, w: w - 0.3, h: h - 0.2, color: dark ? C.background1 : C.text1, valign: "middle", align: "center", margin: 0, isTextBox: true });
  };
  box(0.6, 2.35, 1.9, 2.6, C.background2, "Kullanıcılar", "Müşteri\nDestek ekibi\nİş analisti", "arch-users");
  box(3.05, 2.35, 2.45, 2.6, C.text2, "Azure App Service", "React arayüz\n+ FastAPI\n/health", "arch-app", true);
  box(6.1, 1.5, 2.6, 1.25, C.background2, "Azure AI Foundry", "chat + embedding modeli", "arch-foundry");
  box(6.1, 3.0, 2.6, 1.25, C.background2, "Azure SQL", "ekran, log, çağrı, talep, takvim", "arch-sql");
  box(6.1, 4.5, 2.6, 1.25, C.background2, "Azure AI Search", "hibrit arama: çözüm, çağrı, talep", "arch-search");
  const arrow = (x1, y1, x2, y2, name) => s.addShape(pres.shapes.LINE, { x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1) || 0.001, h: Math.abs(y2 - y1) || 0.001,
    flipV: y2 < y1, line: { color: C.accent5, width: 2, endArrowType: "triangle" }, objectName: name });
  arrow(2.5, 3.65, 3.05, 3.65, "arrow-users-app");
  arrow(5.5, 3.3, 6.1, 2.12, "arrow-app-foundry");
  arrow(5.5, 3.65, 6.1, 3.62, "arrow-app-sql");
  arrow(5.5, 4.0, 6.1, 5.12, "arrow-app-search");
  card(s, 0.6, 6.0, 8.1, 0.8, C.background2, "arch-cicd");
  s.addImage({ data: ic.github, x: 0.8, y: 6.17, w: 0.45, h: 0.45, objectName: "arch-github" });
  s.addText([{ text: "GitHub Actions: ", options: { bold: true } }, { text: "lint · test · audit · gitleaks → build → deploy → health check   " },
    { text: "GHAS: ", options: { bold: true } }, { text: "CodeQL · Dependabot · secret scanning" }],
    { x: 1.4, y: 6.0, w: 7.2, h: 0.8, fontSize: 13, color: C.text1, valign: "middle", margin: 0, isTextBox: true });
  // AI / Kod paneli
  card(s, 9.1, 1.5, 3.63, 2.55, C.accent2, "ai-card");
  s.addText([{ text: "AI ne yapar (Foundry)", options: { bold: true, fontSize: 16, breakLine: true } },
    ...["Sınıflandırma ve özet", "Çağrı zenginleştirme", "Çözüm uyarlama", "Kod analizi", "Gerekçe yazma"].map((t, k, a) => ({ text: t, options: { bullet: true, fontSize: 14, breakLine: k < a.length - 1 } }))],
    { x: 9.3, y: 1.6, w: 3.3, h: 2.35, color: C.background1, valign: "top", margin: 0, paraSpaceAfter: 3, isTextBox: true });
  card(s, 9.1, 4.25, 3.63, 2.55, C.text2, "code-card");
  s.addText([{ text: "Kod ne yapar (kurallar)", options: { bold: true, fontSize: 16, breakLine: true } },
    ...["Eşik ve güven kararları", "Servis ve ekip ataması", "Efor ve maliyet hesabı", "Takvim planı", "AI çıktısını doğrulama"].map((t, k, a) => ({ text: t, options: { bullet: true, fontSize: 14, breakLine: k < a.length - 1 } }))],
    { x: 9.3, y: 4.35, w: 3.3, h: 2.35, color: C.background1, valign: "top", margin: 0, paraSpaceAfter: 3, isTextBox: true });
  s.addNotes("1:20–1:35 · Tek App Service; Foundry'de sohbet ve embedding modeli; SQL yapısal veri; AI Search hibrit arama. CI/CD her PR'da test ve güvenlik taraması yapıyor. Sağda: AI'ın ve kuralların işi net ayrılmış. (Sadece gerçekten çalışan servisler bu slaytta kalmalı.)");

  // ---------- 7. Kullanıcı deneyimi ----------
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Ürün" });
  s.addText("Üç kullanıcı, tek akış", { placeholder: "title" });
  s.addImage({ path: IMG("m-bank-issue.png"), x: 0.95, y: 1.4, w: 1.95, h: 4.0, objectName: "ux-image-1" });
  s.addImage({ path: IMG("m-console-match.png"), x: 3.55, y: 2.1, w: 4.45, h: 1.91, objectName: "ux-image-2" });
  s.addImage({ path: IMG("m-request.png"), x: 8.27, y: 2.1, w: 4.45, h: 1.94, objectName: "ux-image-3" });
  const ux = [
    [0.6, 2.8, "1", "Ayşe sorunu bildirir", "Tek dokunuş; Mercek nedeni ve alternatif yolu söyler."],
    [3.55, 4.45, "2", "Mert çözümü onaylar", "Destek Konsolu: zenginleştirilmiş kayıt, eşleşen çözüm, kaynaklar."],
    [8.27, 4.45, "3", "Zeynep talebi planlar", "Talep Asistanı: etki, efor, takvim ve ekranın çağrı geçmişi."],
  ];
  ux.forEach(([x, w, n, h1, d], i) => {
    const y = i === 0 ? 5.6 : 4.3;
    s.addShape(pres.shapes.OVAL, { x, y, w: 0.42, h: 0.42, fill: { color: C.accent1 }, line: { color: C.accent1 }, objectName: `ux-num-${n}` });
    s.addText(n, { x, y, w: 0.42, h: 0.42, fontSize: 14, bold: true, color: C.text1, align: "center", valign: "middle", margin: 0, isTextBox: true });
    s.addText([{ text: h1, options: { bold: true, fontSize: 16, breakLine: true } }, { text: d, options: { fontSize: 14, color: C.accent5 } }],
      { x: x + 0.55, y: y - 0.05, w: w - 0.55, h: 1.2, color: C.text1, valign: "top", margin: 0, isTextBox: true });
  });
  draftNote(s, 3.55, 6.55, 9);
  s.addNotes("1:35–1:45 · Üç kullanıcı, üç ekran, tek akış. Detayı demoda göstereceğiz.");

  // ---------- 8. Demo ----------
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Ürün" });
  s.addText("Demo: üç sahnede Mercek", { placeholder: "title" });
  const scenes = [
    ["~60 sn", "Sahne 1 · Para gönderemiyorum", "m-bank-tour.png", 780 / 1600, "Ayşe EFT yapamıyor. Mercek o yazmadan nedeni söylüyor, havale yolunu gösteriyor ve çağrıyı açıyor."],
    ["~60 sn", "Sahne 2 · AI kodu okur", "m-console-code.png", 2560 / 1046, "Mert %93 eşleşmeyle çözümü görüyor. Eşleşmeyen çağrıda Mercek SP'deki yuvarlama hatasını buluyor."],
    ["~30 sn", "Sahne 3 · Talepten plana", "m-request.png", 2560 / 1116, "Zeynep'in talebi için etki, efor, takvim. 312 çağrının kalıcı çözümü kapsama giriyor."],
  ];
  scenes.forEach(([t, head, img, ar, desc], i) => {
    const x = 0.6 + i * 4.1, w = 3.85;
    card(s, x, 1.5, w, 5.25, C.background2, `scene-card-${i + 1}`);
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.25, y: 1.7, w: 1.0, h: 0.36, rectRadius: 0.18, fill: { color: C.accent1 }, line: { color: C.accent1 }, objectName: `scene-time-${i + 1}` });
    s.addText(t, { x: x + 0.25, y: 1.7, w: 1.0, h: 0.36, fontSize: 12, bold: true, color: C.text1, align: "center", valign: "middle", margin: 0, isTextBox: true });
    s.addText(head, { x: x + 0.25, y: 2.15, w: w - 0.5, h: 0.45, fontSize: 17, bold: true, color: C.text1, margin: 0, valign: "middle", isTextBox: true });
    const areaY = 2.7, areaH = 2.55, maxW = w - 0.5;
    let iw = maxW, ih = iw / ar;
    if (ih > areaH) { ih = areaH; iw = ih * ar; }
    s.addImage({ path: IMG(img), x: x + 0.25 + (maxW - iw) / 2, y: areaY + (areaH - ih) / 2, w: iw, h: ih, objectName: `demo-image-${i + 1}` });
    s.addText(desc, { x: x + 0.25, y: 5.35, w: w - 0.5, h: 1.3, fontSize: 14, color: C.text2, valign: "top", margin: 0, isTextBox: true });
  });
  draftNote(s, 0.6, 6.78, 8);
  s.addNotes("1:45–4:15 · CANLI DEMO (yaklaşık 2,5 dk). Sahne 1: Para Transferi'nde 2.500 TL EFT → hata → Sorun yaşıyorum → olası neden kartı → Bana göster (havale turu). Sahne 2: Destek Konsolu CAG-1042 (%93 eşleşme, kaynaklar) → CAG-1043 (%41, kod analizi, diff). Sahne 3: Talep Asistanı 'favori alıcı' → etki, 15–22 adam-gün, 9 Kasım → 4 Aralık → 312 çağrı → kapsama ekle → 9 Aralık. Bağlantı sorunu olursa yedek videoya geçin.");

  // ---------- 9. İş değeri ----------
  pres.addSection({ title: "Değer ve kapanış" });
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Değer ve kapanış" });
  s.addText("İş değeri: önce ve sonra", { placeholder: "title" });
  const stats = [["Saatler → saniyeler", "Sorunun ilk tespiti", C.accent2], ["Tek cümle → tam kayıt", "Çağrı kaydının kalitesi", C.accent1], ["Günler → dakikalar", "Talep efor tahmini", C.text2]];
  stats.forEach(([big, lbl, col], i) => {
    const x = 0.6 + i * 4.1, w = 3.85;
    card(s, x, 1.5, w, 1.65, C.background2, `stat-card-${i + 1}`);
    s.addText([{ text: big, options: { fontSize: 24, bold: true, color: col, breakLine: true } }, { text: lbl, options: { fontSize: 14, color: C.accent5 } }],
      { x: x + 0.3, y: 1.6, w: w - 0.6, h: 1.45, valign: "middle", margin: 0, isTextBox: true });
  });
  const hdr = (t) => ({ text: t, options: { bold: true, color: C.background1, fill: { color: C.text2 } } });
  const rows = [
    [hdr("Ölçü"), hdr("Bugün"), hdr("Mercek ile")],
    ["Doğru ekibe yönlendirme", "L1 tahmini, yeniden atamalar", "Hata kodu ve servis haritasıyla ilk seferde"],
    ["Bilinen sorunun çözümü", "Bilgi kişilerde, aranamıyor", "Geçmiş çözüm saniyeler içinde, kaynaklı"],
    ["Yeni sorunun kök nedeni", "Ekip kodu baştan inceler", "Satır düzeyinde düzeltme önerisi"],
    ["Talep kapsamı", "Çağrı verisinden kopuk", "Ekranın çağrı geçmişi kapsamda"],
  ];
  s.addTable(rows, { x: 0.6, y: 3.4, w: 12.1, colW: [3.2, 4.2, 4.7], fontSize: 14, color: C.text1, fontFace: THEME.bodyFontFace,
    border: { type: "solid", pt: 1, color: "DDE2E8" }, rowH: 0.56, valign: "middle", margin: [0.05, 0.12, 0.05, 0.12] });
  s.addText("Rakamlar sentetik veriye ve varsayımlara dayanır; demo ölçümleriyle güncellenecek.", { x: 0.6, y: 6.55, w: 12, h: 0.3, fontSize: 11, italic: true, color: C.accent5, margin: 0, isTextBox: true });
  s.addNotes("4:15–4:40 · Önce/sonra. Ölçümlerden gelen gerçek süreleri (tespit X sn, zenginleştirme Y sn, tahmin Z sn) büyük rakamların yerine koyun. Varsayımları açıkça söyleyin.");

  // ---------- 10. Sonuçlar ve sonraki adımlar ----------
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Değer ve kapanış" });
  s.addText("Neredeyiz, sırada ne var", { placeholder: "title" });
  const cols = [
    [C.accent2, ic.check, "Tamamlanan", ["M1: tespit, zenginleştirme, eşleştirme, kod analizi", "M2: sınıflandırma, etki, efor, takvim, köprü", "Azure: App Service, Foundry, SQL, AI Search", "CI/CD ve PR'da güvenlik taraması"]],
    [C.accent3, ic.warn, "Sınırlamalar", ["Veri tamamen sentetik", "Gerçek log, çağrı ve kod entegrasyonu yok", "Kod düzeltmeleri öneri; uygulama insan onaylı"]],
    [C.accent1, ic.route, "Canlıya geçiş", ["Log, çağrı ve kod reposu için salt-okur entegrasyon", "KVKK: loglarda maskeleme", "Pilot: tek kanal, tek ekran (Para Transferi)", "AI maliyeti ve doğruluğunun izlenmesi"]],
  ];
  cols.forEach(([col, img, head, items], i) => {
    const x = 0.6 + i * 4.1, w = 3.85;
    card(s, x, 1.5, w, 5.2, C.background2, `next-card-${i + 1}`);
    iconCircle(s, x + 0.3, 1.8, 0.75, col, img, `next-${i + 1}`);
    s.addText(head, { x: x + 1.2, y: 1.8, w: w - 1.4, h: 0.75, fontSize: 20, bold: true, color: C.text1, valign: "middle", margin: 0, isTextBox: true });
    s.addText(items.map((t, k) => ({ text: t, options: { bullet: true, breakLine: k < items.length - 1 } })),
      { x: x + 0.3, y: 2.8, w: w - 0.6, h: 3.7, fontSize: 15, color: C.text1, valign: "top", paraSpaceAfter: 8, margin: 0, isTextBox: true });
  });
  s.addNotes("4:40–4:55 · 'Tamamlanan' listesini 2. gün 12:00'de gerçek duruma göre güncelleyin. S-C: AI yanlışsa → eşik, kaynak, insan onayı, hesap kodda. Maliyet → küçük model, çağrı başına ölçülen maliyet. Kim kullanır → müşteri, L1/L2, analist.");

  // ---------- 11. Ekler / kapanış ----------
  s = pres.addSlide({ masterName: "DARK", sectionTitle: "Değer ve kapanış" });
  s.addText("Ekler", { x: 0.8, y: 0.8, w: 6, h: 0.9, fontSize: 40, bold: true, color: C.background1, margin: 0, isTextBox: true });
  const links = [[ic.githubW, "GitHub repository", "[repo bağlantısı]"], [ic.globe, "Web uygulaması", "[mercek-app adresi]"], [ic.video, "Demo videosu", "[video bağlantısı]"]];
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
