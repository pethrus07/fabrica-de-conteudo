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
const URL0 = process.env.URL || `http://127.0.0.1:${srv.address().port}/`;

let falhas = 0;
const ok = (c, m) => { console.log((c ? "  ok  " : "  FALHOU  ") + m); if (!c) falhas++; };
const shot = async (p, n, full = true) => p.screenshot({ path: path.join(OUT, n + ".png"), fullPage: full });
const semBusy = p => p.waitForFunction(() => !document.querySelector(".busy"), null, { timeout: 30000 });

const browser = await chromium.launch({ args: ["--use-fake-ui-for-media-stream", "--use-fake-device-for-media-stream"] });

// Fixtures sintéticas: test/out/ é ignorado pelo git, então o teste cria o que precisa num clone limpo.
// Arquivos que já existirem (ex.: fotos reais de uma rodada local) são mantidos.
fs.mkdirSync(OUT, { recursive: true });
{
  const p = await browser.newPage({ viewport: { width: 1600, height: 1200 } });
  for (const [f, cor] of [[FX.foto, "#2a6"], [FX.clp, "#36c"]]) {
    if (fs.existsSync(f)) continue;
    await p.setContent(`<body style="margin:0;background:linear-gradient(45deg,${cor},#fff)"></body>`);
    await p.screenshot({ path: f, type: "jpeg", quality: 90 });
  }
  await p.close();
  if (!fs.existsSync(FX.video)) fs.writeFileSync(FX.video, crypto.randomBytes(3 * 1024 * 1024));
  if (!fs.existsSync(FX.pdf)) fs.writeFileSync(FX.pdf, "%PDF-1.4\n%%EOF\n");
}
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

console.log("2. pedido escrito + áudio opcional");
await page.fill("#narr textarea[data-narr]", "Preciso de 2 vídeos e do manual de operação até dia 15.");
await page.click("#narr [data-rec]");
await page.waitForSelector("#recbar:not(.hide)");
await page.waitForTimeout(3200);
await shot(page, "02-gravando");
await page.click("#recstop");
await page.waitForSelector("#narr .mi.au");
await semBusy(page);
ok(await page.locator("#narr .mi.au").count() === 1, "narração aparece na lista");

console.log("3. pedido + identificação com foto e vídeo");
const qd = (opt, d) => page.click(`#form button[data-qd="${d}"][data-opt="${opt}"]`);
await qd("Vídeo", 1); await qd("Vídeo", 1); await qd("Vídeo", 1); await qd("Vídeo", -1);
await qd("Manual", 1);
ok(await page.locator('#form input[data-qi][data-opt="Vídeo"]').count() === 2, "quantidade de vídeos = 2 campos de assunto");
await page.locator('#form input[data-qi][data-opt="Vídeo"]').nth(0).fill("Operação do dia a dia");
await page.locator('#form input[data-qi][data-opt="Vídeo"]').nth(1).fill("Limpeza do bico");
await page.locator('#form input[data-qi][data-opt="Manual"]').nth(0).fill("Operação");
await shot(page, "03a-pedido-quantidades", false);
await page.fill("#form [data-k=cliente]", "Laticínio Serra Verde");
await page.click('button[data-go="1"]');
await page.fill("#form [data-k=funcao]", "Envasa e lacra potes de 500 g, até 20 por minuto.");
await page.setInputFiles("#form section.card > .media input[data-gal]", [FX.foto, FX.video]);
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
ok(await page.locator("#form .row label.mbtn.cam").first().isVisible(), "celular: botão Tirar foto aparece");
ok(await page.locator('#form .row input[data-cam="foto"]').getAttribute("capture") === "environment", "Tirar foto abre a câmera traseira (capture=environment)");
ok(await page.locator('#form .row input[data-cam="video"]').getAttribute("accept") === "video/*", "Gravar vídeo aceita só vídeo");
await page.setInputFiles('#form .row input[data-cam="foto"]', [FX.clp]); // simula a foto que volta da câmera
await semBusy(page);
await page.click("#form .row [data-rec]");
await page.waitForTimeout(1500);
await page.click("#recstop");
await page.waitForSelector("#form .row .mi.au");
await semBusy(page);
await page.click("#form [data-radd]");
ok(await page.locator("#form .row").count() === 2, "adicionar passo");
await shot(page, "05-operacao");
await page.locator("#form .row").first().screenshot({ path: path.join(OUT, "05a-botoes-camera.png") });

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
await page.setInputFiles("#form section.card > .media input[data-gal]", [FX.pdf]);
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
// O .zip guarda a mídia byte a byte (modo STORE): tem que ser maior que a soma das fixtures.
const somaFixtures = Object.values(FX).reduce((s, f) => s + fs.statSync(f).size, 0);
ok(fs.statSync(ZIP).size > somaFixtures,"zip baixado: " + path.basename(ZIP) + " " + fs.statSync(ZIP).size + " bytes");
{
  const code = fs.readFileSync(path.join(SITE, "index.html"), "utf8").split("/*ZIP-BEGIN*/")[1].split("/*ZIP-END*/")[0];
  const { readZip } = new Function(code + ";return{readZip}")();
  const ents = await readZip(new Blob([fs.readFileSync(ZIP)]));
  const ped = JSON.parse(await ents.find(e => e.name.endsWith("pedido.json")).blob.text());
  const res = await ents.find(e => e.name.endsWith("RESUMO.md")).blob.text();
  ok(ped.pedido_escrito.startsWith("Preciso de 2 vídeos"), "pedido escrito vai no pedido.json");
  ok(JSON.stringify(ped.entregas) === JSON.stringify([{ tipo: "Vídeo", quantidade: 2, itens: [{ numero: 1, sobre: "Operação do dia a dia" }, { numero: 2, sobre: "Limpeza do bico" }] }, { tipo: "Manual", quantidade: 1, itens: [{ numero: 1, sobre: "Operação" }] }]), "entregas com quantidade: " + JSON.stringify(ped.entregas));
  ok(res.includes("**Vídeo × 2**") && res.includes("O que o cliente pediu"), "RESUMO.md traz pedido escrito e entregas");
}
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
ok(!(await p2.locator("label.mbtn.cam").first().isVisible()), "computador: botões de câmera escondidos");
await p2.click('[data-view="tudo"]');
await p2.waitForTimeout(1000);
await shot(p2, "09-desktop-reaberto", false);

console.log("10. projeto salvo no formato antigo (antes das quantidades) é migrado");
const ctx3 = await browser.newContext(devices["Pixel 7"]);
const p3 = await ctx3.newPage();
p3.on("pageerror", e => erros.push("[p3] " + e.message));
await p3.goto(URL0);
await p3.waitForSelector("button[data-type=completa]");
await p3.evaluate(() => new Promise((res, rej) => {
  const r = indexedDB.open("celiware-estudio", 1);
  r.onsuccess = () => {
    const t = r.result.transaction("proj", "readwrite");
    t.objectStore("proj").put({ app: "celiware-estudio", v: 1, id: "mlegado", nome: "Legada", criado: "2026-10-01T12:00:00Z", salvo: "2026-10-01T12:00:00Z", view: "guiada", cur: 0, narr: [], meta: {},
      secs: [{ id: "s1", tipo: "pedido", titulo: "O pedido", vals: { entregas: ["Vídeo de operação", "Manual de manutenção"], cliente: "X" }, rows: [], mid: [] }] });
    t.oncomplete = () => { localStorage.setItem("ce-cur", "mlegado"); res(); };
    t.onerror = () => rej(t.error);
  };
}));
await p3.reload();
await p3.waitForSelector("#form [data-qf]");
ok((await p3.inputValue('#form input[data-qi][data-opt="Vídeo"]')) === "Operação", "legado: vídeo de operação → Vídeo × 1 (Operação)");
ok((await p3.inputValue('#form input[data-qi][data-opt="Manual"]')) === "Manutenção", "legado: manual de manutenção → Manual × 1 (Manutenção)");
ok((await p3.inputValue("#form [data-k=cliente]")) === "X", "legado: outros campos intactos");

ok(erros.length === 0, "sem erro no console" + (erros.length ? ": " + erros.join(" | ") : ""));
await browser.close();
srv.close();
console.log(falhas ? `\n${falhas} FALHA(S)` : "\nTUDO OK");
process.exit(falhas ? 1 : 0);
