// Baixa imagens do site da Tex em tamanho original, pelo Chromium (o servidor recusa curl com 406).
//   node baixar_tex.mjs url ...   → ../marca/tex/original/
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { chromium } from "playwright";

const OUT = path.join(path.dirname(fileURLToPath(import.meta.url)), "..", "marca", "tex", "original");
fs.mkdirSync(OUT, { recursive: true });
const browser = await chromium.launch();
const ctx = await browser.newContext({ userAgent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36" });
const page = await ctx.newPage();
await page.goto("https://tex.com.br/", { waitUntil: "domcontentloaded" });
await page.waitForTimeout(8000);
for (const u of process.argv.slice(2)) {
  const r = await ctx.request.get(u, { headers: { referer: "https://tex.com.br/" } });
  const nome = u.split("/").pop();
  if (r.ok()) { fs.writeFileSync(path.join(OUT, nome), await r.body()); console.log("ok", nome); }
  else console.log("FALHOU", r.status(), nome);
}
await browser.close();
