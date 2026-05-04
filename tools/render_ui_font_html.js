const path = require("path");
const fs = require("fs");
const { chromium } = require("playwright");

async function main() {
  const root = path.resolve(__dirname, "..");
  const htmlPath = path.join(root, "references", "html", "pt-ui-font-gemini.html");
  const outPath = path.join(root, "visual-diff", "ui-font-html.png");
  fs.mkdirSync(path.dirname(outPath), { recursive: true });
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({
    viewport: { width: 900, height: 700 },
    deviceScaleFactor: 1,
  });
  await page.goto(`file://${htmlPath.replace(/\\/g, "/")}`);
  const targetWidth = 356;
  await page.addStyleTag({
    content: `
      :root { --panel-width: ${targetWidth}px; }
      .theme-toggle { display: none !important; }
      body { width: 900px; height: 700px; }
    `,
  });
  const panel = page.locator(".plugin-window");
  await panel.screenshot({ path: outPath });
  await browser.close();
  console.log(outPath);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
