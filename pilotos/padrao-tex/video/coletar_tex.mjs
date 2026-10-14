// Coleta do site da Tex (autorizada pelo cliente em 02/10/2026: "tudo do site deles pode usar para enriquecer").
// O site recusa curl (406), então vai pelo Chromium: salva o HTML, o texto, a captura e as imagens de cada página.
//   node coletar_tex.mjs [url ...]   → ../marca/tex/site/
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { chromium } from "playwright";

const AQUI = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(AQUI, "..", "marca", "tex", "site");
fs.mkdirSync(path.join(OUT, "img"), { recursive: true });
const urls = process.argv.slice(2).length ? process.argv.slice(2) : ["https://tex.com.br/"];

const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 }, locale: "pt-BR",
  userAgent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36" });
const page = await ctx.newPage();
const imagens = new Map();
page.on("response", async r => {
  const t = r.headers()["content-type"] || "";
  if (!/image\//.test(t) || r.status() !== 200) return;
  try { const b = await r.body(); if (b.length > 1500) imagens.set(r.url(), b); } catch {}
});
const links = new Set();
for (const u of urls) {
  const slug = (new URL(u).pathname.replace(/\/+$/, "").replace(/[^\w-]+/g, "_") || "home").replace(/^_/, "");
  const resp = await page.goto(u, { waitUntil: "domcontentloaded", timeout: 60000 });
  // o site navega de novo logo depois de abrir (desafio anti-robô): espera assentar antes de mexer na página
  await page.waitForTimeout(8000);
  await page.waitForLoadState("load").catch(() => {});
  console.log("  url final:", page.url());
  await page.evaluate(async () => { for (let y = 0; y < document.body.scrollHeight; y += 600) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 150)); } });
  await page.waitForTimeout(4000);
  fs.writeFileSync(path.join(OUT, slug + ".html"), await page.content());
  fs.writeFileSync(path.join(OUT, slug + ".txt"), await page.evaluate(() => document.body.innerText));
  await page.screenshot({ path: path.join(OUT, slug + ".png"), fullPage: true });
  for (const h of await page.$$eval("a[href]", as => as.map(a => a.href))) if (h.includes("tex.com.br")) links.add(h.split("#")[0]);
  const imgs = await page.$$eval("img", is => is.map(i => ({ src: i.currentSrc || i.src, alt: i.alt, w: i.naturalWidth, h: i.naturalHeight })));
  fs.writeFileSync(path.join(OUT, slug + ".imagens.json"), JSON.stringify(imgs, null, 1));
  console.log(u, resp && resp.status(), "título:", await page.title(), "imagens:", imgs.length);
}
let n = 0;
for (const [u, b] of imagens) {
  const nome = decodeURIComponent(new URL(u).pathname.split("/").pop()).replace(/[^\w.-]+/g, "_").slice(-80) || `img${n}`;
  fs.writeFileSync(path.join(OUT, "img", nome), b); n++;
}
fs.writeFileSync(path.join(OUT, "links.txt"), [...links].sort().join("\n"));
console.log("imagens salvas:", n, "links internos:", links.size);
await browser.close();
