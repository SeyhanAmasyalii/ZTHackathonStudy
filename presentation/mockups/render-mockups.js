// Taslak ekranları PNG'ye çevirir. Çalıştırma: node render-mockups.js
const path = require("path");
const { chromium } = require("playwright");
(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || undefined });
  const page = await browser.newPage({ viewport: { width: 1360, height: 900 }, deviceScaleFactor: 2 });
  await page.goto("file://" + path.join(__dirname, "mockups.html"));
  for (const id of ["m-a-panel", "m-b-callcenter", "m-c-code", "m-d-request"]) {
    await page.locator("#" + id).screenshot({ path: path.join(__dirname, id + ".png") });
    console.log("ok", id);
  }
  await browser.close();
})();
