const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

async function render(htmlPath, outputPath) {
  const absHtml = path.resolve(htmlPath);
  const absOutput = path.resolve(outputPath);

  if (!fs.existsSync(absHtml)) {
    console.error(`HTML file not found: ${absHtml}`);
    process.exit(1);
  }

  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();

  // Load via file:// so relative image paths resolve correctly
  await page.goto(`file:///${absHtml.replace(/\\/g, '/')}`, {
    waitUntil: 'networkidle0',
    timeout: 30000,
  });

  // Wait for KaTeX to finish rendering math
  await page.waitForFunction(
    () => document.querySelectorAll('.katex').length > 0 ||
          document.querySelectorAll('[data-math-done]').length > 0,
    { timeout: 15000 }
  ).catch(() => {
    // No math in document — that's fine, continue
  });

  await page.pdf({
    path: absOutput,
    format: 'A4',
    margin: { top: '20mm', right: '20mm', bottom: '25mm', left: '20mm' },
    printBackground: true,
  });

  await browser.close();
  console.log(`OK:${absOutput}`);
}

const [htmlPath, outputPath] = process.argv.slice(2);

if (!htmlPath || !outputPath) {
  console.error('Usage: node render.js <input.html> <output.pdf>');
  process.exit(1);
}

render(htmlPath, outputPath).catch((err) => {
  console.error(`ERROR:${err.message}`);
  process.exit(1);
});
