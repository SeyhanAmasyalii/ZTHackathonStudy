// Mercek logosunu PNG'ye çevirir. Çalıştırma: node render-logo.js
const path = require("path");
const sharp = require("sharp");
(async () => {
  const p = (f) => path.join(__dirname, f);
  await sharp(p("mercek-logo.svg"), { density: 400 }).trim().resize(1000).png().toFile(p("mercek-logo.png"));
  await sharp(p("mercek-logo-kucuk.svg"), { density: 300 }).resize(400, 400).png().toFile(p("mercek-logo-kucuk.png"));
  console.log("ok");
})();
