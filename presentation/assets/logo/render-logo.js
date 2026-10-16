// Mercek logosunu PNG'ye çevirir. Çalıştırma: node render-logo.js
const path = require("path");
const sharp = require("sharp");
(async () => {
  const src = path.join(__dirname, "mercek-logo.svg");
  await sharp(src, { density: 400 }).resize(1200, 1200).png().toFile(path.join(__dirname, "mercek-logo.png"));
  await sharp(src, { density: 200 }).resize(256, 256).png().toFile(path.join(__dirname, "mercek-logo-small.png"));
  console.log("ok");
})();
