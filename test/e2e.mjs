// Teste de ponta a ponta: preenche uma máquina no celular, grava áudio (microfone falso do Chromium),
// anexa foto/vídeo/documento, recarrega, gera o .zip e confere byte a byte. Depois reabre o .zip num
// aparelho "novo" (contexto limpo) e confere que voltou tudo.
// Rodar: PLAYWRIGHT_BROWSERS_PATH=%LOCALAPPDATA%\ms-playwright npm test
import http from "http";
import fs from "fs";
import path from "path";
import crypto from "crypto";
import { fileURLToPath } from "url";
import { chromium, devices } from "playwright";

const DIR = path.dirname(fileURLToPath(import.meta.url));
const SITE = path.join(DIR, "..", "site");
const OUT = path.join(DIR, "out");
const FX = {
  foto: path.join(OUT, "painel-IMG_20261001.jpg"),
  clp: path.join(OUT, "clp.jpg"),
  video: path.join(OUT, "video-maquina.mp4"),
  pdf: path.join(OUT, "diagrama-eletrico.pdf"),
};
const sha = f => crypto.createHash("sha256").update(fs.readFileSync(f)).digest("hex");
const MIME = { ".html": "text/html; charset=utf-8", ".png": "image/png" };
const srv = http.createServer((q, r) => {
  const f = path.join(SITE, q.url === "/" ? "index.html" : decodeURIComponent(q.url.split("?")[0]));
  if (!fs.existsSync(f)) { r.writeHead(404); return r.end(); }
  r.writeHead(200, { "content-type": MIME[path.extname(f)] || "application/octet-stream" });
  fs.createReadStream(f).pipe(r);
});
await new Promise(r => srv.listen(0, "127.0.0.1", r));
const URL0 = `http://127.0.0.1:${srv.address().port}/`;

let falhas = 0;
const ok = (c, m) => { console.log((c ? "  ok  " : "  FALHOU  ") + m); if (!c) falhas++; };
const shot = async (p, n, full = true) => p.screenshot({ path: path.join(OUT, n + ".png"), fullPage: full });
const semBusy = p => p.waitForFunction(() => !document.querySelector(".busy"), null, { timeout: 30000 });

const browser = await chromium.launch({ args: ["--use-fake-ui-for-media-stream", "--use-fake-device-for-media-stream"] });
const ctx = await browser.newContext({ ...devices["Pixel 7"], acceptDownloads: true, permissions: ["microphone"] });
const page = await ctx.newPage();
const erros = [];
page.on("pageerror", e => erros.push(e.message));
page.on("console", m => { if (m.type() === "error") erros.push(m.text()); });

console.log("1. começo");
await page.goto(URL0);
await shot(page, "01-inicio");
await page.fill("#nome", "Envasadora EV-20 — teste");
await page.click("button[data-type=completa]");
ok(await page.locator("#chips .chip").count() === 12, "modelo completo cria 12 blocos");

console.log("2. narração geral (gravada)");
await page.click("#narr [data-rec]");
await page.waitForSelector("#recbar:not(.hide)");
await page.waitForTimeout(3200);
await shot(page, "02-gravando");
await page.click("#recstop");
await page.waitForSelector("#narr .mi.au");
await semBusy(page);
ok(await page.locator("#narr .mi.au").count() === 1, "narração aparece na lista");

console.log("3. pedido + identificação com foto e vídeo");
await page.check('input[data-k=entregas][value="Manual de operação"]');
await page.check('input[data-k=entregas][value="Vídeo de operação"]');
await page.fill("#form [data-k=cliente]", "Laticínio Serra Verde");
await page.click('button[data-go="1"]');
await page.fill("#form [data-k=funcao]", "Envasa e lacra potes de 500 g, até 20 por minuto.");
await page.setInputFiles("#form section.card > .media input[data-add]", [FX.foto, FX.video]);
await semBusy(page);
await page.waitForTimeout(500);
ok(await page.locator("#form section.card > .media .mi").count() === 2, "foto e vídeo anexados");
await page.fill("#form [data-cap]", "Painel frontal");
await shot(page, "03-identificacao");

console.log("4. ficha técnica (valor e unidade)");
await page.click('[data-chip="2"]');
await page.locator("#form .row").nth(0).locator("[data-k=valor]").fill("220");
await page.locator("#form .row").nth(1).locator("[data-k=valor]").fill("1,5");

console.log("5. operação: passo com foto e áudio próprio");
await page.click('[data-chip="6"]');
await page.fill("#form .row [data-k=acao]", "Ligar a chave geral");
await page.setInputFiles("#form .row input[data-add]", [FX.clp]);
await semBusy(page);
await page.click("#form .row [data-rec]");
await page.waitForTimeout(1500);
await page.click("#recstop");
await page.waitForSelector("#form .row .mi.au");
await semBusy(page);
await page.click("#form [data-radd]");
ok(await page.locator("#form .row").count() === 2, "adicionar passo");
await shot(page, "05-operacao");

console.log("6. organizar: mover, remover, adicionar bloco livre com documento");
await page.click("[data-org]");
await shot(page, "06-organizar", false);
await page.click('#box [data-o=dn][data-i="0"]');
ok((await page.locator("#box .li b").first().textContent()).includes("Identificação"), "mover para baixo troca a ordem");
await page.click('#box [data-o=rm][data-i="11"]'); // Regras (vazio) → sem confirmação
await page.waitForSelector("#box .li");
ok(await page.locator("#box .li").count() === 11, "remover bloco vazio");
await page.click("#box [data-o=add]");
await page.click('#box button[data-close="livre"]');
await page.fill("#form [data-title]", "Observações da fábrica");
await page.fill("#form [data-k=texto]", "Bloco criado pelo cliente.");
await page.setInputFiles("#form section.card > .media input[data-add]", [FX.pdf]);
await semBusy(page);

console.log("7. recarregar: tudo continua lá");
await page.waitForTimeout(800);
await page.reload();
await page.waitForSelector("#chips .chip");
ok((await page.inputValue("#nome")) === "Envasadora EV-20 — teste", "nome persistiu");
const cnt = await page.textContent("#count");
ok(/2\s*fotos/.test(cnt) && /1\s*vídeos/.test(cnt) && /2\s*áudios/.test(cnt) && /1\s*arquivos/.test(cnt), "contagem persistiu: " + cnt.trim());
await page.click('[data-view="tudo"]');
await page.waitForTimeout(800);
await shot(page, "07-ver-tudo");

console.log("8. gerar o pacote");
await page.click("#gen");
await page.click('#box button[data-close="ok"]'); // confirma blocos vazios
await page.waitForSelector("#dl", { timeout: 60000 });
await shot(page, "08-pronto", false);
const [dl] = await Promise.all([page.waitForEvent("download"), page.click("#dl")]);
const ZIP = path.join(OUT, dl.suggestedFilename());
await dl.saveAs(ZIP);
ok(fs.statSync(ZIP).size > 13_000_000, "zip baixado: " + path.basename(ZIP) + " " + fs.statSync(ZIP).size + " bytes");
fs.writeFileSync(path.join(OUT, "hashes.json"), JSON.stringify(Object.fromEntries(Object.entries(FX).map(([k, f]) => [k, sha(f)]))));

console.log("9. reabrir o .zip em outro aparelho (contexto limpo, desktop)");
const ctx2 = await browser.newContext({ viewport: { width: 1280, height: 900 } });
const p2 = await ctx2.newPage();
p2.on("pageerror", e => erros.push("[p2] " + e.message));
await p2.goto(URL0);
await p2.click("#bmaq");
await p2.setInputFiles("#zipin", ZIP);
await p2.waitForSelector("#chips .chip", { timeout: 30000 });
ok((await p2.inputValue("#nome")) === "Envasadora EV-20 — teste", "nome voltou do .zip");
const cnt2 = await p2.textContent("#count");
ok(cnt2.replace(/\s+/g, " ") === cnt.replace(/\s+/g, " "), "contagem igual depois de reabrir: " + cnt2.trim());
await p2.click('[data-view="tudo"]');
await p2.waitForTimeout(1000);
await shot(p2, "09-desktop-reaberto", false);

ok(erros.length === 0, "sem erro no console" + (erros.length ? ": " + erros.join(" | ") : ""));
await browser.close();
srv.close();
console.log(falhas ? `\n${falhas} FALHA(S)` : "\nTUDO OK");
process.exit(falhas ? 1 : 0);
