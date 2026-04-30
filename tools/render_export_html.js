const path = require("path");
const { chromium } = require("playwright");

async function main() {
  const root = path.resolve(__dirname, "..");
  const htmlPath = path.join(root, "export-dialogue-gemini.html");
  const outPath = path.join(root, "visual-diff", "export-html.png");
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({
    viewport: { width: 600, height: 700 },
    deviceScaleFactor: 1,
  });
  await page.goto(`file://${htmlPath.replace(/\\/g, "/")}`);
  const panel = page.locator(".export-window");
  await panel.screenshot({ path: outPath });
  await browser.close();
  console.log(outPath);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
