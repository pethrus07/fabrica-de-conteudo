// Estágio 2 do vídeo: renderiza quadro a quadro no Chromium e entrega ao ffmpeg.
//   node render.mjs video-1                 → vídeo completo (trabalho/video-1/video-1.mp4)
//   node render.mjs video-1 --amostra 3,20  → PNGs dos instantes pedidos, para revisão rápida
// Cada quadro é render(t): determinístico, 1920x1080 real, sem gravar tela e sem queda de quadro.
// O vídeo dura EXATAMENTE a trilha de narração (-t), nunca -shortest — foi o -shortest que
// decepou a fala em silêncio na esteira da Mettria.
import fs from "fs";
import path from "path";
import { spawn } from "child_process";
import { fileURLToPath, pathToFileURL } from "url";
import { chromium } from "playwright";

const AQUI = path.dirname(fileURLToPath(import.meta.url));
const RAIZ = path.join(AQUI, "..");
const id = process.argv[2];
const amostra = process.argv.includes("--amostra") ? process.argv[process.argv.indexOf("--amostra") + 1].split(",").map(Number) : null;
const pasta = path.join(AQUI, "trabalho", id);
const tl = JSON.parse(fs.readFileSync(path.join(pasta, "timeline.json"), "utf8"));
const marcas = JSON.parse(fs.readFileSync(path.join(RAIZ, "trabalho", "marcas.json"), "utf8"));
const dados = JSON.parse(fs.readFileSync(path.join(RAIZ, "dados", "padrao-tex.json"), "utf8"));
const svg = fs.readFileSync(path.join(RAIZ, "trabalho", "svg", "bloco.svg"), "utf8");
const svg2 = fs.readFileSync(path.join(RAIZ, "trabalho", "svg", "bloco-profinet.svg"), "utf8");

const browser = await chromium.launch({ args: ["--allow-file-access-from-files", "--force-color-profile=srgb"] });
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
page.on("pageerror", e => { console.error("ERRO NA PÁGINA:", e.message); process.exit(1); });
await page.goto(pathToFileURL(path.join(AQUI, "cena.html")).href);
await page.evaluate(([a, b, c, d, e]) => init(a, b, c, d, e), [tl, marcas, dados, svg, svg2]);
await page.evaluate(() => document.fonts.ready);
await page.waitForFunction(() => [...document.images].every(i => i.complete && i.naturalWidth > 0));

if (amostra) {
  for (const t of amostra) {
    await page.evaluate(x => render(x), t);
    await page.screenshot({ path: path.join(pasta, `amostra-${String(t).padStart(5, "0")}.png`) });
  }
  console.log(`amostras: ${amostra.join(", ")} s`);
  await browser.close();
  process.exit(0);
}

const fps = tl.fps, N = Math.ceil(tl.duracao * fps);
const saida = path.join(pasta, `${id}.mp4`);
// capítulos do MP4: um por cartão de capítulo (mais a abertura), com o início tirado da linha do tempo
const caps = tl.cenas.filter(c => c.tipo === "capitulo").map(c => ({ t: c.ini, nome: `Parte ${c.parte} · ${c.titulo}` }));
const extra = [];
if (caps.length) {
  const marcos = [{ t: 0, nome: "Abertura" }, ...caps];
  const ms = x => Math.round(x * 1000);
  const meta = [";FFMETADATA1", ...marcos.flatMap((m, i) => ["[CHAPTER]", "TIMEBASE=1/1000", `START=${ms(m.t)}`,
    `END=${ms(i + 1 < marcos.length ? marcos[i + 1].t : tl.duracao)}`, `title=${m.nome}`])].join("\n");
  fs.writeFileSync(path.join(pasta, "capitulos.txt"), meta, "utf8");
  extra.push("-i", path.join(pasta, "capitulos.txt"), "-map_chapters", "2");
}
const ff = spawn("ffmpeg", ["-y", "-v", "error",
  "-f", "image2pipe", "-framerate", String(fps), "-c:v", "mjpeg", "-i", "-",
  "-i", path.join(pasta, "narracao.wav"), ...extra,
  "-map", "0:v", "-map", "1:a", "-t", tl.duracao.toFixed(3),
  "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p", "-profile:v", "high", "-r", String(fps),
  "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart",
  "-metadata", `title=Padrão TEX · ${tl.titulo}`, "-metadata", `artist=${dados.produto.fabricante}`, "-metadata", "comment=Narração sintética",
  saida], { stdio: ["pipe", "inherit", "inherit"] });
const t0 = Date.now();
for (let i = 0; i < N; i++) {
  await page.evaluate(x => render(x), i / fps);
  const buf = await page.screenshot({ type: "jpeg", quality: 95 });
  if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once("drain", r));
  if (i % 300 === 0) process.stdout.write(`\r${id}: quadro ${i}/${N} (${Math.round((Date.now() - t0) / 1000)} s)`);
}
ff.stdin.end();
await new Promise(r => ff.on("close", r));
await browser.close();
console.log(`\n${id}: ${saida} em ${Math.round((Date.now() - t0) / 1000)} s`);
